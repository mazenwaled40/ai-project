from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=schemas.FeedbackOut, status_code=201)
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    # Check incident exists
    incident = db.query(models.Incident).filter(
        models.Incident.incident_id == feedback.incident_id
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Update incident status based on decision
    if feedback.decision == "confirmed":
        incident.status = "confirmed"
    elif feedback.decision == "false_alarm":
        incident.status = "false_alarm"

    new_feedback = models.Feedback(**feedback.dict())
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


@router.get("/", response_model=list[schemas.FeedbackOut])
def get_all_feedback(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Feedback).order_by(models.Feedback.feedback_time.desc()).all()


@router.get("/incident/{incident_id}", response_model=list[schemas.FeedbackOut])
def get_feedback_by_incident(incident_id: int, db: Session = Depends(get_db),
                              current_user=Depends(get_current_user)):
    return db.query(models.Feedback).filter(
        models.Feedback.incident_id == incident_id
    ).all()
