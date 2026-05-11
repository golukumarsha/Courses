from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ─── Submit / Update Review ───────────────────────────
class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5, description="1 se 5 stars")
    review: Optional[str] = Field(default=None, max_length=1000)

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError("Rating sirf 1 se 5 ke beech honi chahiye")
        return v


# ─── Review Response ──────────────────────────────────
class ReviewOut(BaseModel):
    id:         int
    course_id:  int
    user_id:    int
    username:   str
    rating:     int
    review:     Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
