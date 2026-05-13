import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

# ─── Patterns ─────────────────────────────────────────
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_\.]+$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$")

BANNED_USERNAMES = {"admin", "root", "superuser",
                    "system", "null", "undefined", "test"}


# ─── Register ─────────────────────────────────────────
class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email:    str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    role:     str = Field(default="user")

    # ── Username ────────────────────────────────────────
    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Username khali nahi ho sakta")
        if not USERNAME_REGEX.match(v):
            raise ValueError(
                "Username mein sirf letters, numbers, underscore (_) aur dot (.) allowed hain"
            )
        if v.lower() in BANNED_USERNAMES:
            raise ValueError(
                f"'{v}' username allowed nahi hai, koi aur chunein")
        if v.startswith(".") or v.endswith("."):
            raise ValueError("Username dot se start ya end nahi ho sakta")
        if ".." in v:
            raise ValueError("Username mein double dot (..) nahi ho sakta")
        return v

    # ── Email ───────────────────────────────────────────
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError(
                "Valid email address daalein (e.g. user@example.com)")
        # Disposable email domains block (basic list)
        blocked_domains = {"mailinator.com", "tempmail.com",
                           "throwaway.email", "guerrillamail.com"}
        domain = v.split("@")[1]
        if domain in blocked_domains:
            raise ValueError("Disposable email addresses allowed nahi hain")
        return v

    # ── Password ────────────────────────────────────────
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError(
                "Password kam se kam 8 characters ka hona chahiye")
        if not re.search(r"[A-Z]", v):
            raise ValueError(
                "Password mein kam se kam 1 uppercase letter hona chahiye (A-Z)")
        if not re.search(r"[a-z]", v):
            raise ValueError(
                "Password mein kam se kam 1 lowercase letter hona chahiye (a-z)")
        if not re.search(r"\d", v):
            raise ValueError(
                "Password mein kam se kam 1 number hona chahiye (0-9)")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?]", v):
            raise ValueError(
                "Password mein kam se kam 1 special character hona chahiye (!@#$% etc)")
        weak_passwords = {"Password1!", "Admin123!", "Test1234!", "Pass@1234"}
        if v in weak_passwords:
            raise ValueError(
                "Bahut common password hai, koi strong password chunein")
        return v

    # ── Role ────────────────────────────────────────────
    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        v = v.strip().lower()
        if v not in ["user", "admin"]:
            raise ValueError("Role sirf 'user' ya 'admin' ho sakta hai")
        return v


# ─── Login ────────────────────────────────────────────
class UserLogin(BaseModel):
    email:    str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def clean_email(cls, v):
        return v.strip().lower()


# ─── Token Response ───────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str
    username:     str


# ─── User Output ──────────────────────────────────────
class UserOut(BaseModel):
    id:       int
    username: str
    email:    str
    role:     str
