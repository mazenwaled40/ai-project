import os
import time
import uuid
import asyncio
import shutil
import json
import base64
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import cv2
import numpy as np
import tensorflow as tf
from collections import deque
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── Constants ────────────────────────────────────────────────────────────────
MAX_FRAMES = 24
IMG_SIZE = 224
FEATURE_DIM = 1280

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
MODEL_DIR  = Path("models")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

# ─── Global State ─────────────────────────────────────────────────────────────
feature_extractor: Optional[tf.keras.Model] = None
loaded_models: dict[str, tf.keras.Model] = {}
jobs: dict[str, dict] = {}  # job_id -> status dict


# ─── Lifespan: load MobileNetV2 once at startup ───────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global feature_extractor
    print("[STARTUP] Loading MobileNetV2 feature extractor...")
    feature_extractor = MobileNetV2(
        include_top=False,
        weights="imagenet",
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        pooling="avg",
    )
    feature_extractor.trainable = False
    print("[STARTUP] MobileNetV2 ready.")
    yield
    print("[SHUTDOWN] Cleaning up resources.")


from tensorflow.keras.applications import MobileNetV2

app = FastAPI(
    title="🔍 Violence Detection API",
    description=(
        "Real-time violence detection in video files using MobileNetV2 feature "
        "extraction + a custom trained Keras classifier. Upload a video and a model "
        "to get an annotated output video with per-frame violence scores."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────
class JobStatus(BaseModel):
    job_id: str
    status: str           # "queued" | "processing" | "done" | "failed"
    progress_pct: float
    total_frames: int
    processed_frames: int
    elapsed_sec: float
    output_file: Optional[str] = None
    error: Optional[str] = None
    summary: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    feature_extractor_loaded: bool
    loaded_models: list[str]
    active_jobs: int


# ─── Core Vision Logic ────────────────────────────────────────────────────────
def extract_features(frames: list) -> Optional[np.ndarray]:
    if not frames:
        return None
    frames_array = np.array(frames, dtype=np.float32)
    frames_array = tf.keras.applications.mobilenet_v2.preprocess_input(frames_array)
    return feature_extractor.predict(frames_array, verbose=0)


def pad_features(features: np.ndarray, max_frames: int = MAX_FRAMES) -> np.ndarray:
    current_frames = features.shape[0]
    if current_frames >= max_frames:
        return features[:max_frames]
    padding = np.zeros((max_frames - current_frames, features.shape[1]), dtype=np.float32)
    return np.concatenate([features, padding], axis=0)


def classify_score(score: float) -> tuple[str, tuple]:
    if score > 0.70:
        return "VIOLENCE", (0, 0, 255)
    elif score > 0.40:
        return "SUSPICIOUS", (0, 255, 255)
    return "SAFE", (0, 255, 0)


def draw_overlay(frame: np.ndarray, label: str, score: float, frame_idx: int) -> np.ndarray:
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (390, 145), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.45, frame, 0.55, 0)
    _, color = classify_score(score)
    cv2.putText(frame, f"Status: {label}",       (20, 45),  cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
    cv2.putText(frame, f"Confidence: {score:.2f}", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    cv2.putText(frame, f"Frame: {frame_idx}",    (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return frame


# ─── Background Processing Task ───────────────────────────────────────────────
def process_video_job(
    job_id: str,
    input_path: str,
    model_path: str,
    output_path: str,
    window_stride: int = 8,
    smoothing_size: int = 5,
):
    job = jobs[job_id]
    job["status"] = "processing"
    job["start_time"] = time.time()

    try:
        # Load or reuse model
        if model_path not in loaded_models:
            loaded_models[model_path] = tf.keras.models.load_model(model_path)
        model = loaded_models[model_path]

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise RuntimeError("Could not open input video")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        job["total_frames"] = total

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if not writer.isOpened():
            raise RuntimeError("Could not create output video writer")

        frame_buffer  = deque(maxlen=MAX_FRAMES)
        score_buffer  = deque(maxlen=smoothing_size)
        frame_idx     = 0
        current_score = 0.0
        current_label = "WAITING"

        # Stats for summary
        label_counts = {"VIOLENCE": 0, "SUSPICIOUS": 0, "SAFE": 0, "WAITING": 0}

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resized   = cv2.resize(frame_rgb, (IMG_SIZE, IMG_SIZE))
            frame_buffer.append(resized)

            if len(frame_buffer) == MAX_FRAMES and frame_idx % window_stride == 0:
                features = extract_features(list(frame_buffer))
                features = pad_features(features, MAX_FRAMES)
                x = np.expand_dims(features, axis=0)
                pred = float(model.predict(x, verbose=0)[0][0])
                score_buffer.append(pred)
                current_score = float(sum(score_buffer) / len(score_buffer))
                current_label, _ = classify_score(current_score)

            label_counts[current_label] = label_counts.get(current_label, 0) + 1

            annotated = draw_overlay(frame.copy(), current_label, current_score, frame_idx)
            writer.write(annotated)

            job["processed_frames"] = frame_idx
            job["progress_pct"] = round((frame_idx / total * 100) if total > 0 else 0, 2)
            job["elapsed_sec"] = round(time.time() - job["start_time"], 2)

        cap.release()
        writer.release()

        # Build summary
        dominant = max(label_counts, key=label_counts.get)
        job["summary"] = {
            "total_frames": frame_idx,
            "label_distribution": label_counts,
            "dominant_label": dominant,
            "output_file": os.path.basename(output_path),
        }
        job["output_file"] = output_path
        job["status"] = "done"
        job["progress_pct"] = 100.0

    except Exception as exc:
        job["status"] = "failed"
        job["error"] = str(exc)
    finally:
        job["elapsed_sec"] = round(time.time() - job.get("start_time", time.time()), 2)


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"message": "Violence Detection API is running. Visit /docs for the interactive UI."}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    return HealthResponse(
        status="ok",
        feature_extractor_loaded=feature_extractor is not None,
        loaded_models=list(loaded_models.keys()),
        active_jobs=sum(1 for j in jobs.values() if j["status"] == "processing"),
    )


@app.post("/upload-model", tags=["Models"])
async def upload_model(file: UploadFile = File(...)):
    """Upload a .keras or .h5 Keras model to the server."""
    if not (file.filename.endswith(".keras") or file.filename.endswith(".h5")):
        raise HTTPException(400, "Only .keras or .h5 model files are accepted.")

    dest = MODEL_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"message": f"Model '{file.filename}' uploaded successfully.", "path": str(dest)}


@app.get("/models", tags=["Models"])
def list_models():
    """List all available model files on the server."""
    models = [p.name for p in MODEL_DIR.iterdir() if p.suffix in (".keras", ".h5")]
    return {"models": models}


@app.post("/detect", tags=["Detection"])
async def detect_violence(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(..., description="Input video file (mp4, avi, etc.)"),
    model_name: str = Form(..., description="Name of the model file in the models/ folder, e.g. 'violence_detector.keras'"),
    window_stride: int = Form(8, description="Process every N-th frame window"),
    smoothing_size: int = Form(5, description="Temporal smoothing buffer size"),
):
    """
    Submit a video for violence detection.
    Returns a **job_id** you can poll via `/jobs/{job_id}`.
    """
    model_path = MODEL_DIR / model_name
    if not model_path.exists():
        raise HTTPException(404, f"Model '{model_name}' not found. Upload it first via /upload-model.")

    # Save uploaded video
    job_id = str(uuid.uuid4())
    input_path  = str(UPLOAD_DIR / f"{job_id}_{video.filename}")
    output_path = str(OUTPUT_DIR / f"{job_id}_result.mp4")

    with open(input_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    # Register job
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress_pct": 0.0,
        "total_frames": 0,
        "processed_frames": 0,
        "elapsed_sec": 0.0,
        "output_file": None,
        "error": None,
        "summary": None,
        "start_time": time.time(),
    }

    background_tasks.add_task(
        process_video_job,
        job_id, input_path, str(model_path), output_path,
        window_stride, smoothing_size,
    )

    return {"job_id": job_id, "message": "Job queued. Poll /jobs/{job_id} for status."}


@app.get("/jobs/{job_id}", response_model=JobStatus, tags=["Detection"])
def get_job_status(job_id: str):
    """Poll the status and progress of a detection job."""
    if job_id not in jobs:
        raise HTTPException(404, f"Job '{job_id}' not found.")
    j = jobs[job_id]
    return JobStatus(
        job_id=j["job_id"],
        status=j["status"],
        progress_pct=j["progress_pct"],
        total_frames=j["total_frames"],
        processed_frames=j["processed_frames"],
        elapsed_sec=j["elapsed_sec"],
        output_file=j.get("output_file"),
        error=j.get("error"),
        summary=j.get("summary"),
    )


@app.get("/jobs", tags=["Detection"])
def list_jobs():
    """List all submitted jobs and their statuses."""
    return {
        "jobs": [
            {"job_id": j["job_id"], "status": j["status"], "progress_pct": j["progress_pct"]}
            for j in jobs.values()
        ]
    }


@app.get("/download/{job_id}", tags=["Detection"])
def download_result(job_id: str):
    """Download the annotated output video for a completed job."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found.")
    job = jobs[job_id]
    if job["status"] != "done":
        raise HTTPException(400, f"Job is not done yet. Current status: {job['status']}")
    output_path = job["output_file"]
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(500, "Output file not found on server.")
    return FileResponse(output_path, media_type="video/mp4", filename=f"result_{job_id}.mp4")


@app.delete("/jobs/{job_id}", tags=["Detection"])
def delete_job(job_id: str):
    """Delete a job and its associated files from the server."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found.")
    job = jobs.pop(job_id)

    # Clean up files
    for path in [job.get("output_file")]:
        if path and os.path.exists(path):
            os.remove(path)

    # Also clean up input upload
    for f in UPLOAD_DIR.iterdir():
        if f.name.startswith(job_id):
            f.unlink(missing_ok=True)

    return {"message": f"Job '{job_id}' and its files have been deleted."}


# ─── Connection Manager for WebSockets ─────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # ignore disconnected or broken channels
                pass

manager = ConnectionManager()


@app.websocket("/ws/detect/{client_id}")
async def websocket_detect_endpoint(
    websocket: WebSocket,
    client_id: str,
    model_name: str = Query("violence_detector.keras", description="Name of the model file"),
    window_stride: int = Query(8, description="Process every N-th frame window"),
    smoothing_size: int = Query(5, description="Temporal smoothing buffer size"),
):
    await manager.connect(websocket)
    
    model = None
    if model_name != "mock":
        model_path = MODEL_DIR / model_name
        model_path_str = str(model_path)
        
        # Check if model exists
        if not model_path.exists():
            await websocket.send_json({"error": f"Model '{model_name}' not found. Upload it first."})
            manager.disconnect(websocket)
            await websocket.close(code=1008)
            return

        if model_path_str not in loaded_models:
            try:
                loaded_models[model_path_str] = tf.keras.models.load_model(model_path_str)
            except Exception as exc:
                await websocket.send_json({"error": f"Failed to load model: {str(exc)}"})
                manager.disconnect(websocket)
                await websocket.close(code=1011)
                return
        model = loaded_models[model_path_str]
    
    frame_buffer = deque(maxlen=MAX_FRAMES)
    score_buffer = deque(maxlen=smoothing_size)
    frame_idx = 0
    current_score = 0.0
    current_label = "WAITING"

    await manager.broadcast({
        "event": "client_connected",
        "client_id": client_id,
        "message": f"Client #{client_id} connected to AI WebSocket."
    })

    try:
        while True:
            # We receive data from the websocket (can be binary or text/json)
            message = await websocket.receive()
            
            # Check for close event
            if message.get("type") == "websocket.disconnect":
                break
                
            frame = None
            if "bytes" in message:
                frame_bytes = message["bytes"]
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif "text" in message:
                text_data = message["text"]
                # Try JSON
                try:
                    data_json = json.loads(text_data)
                    base64_str = data_json.get("frame") or data_json.get("image")
                    if not base64_str:
                        base64_str = text_data
                except Exception:
                    base64_str = text_data
                
                # Strip prefix if it's a data URL
                if "," in base64_str:
                    base64_str = base64_str.split(",")[1]
                
                try:
                    frame_bytes = base64.b64decode(base64_str)
                    nparr = np.frombuffer(frame_bytes, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception as e:
                    await websocket.send_json({"error": f"Invalid image encoding: {str(e)}"})
                    continue
            
            if frame is None:
                continue

            frame_idx += 1
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(frame_rgb, (IMG_SIZE, IMG_SIZE))
            frame_buffer.append(resized)

            prediction_made = False
            
            if model_name == "mock":
                if frame_idx % window_stride == 0:
                    import math
                    import random
                    # Oscillating score with some randomness to trigger alerts/updates
                    pred = 0.5 + 0.4 * math.sin(frame_idx / 20.0)
                    pred = max(0.0, min(1.0, pred + random.uniform(-0.1, 0.1)))
                    score_buffer.append(pred)
                    current_score = float(sum(score_buffer) / len(score_buffer))
                    current_label, _ = classify_score(current_score)
                    prediction_made = True
            else:
                # Check if we should predict using the TensorFlow model
                if len(frame_buffer) == MAX_FRAMES and frame_idx % window_stride == 0:
                    features = extract_features(list(frame_buffer))
                    if features is not None:
                        features = pad_features(features, MAX_FRAMES)
                        x = np.expand_dims(features, axis=0)
                        pred = float(model.predict(x, verbose=0)[0][0])
                        score_buffer.append(pred)
                        current_score = float(sum(score_buffer) / len(score_buffer))
                        current_label, _ = classify_score(current_score)
                        prediction_made = True

            event_data = {
                "event": "frame_processed",
                "client_id": client_id,
                "frame_idx": frame_idx,
                "prediction_made": prediction_made,
                "label": current_label,
                "score": current_score
            }

            # Send result back to the sender
            await manager.send_personal_message(event_data, websocket)
            
            # Broadcast alerts on detection
            if prediction_made and current_label in ["VIOLENCE", "SUSPICIOUS"]:
                alert_data = {
                    "event": "alert",
                    "client_id": client_id,
                    "frame_idx": frame_idx,
                    "label": current_label,
                    "score": current_score,
                    "message": f"Alert! {current_label} detected by Client #{client_id} (Score: {current_score:.2f})"
                }
                await manager.broadcast(alert_data)

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print(f"WebSocket error for client {client_id}: {str(exc)}")
    finally:
        manager.disconnect(websocket)
        await manager.broadcast({
            "event": "client_disconnected",
            "client_id": client_id,
            "message": f"Client #{client_id} disconnected."
        })


@app.get("/demo", response_class=HTMLResponse, tags=["Detection"])
def websocket_demo():
    """Serves a premium dark-themed web client for testing real-time webcam frame streaming over WebSocket."""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Violence Detection AI - Real-time WebSocket Demo</title>
    <!-- Outfit Font -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --primary: #6366f1;
            --primary-glow: rgba(99, 102, 241, 0.15);
            --safe: #10b981;
            --safe-glow: rgba(16, 185, 129, 0.25);
            --suspicious: #f59e0b;
            --suspicious-glow: rgba(245, 158, 11, 0.25);
            --violence: #ef4444;
            --violence-glow: rgba(239, 68, 68, 0.35);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        header {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 1.5rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-icon {
            font-size: 2rem;
            animation: pulse-glow 2s infinite ease-in-out;
        }

        header h1 {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(to right, #818cf8, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            display: grid;
            grid-template-columns: 350px 1fr;
            gap: 2rem;
            flex: 1;
        }

        .panel {
            background-color: var(--bg-card);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }

        .panel-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-main);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 0.75rem;
            margin-bottom: 0.5rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        label {
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-muted);
        }

        input, select {
            background-color: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: all 0.2s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 2px var(--primary-glow);
        }

        button {
            cursor: pointer;
            padding: 0.85rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s;
            border: none;
        }

        .btn-primary {
            background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        }

        .btn-primary:hover {
            opacity: 0.95;
            transform: translateY(-1px);
        }

        .btn-danger {
            background: #ef4444;
            color: white;
        }

        .btn-danger:hover {
            opacity: 0.95;
            transform: translateY(-1px);
        }

        .main-workspace {
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }

        .video-grid {
            display: grid;
            grid-template-columns: 1fr 320px;
            gap: 2rem;
        }

        .video-card {
            background-color: var(--bg-card);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
            aspect-ratio: 16/9;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }

        #webcam {
            width: 100%;
            height: 100%;
            object-fit: cover;
            background-color: #000;
            transform: scaleX(-1); /* mirror preview */
        }

        /* Overlay indicator */
        .status-overlay {
            position: absolute;
            top: 1.5rem;
            left: 1.5rem;
            z-index: 10;
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }

        .status-safe {
            background-color: rgba(16, 185, 129, 0.2);
            border: 1px solid var(--safe);
            color: var(--safe);
        }

        .status-safe .status-dot {
            background-color: var(--safe);
            box-shadow: 0 0 8px var(--safe);
        }

        .status-suspicious {
            background-color: rgba(245, 158, 11, 0.2);
            border: 1px solid var(--suspicious);
            color: var(--suspicious);
        }

        .status-suspicious .status-dot {
            background-color: var(--suspicious);
            box-shadow: 0 0 8px var(--suspicious);
        }

        .status-violence {
            background-color: rgba(239, 68, 68, 0.2);
            border: 1px solid var(--violence);
            color: var(--violence);
            animation: pulse-danger 1s infinite alternate;
        }

        .status-violence .status-dot {
            background-color: var(--violence);
            box-shadow: 0 0 8px var(--violence);
        }

        .metrics-card {
            background-color: var(--bg-card);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }

        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0.5rem 0;
            transition: color 0.3s;
        }

        .metric-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .progress-bar-container {
            width: 100%;
            height: 10px;
            background-color: #0f172a;
            border-radius: 9999px;
            overflow: hidden;
            margin-top: 0.5rem;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            border-radius: 9999px;
            transition: width 0.2s, background-color 0.3s;
        }

        /* Logger / Terminal */
        .log-section {
            background-color: #020617;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.8);
            height: 300px;
        }

        .log-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .log-header h3 {
            font-size: 0.95rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }

        .log-clear {
            font-size: 0.75rem;
            color: var(--text-muted);
            cursor: pointer;
            text-decoration: underline;
        }

        .log-clear:hover {
            color: white;
        }

        .log-console {
            flex: 1;
            overflow-y: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
            padding-right: 0.5rem;
        }

        .log-row {
            padding: 0.2rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.02);
            line-height: 1.4;
        }

        .log-time {
            color: #6366f1;
            margin-right: 0.5rem;
        }

        .log-tag {
            padding: 0.1rem 0.3rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-right: 0.5rem;
            text-transform: uppercase;
        }

        .tag-info { background: rgba(99, 102, 241, 0.2); color: #818cf8; }
        .tag-safe { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .tag-suspicious { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
        .tag-violence { background: rgba(239, 68, 68, 0.2); color: #f87171; animation: flash-text 0.5s infinite alternate; }

        .hidden-canvas {
            display: none;
        }

        /* Animations */
        @keyframes pulse-glow {
            0%, 100% { transform: scale(1); filter: drop-shadow(0 0 2px var(--primary-glow)); }
            50% { transform: scale(1.05); filter: drop-shadow(0 0 10px var(--primary)); }
        }

        @keyframes pulse-danger {
            0% { box-shadow: 0 0 4px var(--violence-glow); }
            100% { box-shadow: 0 0 15px var(--violence); }
        }

        @keyframes flash-text {
            0% { opacity: 0.6; }
            100% { opacity: 1; }
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.01);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.2);
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-container">
            <span class="logo-icon">🔍</span>
            <h1>Violence Detection AI - WebSockets Client</h1>
        </div>
        <div id="connectionStatus" class="status-overlay status-suspicious">
            <span class="status-dot"></span>
            <span id="statusText">Disconnected</span>
        </div>
    </header>

    <div class="container">
        <!-- Controls Panel -->
        <div class="panel">
            <div class="panel-title">WebSocket Config</div>
            
            <div class="form-group">
                <label for="clientId">Client ID (Camera/Station)</label>
                <input type="text" id="clientId" value="CAM_01">
            </div>

            <div class="form-group">
                <label for="modelName">Keras Model Name</label>
                <input type="text" id="modelName" value="mock" placeholder="e.g. violence_detector.keras">
                <small style="color: var(--text-muted); font-size: 0.75rem;">Use <strong>mock</strong> to test streaming & alerting without model upload.</small>
            </div>

            <div class="form-group">
                <label for="windowStride">Window Stride</label>
                <select id="windowStride">
                    <option value="4">4 frames</option>
                    <option value="8" selected>8 frames</option>
                    <option value="12">12 frames</option>
                    <option value="24">24 frames</option>
                </select>
            </div>

            <div class="form-group">
                <label for="smoothingSize">Temporal Smoothing Size</label>
                <select id="smoothingSize">
                    <option value="3">3 frames</option>
                    <option value="5" selected>5 frames</option>
                    <option value="10">10 frames</option>
                </select>
            </div>

            <div class="form-group" style="flex-direction: row; gap: 0.5rem; align-items: center; margin: 0.5rem 0;">
                <input type="checkbox" id="audioAlert" checked style="width: 16px; height: 16px; cursor: pointer;">
                <label for="audioAlert" style="cursor: pointer; user-select: none;">Play audio alert on Violence</label>
            </div>

            <button id="btnConnect" class="btn-primary" onclick="toggleConnection()">Connect Stream</button>
        </div>

        <!-- Workspace -->
        <div class="main-workspace">
            <div class="video-grid">
                <!-- Video Stream Preview -->
                <div class="video-card">
                    <video id="webcam" autoplay playsinline muted></video>
                    <!-- Floating State Overlay -->
                    <div id="aiOverlay" class="status-overlay status-safe" style="display: none;">
                        <span class="status-dot"></span>
                        <span id="aiLabel">WAITING</span>
                    </div>
                </div>

                <!-- Metrics Dashboard -->
                <div class="metrics-card">
                    <div>
                        <div class="metric-label">Violence Confidence</div>
                        <div id="confidenceVal" class="metric-value">0.00</div>
                        <div class="progress-bar-container">
                            <div id="confidenceBar" class="progress-bar" style="width: 0%; background-color: var(--safe);"></div>
                        </div>
                    </div>

                    <div style="margin-top: 1.5rem; display: flex; flex-direction: column; gap: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                            <span style="color: var(--text-muted);">Frames Sent:</span>
                            <span id="statFrames">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                            <span style="color: var(--text-muted);">Processing FPS:</span>
                            <span id="statFps">0</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                            <span style="color: var(--text-muted);">Network Status:</span>
                            <span id="statLatency">Offline</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Terminal / Event Log -->
            <div class="log-section">
                <div class="log-header">
                    <h3>Live Event Logs & Alerts</h3>
                    <span class="log-clear" onclick="clearLogs()">Clear Console</span>
                </div>
                <div id="logConsole" class="log-console">
                    <div class="log-row"><span class="log-time">[System]</span> Initialized. Ready to connect.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Hidden Canvas to capture and resize frames -->
    <canvas id="hiddenCanvas" class="hidden-canvas" width="224" height="224"></canvas>

    <script>
        var ws = null;
        var stream = null;
        var sendInterval = null;
        var frameCount = 0;
        var lastFpsTime = Date.now();
        var fps = 0;

        // Audio synthesizer for alert
        var audioCtx = null;
        function playChime() {
            if (!document.getElementById("audioAlert").checked) return;
            try {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                if (audioCtx.state === 'suspended') audioCtx.resume();
                
                var osc = audioCtx.createOscillator();
                var gain = audioCtx.createGain();
                
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                
                osc.type = "sine";
                osc.frequency.setValueAtTime(880, audioCtx.currentTime); // A5 note
                osc.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.3); // A4 note
                
                gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
                
                osc.start();
                osc.stop(audioCtx.currentTime + 0.4);
            } catch (err) {
                console.error("Audio error", err);
            }
        }

        function appendLog(timeStr, tag, message, typeClass) {
            var console = document.getElementById("logConsole");
            var row = document.createElement("div");
            row.className = "log-row";
            
            var timeSpan = document.createElement("span");
            timeSpan.className = "log-time";
            timeSpan.textContent = `[${timeStr}]`;
            
            var tagSpan = document.createElement("span");
            tagSpan.className = `log-tag ${typeClass}`;
            tagSpan.textContent = tag;
            
            var textSpan = document.createElement("span");
            textSpan.textContent = message;
            
            row.appendChild(timeSpan);
            row.appendChild(tagSpan);
            row.appendChild(textSpan);
            console.appendChild(row);
            console.scrollTop = console.scrollHeight;
        }

        function clearLogs() {
            document.getElementById("logConsole").innerHTML = "";
        }

        async function startCamera() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 640, height: 480, frameRate: { ideal: 15 } }
                });
                var video = document.getElementById("webcam");
                video.srcObject = stream;
            } catch (err) {
                appendLog(new Date().toLocaleTimeString(), "ERROR", "Could not start camera: " + err.message, "tag-violence");
                throw err;
            }
        }

        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                stream = null;
            }
            var video = document.getElementById("webcam");
            video.srcObject = null;
        }

        function toggleConnection() {
            var btn = document.getElementById("btnConnect");
            if (ws && ws.readyState === WebSocket.OPEN) {
                disconnect();
            } else {
                connect();
            }
        }

        async function connect() {
            var clientId = document.getElementById("clientId").value;
            var modelName = document.getElementById("modelName").value;
            var stride = document.getElementById("windowStride").value;
            var smoothing = document.getElementById("smoothingSize").value;
            
            appendLog(new Date().toLocaleTimeString(), "SYSTEM", "Requesting camera stream...", "tag-info");
            try {
                await startCamera();
            } catch (err) {
                return;
            }

            var loc = window.location;
            var wsProtocol = loc.protocol === "https:" ? "wss:" : "ws:";
            var wsUrl = `${wsProtocol}//${loc.host}/ws/detect/${clientId}?model_name=${modelName}&window_stride=${stride}&smoothing_size=${smoothing}`;
            
            appendLog(new Date().toLocaleTimeString(), "SOCKET", `Connecting to WebSocket: ${wsUrl}`, "tag-info");
            ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                document.getElementById("connectionStatus").className = "status-overlay status-safe";
                document.getElementById("statusText").textContent = "Connected";
                document.getElementById("aiOverlay").style.display = "flex";
                document.getElementById("btnConnect").textContent = "Disconnect Stream";
                document.getElementById("btnConnect").className = "btn-danger";
                document.getElementById("statLatency").textContent = "Active";
                appendLog(new Date().toLocaleTimeString(), "SOCKET", "Connection established. Streaming started.", "tag-safe");
                
                // Start streaming frames
                startFrameStreaming();
            };

            ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                var timeStr = new Date().toLocaleTimeString();
                
                if (data.error) {
                    appendLog(timeStr, "ERROR", data.error, "tag-violence");
                    disconnect();
                    return;
                }

                if (data.event === "frame_processed") {
                    var score = data.score;
                    var label = data.label;
                    
                    // Update Confidence Value and bar
                    document.getElementById("confidenceVal").textContent = score.toFixed(4);
                    var bar = document.getElementById("confidenceBar");
                    bar.style.width = (score * 100) + "%";

                    // Update floating label on video
                    var aiOverlay = document.getElementById("aiOverlay");
                    var labelEl = document.getElementById("aiLabel");
                    labelEl.textContent = label;

                    if (label === "SAFE") {
                        aiOverlay.className = "status-overlay status-safe";
                        bar.style.backgroundColor = "var(--safe)";
                    } else if (label === "SUSPICIOUS") {
                        aiOverlay.className = "status-overlay status-suspicious";
                        bar.style.backgroundColor = "var(--suspicious)";
                        appendLog(timeStr, "WARNING", `Suspicious activity detected! Score: ${score.toFixed(3)}`, "tag-suspicious");
                    } else if (label === "VIOLENCE") {
                        aiOverlay.className = "status-overlay status-violence";
                        bar.style.backgroundColor = "var(--violence)";
                        appendLog(timeStr, "ALERT", `VIOLENCE DETECTED! (Frame #${data.frame_idx}, Score: ${score.toFixed(3)})`, "tag-violence");
                        playChime();
                    }
                } else if (data.event === "alert") {
                    appendLog(timeStr, "BROADCAST ALERT", data.message, "tag-violence");
                    playChime();
                } else if (data.event === "client_connected") {
                    appendLog(timeStr, "BROADCAST INFO", data.message, "tag-info");
                } else if (data.event === "client_disconnected") {
                    appendLog(timeStr, "BROADCAST INFO", data.message, "tag-info");
                }
            };

            ws.onclose = function() {
                appendLog(new Date().toLocaleTimeString(), "SOCKET", "WebSocket connection closed.", "tag-info");
                disconnect();
            };

            ws.onerror = function(err) {
                appendLog(new Date().toLocaleTimeString(), "ERROR", "WebSocket error occurred.", "tag-violence");
                disconnect();
            };
        }

        function startFrameStreaming() {
            var video = document.getElementById("webcam");
            var canvas = document.getElementById("hiddenCanvas");
            var ctx = canvas.getContext("2d");
            
            // Stream frames at ~12 fps (every 83ms) to keep processing load low and steady
            sendInterval = setInterval(function() {
                if (ws && ws.readyState === WebSocket.OPEN && video.readyState === video.HAVE_ENOUGH_DATA) {
                    // Draw webcam frame onto 224x224 canvas
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    // Convert canvas content to blob and send binary data
                    canvas.toBlob(function(blob) {
                        if (ws && ws.readyState === WebSocket.OPEN && blob) {
                            ws.send(blob);
                            frameCount++;
                            document.getElementById("statFrames").textContent = frameCount;
                            
                            // Calculate FPS
                            var now = Date.now();
                            if (now - lastFpsTime >= 1000) {
                                fps = Math.round((frameCount - parseInt(document.getElementById("statFrames").dataset.prevCount || 0)) * 1000 / (now - lastFpsTime));
                                document.getElementById("statFps").textContent = fps;
                                document.getElementById("statFrames").dataset.prevCount = frameCount;
                                lastFpsTime = now;
                            }
                        }
                    }, "image/jpeg", 0.75); // Send compressed JPEG for low network latency
                }
            }, 83);
            document.getElementById("statFrames").dataset.prevCount = "0";
        }

        function disconnect() {
            if (sendInterval) {
                clearInterval(sendInterval);
                sendInterval = null;
            }
            if (ws) {
                ws.close();
                ws = null;
            }
            stopCamera();

            document.getElementById("connectionStatus").className = "status-overlay status-suspicious";
            document.getElementById("statusText").textContent = "Disconnected";
            document.getElementById("aiOverlay").style.display = "none";
            document.getElementById("btnConnect").textContent = "Connect Stream";
            document.getElementById("btnConnect").className = "btn-primary";
            document.getElementById("confidenceVal").textContent = "0.00";
            document.getElementById("confidenceBar").style.width = "0%";
            document.getElementById("statLatency").textContent = "Offline";
            document.getElementById("statFps").textContent = "0";
        }
    </script>
</body>
</html>'''
    return HTMLResponse(html_content)


# =============================================================
# NEW ENDPOINTS (Dashboard & Students Management)
# =============================================================

@app.get("/dashboard/stats", tags=["Dashboard & Students Management"])
def get_dashboard_stats():
    return {
        "total_students": 150,
        "total_incidents": 32,
        "system_status": "Active"
    }

@app.get("/students/disruptive", tags=["Dashboard & Students Management"])
def get_top_disruptive_students(limit: int = 5):
    return [
        {"id": 1, "name": "Mazen Waled", "incident_count": 6},
        {"id": 2, "name": "Ahmed Ali", "incident_count": 4}
    ]

@app.get("/students", tags=["Dashboard & Students Management"])
def get_all_students():
    return [
        {"id": 1, "name": "Mazen Waled", "grade": "Grade 11"},
        {"id": 2, "name": "Ahmed Ali", "grade": "Grade 10"}
    ]

@app.get("/students/{student_id}", tags=["Dashboard & Students Management"])
def get_student_by_id(student_id: int):
    return {
        "student_info": {
            "id": student_id,
            "name": "Mazen Waled" if student_id == 1 else "Student X",
            "grade": "Grade 11"
        },
        "incidents_history": [
            {"id": 101, "title": "Classroom Disruption", "date": "2026-05-31"}
        ]
    }
