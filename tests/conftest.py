"""
tests/conftest.py
Shared fixtures for all tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from main import app
from database.connection import get_db
from database.db_model import Base

# ─── Test Database (SQLite in-memory) ─────────────────
TEST_DATABASE_URL = "sqlite:///./test_coursevault.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Override DB dependency ────────────────────────────
app.dependency_overrides[get_db] = override_get_db


# ─── Client fixture ───────────────────────────────────
@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


# ─── Admin user fixture ───────────────────────────────
@pytest.fixture(scope="session")
def admin_token(client):
    # Register admin
    client.post("/auth/register", json={
        "username": "testadmin",
        "email":    "testadmin@example.com",
        "password": "Admin@1234",
        "role":     "admin"
    })
    # Login
    res = client.post("/auth/login", json={
        "email":    "testadmin@example.com",
        "password": "Admin@1234"
    })
    return res.json()["access_token"]


# ─── Normal user fixture ──────────────────────────────
@pytest.fixture(scope="session")
def user_token(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "email":    "testuser@example.com",
        "password": "User@1234",
        "role":     "user"
    })
    res = client.post("/auth/login", json={
        "email":    "testuser@example.com",
        "password": "User@1234"
    })
    return res.json()["access_token"]


# ─── Admin headers fixture ────────────────────────────
@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ─── User headers fixture ─────────────────────────────
@pytest.fixture(scope="session")
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


# ─── Sample course data ───────────────────────────────
@pytest.fixture
def sample_course():
    return {
        "title":            "Python Basics",
        "instructor":       "Aanya Sharma",
        "category":         "programming",
        "price":            499.00,
        "duration_hours":   10,
        "discount_percent": 10.0,
        "is_published":     True
    }


@pytest.fixture
def sample_course_2():
    return {
        "title":            "FastAPI Course",
        "instructor":       "Rohan Mehta",
        "category":         "web development",
        "price":            799.00,
        "duration_hours":   20,
        "discount_percent": 0.0,
        "is_published":     True
    }
