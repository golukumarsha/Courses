from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.connection import get_db
from models.auth_model import UserRegister, UserLogin, TokenResponse, UserOut
from utils.auth import hash_password, verify_password, create_access_token, get_current_user
from utils.logger import get_logger

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger("routers.auth")


# ─── REGISTER ─────────────────────────────────────────
@auth_router.post("/register", response_model=UserOut)
def register(user: UserRegister, db: Session = Depends(get_db)):
    logger.info(
        f"REGISTER attempt — username='{user.username}' email='{user.email}' role='{user.role}'")

    if db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user.email}).first():
        logger.warning(f"REGISTER failed — email already exists: {user.email}")
        raise HTTPException(
            status_code=400, detail="Yeh email already registered hai")

    if db.execute(text("SELECT id FROM users WHERE username = :username"), {"username": user.username}).first():
        logger.warning(
            f"REGISTER failed — username already taken: {user.username}")
        raise HTTPException(
            status_code=400, detail="Yeh username already le liya gaya hai")

    hashed = hash_password(user.password)
    result = db.execute(text("""
        INSERT INTO users (username, email, hashed_password, role, is_active)
        VALUES (:username, :email, :hashed_password, :role, true)
        RETURNING id, username, email, role
    """), {"username": user.username, "email": user.email, "hashed_password": hashed, "role": user.role})
    db.commit()
    logger.info(
        f"REGISTER success — username='{user.username}' role='{user.role}'")
    return result.mappings().first()


# ─── LOGIN ────────────────────────────────────────────
@auth_router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"LOGIN attempt — email='{credentials.email}'")

    user = db.execute(
        text(
            "SELECT * FROM users WHERE email = :email"), {"email": credentials.email}
    ).mappings().first()

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        logger.warning(
            f"LOGIN failed — wrong email/password for '{credentials.email}'")
        raise HTTPException(
            status_code=401, detail="Email ya password galat hai")

    if not user["is_active"]:
        logger.warning(
            f"LOGIN failed — account deactivated: '{credentials.email}'")
        raise HTTPException(status_code=403, detail="Account deactivated hai")

    token = create_access_token(
        data={"sub": user["email"], "role": user["role"], "username": user["username"]})
    logger.info(
        f"LOGIN success — username='{user['username']}' role='{user['role']}'")
    return {"access_token": token, "token_type": "bearer", "role": user["role"], "username": user["username"]}


# ─── ME ───────────────────────────────────────────────
@auth_router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    logger.debug(f"GET /me — user='{current_user['username']}'")
    return current_user


# ─── ALL USERS (Admin) ────────────────────────────────
@auth_router.get("/users")
def get_all_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        logger.warning(
            f"UNAUTHORIZED /users access by '{current_user['username']}'")
        raise HTTPException(
            status_code=403, detail="Sirf Admin dekh sakta hai")
    users = db.execute(
        text("SELECT id, username, email, role, is_active FROM users")).mappings().all()
    logger.info(
        f"GET /users by admin='{current_user['username']}' — {len(users)} users")
    return users
