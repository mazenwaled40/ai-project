from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routers import users, cameras, incidents, alerts, feedback, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="School Guard API",
    description="AI-assisted school violence detection and incident management system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(cameras.router)
app.include_router(incidents.router)
app.include_router(alerts.router)
app.include_router(feedback.router)
app.include_router(dashboard.router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "School Guard API is running 🚀"}
