from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing import Optional


class Course(BaseModel):
    id:               Optional[int] = Field(
        default=None, exclude=True)  # ✅ Swagger mein nahi dikhega
    title:            str = Field(min_length=2, max_length=100)
    instructor:       str = Field(min_length=2, max_length=50)
    category:         str = Field(min_length=2, max_length=30)
    price:            float = Field(gt=0, le=1_00_000)
    duration_hours:   int = Field(gt=0, le=500)
    discount_percent: float = Field(ge=0, le=100, default=0.0)
    is_published:     bool = Field(default=False)

    model_config = {"populate_by_name": True}

    @field_validator('title')
    @classmethod
    def clean_title(cls, v): return v.title()

    @field_validator('instructor')
    @classmethod
    def clean_instructor(cls, v): return v.title()

    @field_validator('category')
    @classmethod
    def clean_category(cls, v): return v.lower()

    @model_validator(mode='after')
    def check_published_and_price(self):
        if self.is_published and self.discount_percent == 100:
            raise ValueError('Published course ka discount 100% nahi ho sakta')
        return self

    @computed_field
    @property
    def discounted_price(self) -> float:
        return round(self.price - (self.price * self.discount_percent / 100), 2)

    @computed_field
    @property
    def price_category(self) -> str:
        if self.price < 500:
            return 'Free / Budget'
        elif self.price < 5000:
            return 'Mid-Range'
        else:
            return 'Premium'
