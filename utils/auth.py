import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.connection import get_db      # ✅ Fix

# ─── Config ───────────────────────────────────────────
SECRET_KEY = os.getenv(
    "SECRET_KEY", "coursevault-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24   # 24 ghante

# ─── Password Hashing ─────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── Bearer Scheme (Swagger mein BearerAuth box dikhayega) ───
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid ya expire ho gaya hai",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── Current User Dependency ──────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=401, detail="Token mein email nahi mili")

    user = db.execute(
        text("SELECT * FROM users WHERE email = :email"),
        {"email": email}
    ).mappings().first()

    if not user:
        raise HTTPException(status_code=401, detail="User nahi mila")
    return user


# ─── Admin Only ───────────────────────────────────────
def require_admin(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sirf Admin yeh kaam kar sakta hai 🚫"
        )
    return current_user


# ─── Any Logged-in User ───────────────────────────────
def require_user(current_user=Depends(get_current_user)):
    return current_user
