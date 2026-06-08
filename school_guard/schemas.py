from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────
# ROLE
# ─────────────────────────────────────────
class RoleBase(BaseModel):
    role_name: str

class RoleCreate(RoleBase):
    pass

class RoleOut(RoleBase):
    role_id: int
    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# USER
# ─────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int

class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role_id: int
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


# ─────────────────────────────────────────
# CAMERA
# ─────────────────────────────────────────
class CameraCreate(BaseModel):
    location: str
    rtsp_url: str
    status: Optional[str] = "active"

class CameraUpdate(BaseModel):
    location: Optional[str] = None
    rtsp_url: Optional[str] = None
    status: Optional[str] = None

class CameraOut(CameraCreate):
    camera_id: int
    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# INCIDENT
# ─────────────────────────────────────────
class IncidentCreate(BaseModel):
    camera_id: int
    type: str
    severity: Optional[str] = "medium"

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None

class IncidentOut(BaseModel):
    incident_id: int
    camera_id: int
    type: str
    timestamp: datetime
    severity: str
    status: str
    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# ALERT
# ─────────────────────────────────────────
class AlertCreate(BaseModel):
    incident_id: int
    user_id: int
    video_clip_path: Optional[str] = None

class AlertUpdate(BaseModel):
    alert_status: Optional[str] = None

class AlertOut(BaseModel):
    alert_id: int
    incident_id: int
    user_id: int
    sent_time: datetime
    alert_status: str
    video_clip_path: Optional[str]
    class Config:
        from_attributes = True


# ─────────────────────────────────────────
# FEEDBACK
# ─────────────────────────────────────────
class FeedbackCreate(BaseModel):
    user_id: int
    incident_id: int
    decision: str
    notes: Optional[str] = None

class FeedbackOut(BaseModel):
    feedback_id: int
    user_id: int
    incident_id: int
    decision: str
    feedback_time: datetime
    notes: Optional[str]
    class Config:
        from_attributes = True
