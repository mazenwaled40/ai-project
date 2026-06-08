from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.post("/", response_model=schemas.CameraOut, status_code=201)
def create_camera(camera: schemas.CameraCreate, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    new_camera = models.Camera(**camera.dict())
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return new_camera


@router.get("/", response_model=list[schemas.CameraOut])
def get_all_cameras(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Camera).all()


@router.get("/{camera_id}", response_model=schemas.CameraOut)
def get_camera(camera_id: int, db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.put("/{camera_id}", response_model=schemas.CameraOut)
def update_camera(camera_id: int, data: schemas.CameraUpdate,
                  db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    for key, value in data.dict(exclude_none=True).items():
        setattr(camera, key, value)
    db.commit()
    db.refresh(camera)
    return camera


@router.delete("/{camera_id}", status_code=204)
def delete_camera(camera_id: int, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    db.delete(camera)
    db.commit()
