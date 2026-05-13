import re
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing import Optional


# ─── Allowed characters ───────────────────────────────
TITLE_REGEX = re.compile(r"^[a-zA-Z0-9 _\-\.\+\#\(\)\/&]+$")
NAME_REGEX = re.compile(r"^[a-zA-Z\s\.\-']+$")
CATEGORY_REGEX = re.compile(r"^[a-zA-Z0-9 \-\/]+$")


class Course(BaseModel):
    id:               Optional[int] = Field(default=None, exclude=True)
    title:            str = Field(min_length=3,  max_length=100)
    instructor:       str = Field(min_length=3,  max_length=50)
    category:         str = Field(min_length=2,  max_length=30)
    price:            float = Field(gt=0,          le=1_00_000)
    duration_hours:   int = Field(gt=0,          le=500)
    discount_percent: float = Field(ge=0,          le=99, default=0.0)
    is_published:     bool = Field(default=False)

    model_config = {"populate_by_name": True}

    # ── Title ──────────────────────────────────────────
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Title khali nahi ho sakta")
        if len(v) < 3:
            raise ValueError("Title kam se kam 3 characters ka hona chahiye")
        if not TITLE_REGEX.match(v):
            raise ValueError(
                "Title mein sirf letters, numbers, spaces aur yeh characters allowed hain: - . + # ( ) / &"
            )
        # Repeated spaces check
        if "  " in v:
            raise ValueError("Title mein double spaces nahi chalenge")
        return v.title()

    # ── Instructor ─────────────────────────────────────
    @field_validator('instructor')
    @classmethod
    def validate_instructor(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Instructor ka naam khali nahi ho sakta")
        if not NAME_REGEX.match(v):
            raise ValueError(
                "Instructor ke naam mein sirf letters, spaces, dots aur hyphens allowed hain"
            )
        if len(v.split()) < 1:
            raise ValueError("Instructor ka naam daalein")
        return v.title()

    # ── Category ───────────────────────────────────────
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Category khali nahi ho sakti")
        if not CATEGORY_REGEX.match(v):
            raise ValueError(
                "Category mein sirf letters, numbers, spaces aur hyphen allowed hain"
            )
        ALLOWED_CATEGORIES = [
            "programming", "web development", "data science", "computer science",
            "databases", "devops", "design", "cloud", "security", "mobile development",
            "machine learning", "artificial intelligence", "networking", "other"
        ]
        v_lower = v.lower()
        # Exact match check — agar allowed list mein nahi hai toh warning nahi, allow karo
        # (flexible rakhte hain, sirf format validate karo)
        return v_lower

    # ── Price ──────────────────────────────────────────
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        # Integer-like check — decimal allowed but not more than 2 places
        if round(v, 2) != v:
            raise ValueError(
                "Price mein sirf 2 decimal places allowed hain (e.g. 499.99)")
        if v < 1:
            raise ValueError("Price kam se kam ₹1 honi chahiye")
        if v > 1_00_000:
            raise ValueError("Price ₹1,00,000 se zyada nahi ho sakti")
        return round(v, 2)

    # ── Duration ───────────────────────────────────────
    @field_validator('duration_hours')
    @classmethod
    def validate_duration(cls, v):
        if not isinstance(v, int):
            raise ValueError(
                "Duration sirf poora number (integer) hona chahiye, e.g. 10")
        if v < 1:
            raise ValueError("Duration kam se kam 1 ghanta hona chahiye")
        if v > 500:
            raise ValueError("Duration 500 ghante se zyada nahi ho sakta")
        return v

    # ── Discount ───────────────────────────────────────
    @field_validator('discount_percent')
    @classmethod
    def validate_discount(cls, v):
        if v < 0:
            raise ValueError("Discount negative nahi ho sakta")
        if v >= 100:
            raise ValueError("Discount 100% ya usse zyada nahi ho sakta")
        if round(v, 2) != v:
            raise ValueError(
                "Discount mein sirf 2 decimal places allowed hain")
        return round(v, 2)

    # ── Cross-field validation ──────────────────────────
    @model_validator(mode='after')
    def cross_field_checks(self):
        # Published course pe 100% discount nahi
        if self.is_published and self.discount_percent >= 99:
            raise ValueError(
                "Published course ka discount 99% ya usse zyada nahi ho sakta")

        # Agar price < 100 hai aur discount > 50% hai — warning raise karo
        if self.price < 100 and self.discount_percent > 50:
            raise ValueError(
                f"₹{self.price} price pe {self.discount_percent}% discount bahut zyada hai"
            )
        return self

    # ── Computed fields ────────────────────────────────
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
