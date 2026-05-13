import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

REVIEW_TEXT_REGEX = re.compile(
    r"^[a-zA-Z0-9 \u0900-\u097F\.,!?'\"\-\(\)\n\r]+$")


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5, description="1 se 5 stars")
    review: Optional[str] = Field(default=None, min_length=5, max_length=1000)

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError("Rating sirf 1, 2, 3, 4 ya 5 ho sakti hai")
        return v

    @field_validator('review')
    @classmethod
    def validate_review_text(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Review kam se kam 5 characters ka hona chahiye")
        if len(v) > 1000:
            raise ValueError("Review 1000 characters se zyada nahi ho sakta")
        # Check for spam patterns
        if v.lower().count("http") > 0 or v.lower().count("www.") > 0:
            raise ValueError("Review mein links allowed nahi hain")
        # Check for excessive repetition
        if len(set(v.lower().replace(" ", ""))) < 3:
            raise ValueError("Meaningful review likhein")
        return v


class ReviewOut(BaseModel):
    id:         int
    course_id:  int
    user_id:    int
    username:   str
    rating:     int
    review:     Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
