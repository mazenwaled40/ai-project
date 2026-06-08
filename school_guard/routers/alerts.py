from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/", response_model=schemas.AlertOut, status_code=201)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db),
                 current_user=Depends(get_current_user)):
    new_alert = models.Alert(**alert.dict())
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


@router.get("/", response_model=list[schemas.AlertOut])
def get_all_alerts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Alert).order_by(models.Alert.sent_time.desc()).all()


@router.get("/{alert_id}", response_model=schemas.AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db),
              current_user=Depends(get_current_user)):
    alert = db.query(models.Alert).filter(models.Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}", response_model=schemas.AlertOut)
def update_alert_status(alert_id: int, data: schemas.AlertUpdate,
                        db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    alert = db.query(models.Alert).filter(models.Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for key, value in data.dict(exclude_none=True).items():
        setattr(alert, key, value)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/user/{user_id}", response_model=list[schemas.AlertOut])
def get_alerts_by_user(user_id: int, db: Session = Depends(get_db),
                       current_user=Depends(get_current_user)):
    return db.query(models.Alert).filter(
        models.Alert.user_id == user_id
    ).order_by(models.Alert.sent_time.desc()).all()
