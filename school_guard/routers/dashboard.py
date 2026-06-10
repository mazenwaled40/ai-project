from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import get_current_user

router = APIRouter(tags=["Dashboard & Students Management"])

@router.get("/dashboard/stats")
def get_dashboard_stats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {"message": "Stats data here"}

@router.get("/students/disruptive")
def get_disruptive_students(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {"data": "List of disruptive students"}

@router.get("/students")
def get_all_students(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Student).all()

@router.get("/students/{student_id}")
def get_student_by_id(student_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
