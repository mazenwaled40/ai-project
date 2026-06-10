import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Student(Base):
    __tablename__ = "student"
    student_id = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    grade      = Column(String(50), nullable=True)
    incidents  = relationship("Incident", back_populates="student")

class Role(Base):
    __tablename__ = "role"
    role_id   = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "user"
    user_id  = Column(Integer, primary_key=True, index=True)
    name     = Column(String(100), nullable=False)
    email    = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role_id  = Column(Integer, ForeignKey("role.role_id"), nullable=False)
    role     = relationship("Role", back_populates="users")
    alerts   = relationship("Alert", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")

class Camera(Base):
    __tablename__ = "camera"
    camera_id = Column(Integer, primary_key=True, index=True)
    location  = Column(String(200), nullable=False)
    rtsp_url  = Column(String(500), nullable=False)
    status    = Column(String(20), nullable=False, default="active")
    incidents = relationship("Incident", back_populates="camera")

class Incident(Base):
    __tablename__ = "incident"
    incident_id = Column(Integer, primary_key=True, index=True)
    camera_id   = Column(Integer, ForeignKey("camera.camera_id"), nullable=False)
    student_id  = Column(Integer, ForeignKey("student.student_id"), nullable=True)
    type        = Column(String(100), nullable=False)
    timestamp   = Column(DateTime(timezone=True), server_default=func.now())
    severity    = Column(String(20), nullable=False, default="medium")
    status      = Column(String(20), nullable=False, default="pending")
    
    camera      = relationship("Camera", back_populates="incidents")
    student     = relationship("Student", back_populates="incidents")
    alerts      = relationship("Alert", back_populates="incident")
    feedbacks   = relationship("Feedback", back_populates="incident")

class Alert(Base):
    __tablename__ = "alert"
    alert_id      = Column(Integer, primary_key=True, index=True)
    incident_id   = Column(Integer, ForeignKey("incident.incident_id"), nullable=False)
    user_id       = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    sent_time     = Column(DateTime(timezone=True), server_default=func.now())
    alert_status  = Column(String(20), nullable=False, default="sent")
    video_clip_path = Column(String(500), nullable=True)
    incident      = relationship("Incident", back_populates="alerts")
    user          = relationship("User", back_populates="alerts")

class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id   = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    incident_id   = Column(Integer, ForeignKey("incident.incident_id"), nullable=False)
    decision      = Column(String(20), nullable=False)
    feedback_time = Column(DateTime(timezone=True), server_default=func.now())
    notes         = Column(Text, nullable=True)
    user          = relationship("User", back_populates="feedbacks")
    incident      = relationship("Incident", back_populates="feedbacks") hthoty da zy ma hwa
