from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── Enroll karo ──────────────────────────────────────
class EnrollRequest(BaseModel):
    pass   # sirf course_id URL se aata hai


# ─── Status update ────────────────────────────────────
class EnrollStatusUpdate(BaseModel):
    status: str = Field(..., description="active | completed | cancelled")

    class Config:
        json_schema_extra = {"example": {"status": "completed"}}


# ─── Response ─────────────────────────────────────────
class EnrollmentOut(BaseModel):
    id:           int
    user_id:      int
    course_id:    int
    username:     str
    course_title: str
    enrolled_at:  datetime
    status:       str

    model_config = {"from_attributes": True}
