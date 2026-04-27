from pydantic import BaseModel
from typing import Optional


class Course(BaseModel):
    id: Optional[int] = None
    title: str
    instructor: str
    category: str
    price: float
    duration_hours: int
    is_published: bool
    discount_percent: Optional[float] = None
