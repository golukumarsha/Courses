from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.connection import get_db      # ✅ Fix
from models.course_model import Course      # ✅ Fix
from utils.auth import require_admin        # ✅ Fix

router = APIRouter(tags=["Courses"])


# ─── Home ─────────────────────────────────────────────
@router.get("/home")
def home():
    return {"message": "Course API Running 🚀"}


# ─── GET course by ID ─────────────────────────────────
@router.get("/course/{id}")
def get_course(id: int, db: Session = Depends(get_db)):
    course = db.execute(
        text("SELECT * FROM courses WHERE id = :id"), {"id": id}
    ).mappings().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/data/{id}")
def get_course_by_id(id: int, db: Session = Depends(get_db)):
    course = db.execute(
        text("SELECT * FROM courses WHERE id = :id"), {"id": id}
    ).mappings().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


# ─── GET all courses (public) ─────────────────────────
@router.get("/courses")
def get_all_courses(db: Session = Depends(get_db)):
    return db.execute(text("SELECT * FROM courses")).mappings().all()


# ─── POST - Create course (Admin only) ────────────────
@router.post("/create")
def create_course(
    course: Course,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    try:
        data = course.model_dump(
            exclude={"id", "discounted_price", "price_category"})
        # ✅ Safety: agar kisi tarah id aa bhi jaye toh hata do
        data.pop("id", None)
        data["duration_hours"] = int(data["duration_hours"])
        db.execute(text("""
            INSERT INTO courses
                (title, instructor, category, price, duration_hours, is_published, discount_percent)
            VALUES
                (:title, :instructor, :category, :price, :duration_hours, :is_published, :discount_percent)
        """), data)
        db.commit()
        return {"message": f"Course '{course.title}' add kiya by {current_user['username']}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")


# ─── PUT - Update course (Admin only) ─────────────────
@router.put("/update/{id}")
def update_course(
    id: int,
    course: Course,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    existing = db.execute(
        text("SELECT * FROM courses WHERE id = :id"), {"id": id}
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Course nahi mila")

    data = course.model_dump(
        exclude={"id", "discounted_price", "price_category"})
    data.pop("id", None)
    data["id"] = id

    db.execute(text("""
        UPDATE courses
        SET title            = :title,
            instructor       = :instructor,
            category         = :category,
            price            = :price,
            duration_hours   = :duration_hours,
            is_published     = :is_published,
            discount_percent = :discount_percent
        WHERE id = :id
    """), data)
    db.commit()
    return {"message": f"Course #{id} update hua ✅ by {current_user['username']}"}


# ─── DELETE - Delete course (Admin only) ──────────────
@router.delete("/delete/{id}")
def delete_course(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    existing = db.execute(
        text("SELECT * FROM courses WHERE id = :id"), {"id": id}
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Course nahi mila")

    db.execute(text("DELETE FROM courses WHERE id = :id"), {"id": id})
    db.commit()
    return {"message": f"Course #{id} delete hua ✅ by {current_user['username']}"}


# ─── FILTER ───────────────────────────────────────────
@router.get("/filter")
def filter_courses(
    category:     Optional[str] = Query(None),
    instructor:   Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    min_price:    Optional[float] = Query(None),
    max_price:    Optional[float] = Query(None),
    min_duration: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = "SELECT * FROM courses WHERE 1=1"
    params = {}

    if category:
        query += " AND LOWER(category) = LOWER(:category)"
        params["category"] = category

    if instructor:
        query += " AND LOWER(instructor) LIKE LOWER(:instructor)"
        params["instructor"] = f"%{instructor}%"

    if is_published is not None:
        query += " AND is_published = :is_published"
        params["is_published"] = is_published

    if min_price is not None:
        query += " AND price >= :min_price"
        params["min_price"] = min_price

    if max_price is not None:
        query += " AND price <= :max_price"
        params["max_price"] = max_price

    if min_duration is not None:
        query += " AND duration_hours >= :min_duration"
        params["min_duration"] = min_duration

    return db.execute(text(query), params).mappings().all()


# ─── SEARCH ───────────────────────────────────────────
@router.get("/search")
def search_courses(
    q: str = Query(..., min_length=1,
                   description="Search query — title, instructor, ya category mein dhundhe"),
    db: Session = Depends(get_db)
):
    """
    GET /search?q=python
    Title, instructor, aur category mein search karta hai (case-insensitive).
    """
    keyword = f"%{q.strip()}%"
    results = db.execute(text("""
        SELECT * FROM courses
        WHERE LOWER(title)      LIKE LOWER(:kw)
           OR LOWER(instructor) LIKE LOWER(:kw)
           OR LOWER(category)   LIKE LOWER(:kw)
        ORDER BY
            CASE
                WHEN LOWER(title) LIKE LOWER(:kw) THEN 1
                WHEN LOWER(instructor) LIKE LOWER(:kw) THEN 2
                ELSE 3
            END,
            title ASC
    """), {"kw": keyword}).mappings().all()

    return {
        "query":        q,
        "total_found":  len(results),
        "results":      [dict(r) for r in results]
    }


# ─── PAGINATION ───────────────────────────────────────
@router.get("/items")
def get_paginated_courses(
    page:  int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit

    total = db.execute(
        text("SELECT COUNT(*) as cnt FROM courses")
    ).mappings().first()["cnt"]

    data = db.execute(
        text("SELECT * FROM courses LIMIT :limit OFFSET :offset"),
        {"limit": limit, "offset": offset}
    ).mappings().all()

    return {
        "total":       total,
        "page":        page,
        "limit":       limit,
        "total_pages": -(-total // limit),
        "data":        data
    }
