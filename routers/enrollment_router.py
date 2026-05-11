from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.connection import get_db
from models.enrollment_model import EnrollStatusUpdate, EnrollmentOut
from utils.auth import get_current_user, require_admin

enrollment_router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


# ─── POST: Course enroll karo ─────────────────────────
@enrollment_router.post("/enroll/{course_id}", response_model=EnrollmentOut)
def enroll_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Course exist karta hai?
    course = db.execute(
        text("SELECT id, title, is_published FROM courses WHERE id = :id"),
        {"id": course_id}
    ).mappings().first()

    if not course:
        raise HTTPException(status_code=404, detail="Course nahi mila")

    if not course["is_published"]:
        raise HTTPException(
            status_code=400, detail="Yeh course published nahi hai, enroll nahi kar sakte")

    # Pehle se enrolled hai?
    existing = db.execute(text("""
        SELECT id, status FROM enrollments
        WHERE user_id = :user_id AND course_id = :course_id
    """), {"user_id": current_user["id"], "course_id": course_id}).mappings().first()

    if existing:
        if existing["status"] == "cancelled":
            # Re-enroll karo
            result = db.execute(text("""
                UPDATE enrollments SET status = 'active'
                WHERE user_id = :user_id AND course_id = :course_id
                RETURNING id, user_id, course_id, username, course_title, enrolled_at, status
            """), {"user_id": current_user["id"], "course_id": course_id})
            db.commit()
            return dict(result.mappings().first())
        raise HTTPException(
            status_code=400,
            detail=f"Aap pehle se is course mein enrolled hain (status: {existing['status']})"
        )

    result = db.execute(text("""
        INSERT INTO enrollments (user_id, course_id, username, course_title, status)
        VALUES (:user_id, :course_id, :username, :course_title, 'active')
        RETURNING id, user_id, course_id, username, course_title, enrolled_at, status
    """), {
        "user_id":      current_user["id"],
        "course_id":    course_id,
        "username":     current_user["username"],
        "course_title": course["title"],
    })
    db.commit()
    return dict(result.mappings().first())


# ─── DELETE: Enrollment cancel karo ──────────────────
@enrollment_router.delete("/cancel/{course_id}")
def cancel_enrollment(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing = db.execute(text("""
        SELECT id, status FROM enrollments
        WHERE user_id = :user_id AND course_id = :course_id
    """), {"user_id": current_user["id"], "course_id": course_id}).first()

    if not existing:
        raise HTTPException(
            status_code=404, detail="Aap is course mein enrolled nahi hain")

    db.execute(text("""
        UPDATE enrollments SET status = 'cancelled'
        WHERE user_id = :user_id AND course_id = :course_id
    """), {"user_id": current_user["id"], "course_id": course_id})
    db.commit()
    return {"message": f"Course #{course_id} ka enrollment cancel ho gaya ✅"}


# ─── PUT: Status update karo (active/completed/cancelled)
@enrollment_router.put("/status/{course_id}", response_model=EnrollmentOut)
def update_enrollment_status(
    course_id: int,
    payload: EnrollStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    allowed = ["active", "completed", "cancelled"]
    if payload.status not in allowed:
        raise HTTPException(
            status_code=400, detail=f"Status sirf {allowed} ho sakta hai")

    existing = db.execute(text("""
        SELECT id FROM enrollments
        WHERE user_id = :user_id AND course_id = :course_id
    """), {"user_id": current_user["id"], "course_id": course_id}).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Enrollment nahi mila")

    result = db.execute(text("""
        UPDATE enrollments SET status = :status
        WHERE user_id = :user_id AND course_id = :course_id
        RETURNING id, user_id, course_id, username, course_title, enrolled_at, status
    """), {"status": payload.status, "user_id": current_user["id"], "course_id": course_id})
    db.commit()
    return dict(result.mappings().first())


# ─── GET: Mere saare enrollments ──────────────────────
@enrollment_router.get("/my")
def my_enrollments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    rows = db.execute(text("""
        SELECT
            e.id, e.course_id, e.course_title, e.enrolled_at, e.status,
            c.instructor, c.category, c.price, c.duration_hours,
            c.discount_percent,
            ROUND((c.price - c.price * c.discount_percent / 100)::numeric, 2) AS discounted_price
        FROM enrollments e
        JOIN courses c ON c.id = e.course_id
        WHERE e.user_id = :user_id
        ORDER BY e.enrolled_at DESC
    """), {"user_id": current_user["id"]}).mappings().all()

    stats = {
        "total":     len(rows),
        "active":    sum(1 for r in rows if r["status"] == "active"),
        "completed": sum(1 for r in rows if r["status"] == "completed"),
        "cancelled": sum(1 for r in rows if r["status"] == "cancelled"),
    }

    return {
        "username":    current_user["username"],
        "stats":       stats,
        "enrollments": [dict(r) for r in rows]
    }


# ─── GET: Ek course ke saare enrolled users (Admin) ──
@enrollment_router.get("/course/{course_id}")
def course_enrollments(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    course = db.execute(
        text("SELECT id, title FROM courses WHERE id = :id"), {"id": course_id}
    ).mappings().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course nahi mila")

    rows = db.execute(text("""
        SELECT
            e.id, e.user_id, e.username, e.enrolled_at, e.status,
            u.email, u.is_active
        FROM enrollments e
        JOIN users u ON u.id = e.user_id
        WHERE e.course_id = :course_id
        ORDER BY e.enrolled_at DESC
    """), {"course_id": course_id}).mappings().all()

    stats = {
        "total":     len(rows),
        "active":    sum(1 for r in rows if r["status"] == "active"),
        "completed": sum(1 for r in rows if r["status"] == "completed"),
        "cancelled": sum(1 for r in rows if r["status"] == "cancelled"),
    }

    return {
        "course_id":    course_id,
        "course_title": course["title"],
        "stats":        stats,
        "enrolled_users": [dict(r) for r in rows]
    }


# ─── GET: Saare enrollments (Admin) ──────────────────
@enrollment_router.get("/all")
def all_enrollments(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    rows = db.execute(text("""
        SELECT
            e.id, e.user_id, e.username, e.course_id, e.course_title,
            e.enrolled_at, e.status,
            c.category, c.instructor
        FROM enrollments e
        JOIN courses c ON c.id = e.course_id
        ORDER BY e.enrolled_at DESC
    """)).mappings().all()

    total_stats = {
        "total":     len(rows),
        "active":    sum(1 for r in rows if r["status"] == "active"),
        "completed": sum(1 for r in rows if r["status"] == "completed"),
        "cancelled": sum(1 for r in rows if r["status"] == "cancelled"),
    }

    return {
        "stats":       total_stats,
        "enrollments": [dict(r) for r in rows]
    }


# ─── GET: Top enrolled courses ────────────────────────
@enrollment_router.get("/top-courses")
def top_enrolled_courses(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT
            c.id, c.title, c.instructor, c.category, c.price,
            COUNT(e.id)                                              AS total_enrollments,
            COUNT(CASE WHEN e.status='active'    THEN 1 END)        AS active_enrollments,
            COUNT(CASE WHEN e.status='completed' THEN 1 END)        AS completed_enrollments
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        GROUP BY c.id, c.title, c.instructor, c.category, c.price
        ORDER BY total_enrollments DESC
        LIMIT 10
    """)).mappings().all()

    return {
        "total": len(rows),
        "top_courses": [dict(r) for r in rows]
    }
