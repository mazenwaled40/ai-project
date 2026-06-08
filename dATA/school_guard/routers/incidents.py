from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("/", response_model=schemas.IncidentOut, status_code=201)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    camera = db.query(models.Camera).filter(models.Camera.camera_id == incident.camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    new_incident = models.Incident(**incident.dict())
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident


@router.get("/", response_model=list[schemas.IncidentOut])
def get_all_incidents(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Incident).order_by(models.Incident.timestamp.desc()).all()


@router.get("/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    incident = db.query(models.Incident).filter(models.Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}", response_model=schemas.IncidentOut)
def update_incident(incident_id: int, data: schemas.IncidentUpdate,
                    db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    incident = db.query(models.Incident).filter(models.Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    for key, value in data.dict(exclude_none=True).items():
        setattr(incident, key, value)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/camera/{camera_id}", response_model=list[schemas.IncidentOut])
def get_incidents_by_camera(camera_id: int, db: Session = Depends(get_db),
                             current_user=Depends(get_current_user)):
    return db.query(models.Incident).filter(
        models.Incident.camera_id == camera_id
    ).order_by(models.Incident.timestamp.desc()).all()
