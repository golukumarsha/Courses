from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email:    str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=6, max_length=100)
    role:     str = Field(default="user")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ["user", "admin"]:
            raise ValueError("Role sirf 'user' ya 'admin' ho sakta hai")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v or "." not in v:
            raise ValueError("Valid email address daalein")
        return v.lower()


class UserLogin(BaseModel):
    email:    str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str
    username:     str


class UserOut(BaseModel):
    id:       int
    username: str
    email:    str
    role:     str
