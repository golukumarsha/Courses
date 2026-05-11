from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.connection import get_db
from models.review_model import ReviewCreate, ReviewOut
from utils.auth import get_current_user, require_admin

reviews_router = APIRouter(prefix="/reviews", tags=["Reviews & Ratings"])


# ─── POST: Review submit karo ─────────────────────────
@reviews_router.post("/course/{course_id}", response_model=ReviewOut)
def submit_review(
    course_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Course exist karta hai?
    course = db.execute(
        text("SELECT id FROM courses WHERE id = :id"), {"id": course_id}
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course nahi mila")

    # Pehle se review hai?
    existing = db.execute(text("""
        SELECT id FROM reviews
        WHERE course_id = :course_id AND user_id = :user_id
    """), {"course_id": course_id, "user_id": current_user["id"]}).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Aap pehle se is course ka review de chuke hain. Update karein."
        )

    result = db.execute(text("""
        INSERT INTO reviews (course_id, user_id, username, rating, review)
        VALUES (:course_id, :user_id, :username, :rating, :review)
        RETURNING id, course_id, user_id, username, rating, review, created_at
    """), {
        "course_id": course_id,
        "user_id":   current_user["id"],
        "username":  current_user["username"],
        "rating":    payload.rating,
        "review":    payload.review,
    })
    db.commit()
    return dict(result.mappings().first())


# ─── PUT: Apna review update karo ────────────────────
@reviews_router.put("/course/{course_id}", response_model=ReviewOut)
def update_review(
    course_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing = db.execute(text("""
        SELECT id FROM reviews
        WHERE course_id = :course_id AND user_id = :user_id
    """), {"course_id": course_id, "user_id": current_user["id"]}).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Aapka koi review nahi mila. Pehle submit karein."
        )

    result = db.execute(text("""
        UPDATE reviews
        SET rating = :rating, review = :review
        WHERE course_id = :course_id AND user_id = :user_id
        RETURNING id, course_id, user_id, username, rating, review, created_at
    """), {
        "rating":    payload.rating,
        "review":    payload.review,
        "course_id": course_id,
        "user_id":   current_user["id"],
    })
    db.commit()
    return dict(result.mappings().first())


# ─── DELETE: Apna review hatao ────────────────────────
@reviews_router.delete("/course/{course_id}")
def delete_review(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    existing = db.execute(text("""
        SELECT id FROM reviews
        WHERE course_id = :course_id AND user_id = :user_id
    """), {"course_id": course_id, "user_id": current_user["id"]}).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Review nahi mila")

    db.execute(text("""
        DELETE FROM reviews
        WHERE course_id = :course_id AND user_id = :user_id
    """), {"course_id": course_id, "user_id": current_user["id"]})
    db.commit()
    return {"message": f"Course #{course_id} ka review delete ho gaya ✅"}


# ─── GET: Kisi course ke saare reviews ───────────────
@reviews_router.get("/course/{course_id}")
def get_course_reviews(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.execute(
        text("SELECT id, title FROM courses WHERE id = :id"), {"id": course_id}
    ).mappings().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course nahi mila")

    reviews = db.execute(text("""
        SELECT id, course_id, user_id, username, rating, review, created_at
        FROM reviews
        WHERE course_id = :course_id
        ORDER BY created_at DESC
    """), {"course_id": course_id}).mappings().all()

    stats = db.execute(text("""
        SELECT
            COUNT(*)                        AS total_reviews,
            ROUND(AVG(rating)::numeric, 2)  AS avg_rating,
            COUNT(CASE WHEN rating=5 THEN 1 END) AS five_star,
            COUNT(CASE WHEN rating=4 THEN 1 END) AS four_star,
            COUNT(CASE WHEN rating=3 THEN 1 END) AS three_star,
            COUNT(CASE WHEN rating=2 THEN 1 END) AS two_star,
            COUNT(CASE WHEN rating=1 THEN 1 END) AS one_star
        FROM reviews WHERE course_id = :course_id
    """), {"course_id": course_id}).mappings().first()

    return {
        "course_id":    course_id,
        "course_title": course["title"],
        "stats":        dict(stats),
        "reviews":      [dict(r) for r in reviews]
    }


# ─── GET: Mera review for a course ───────────────────
@reviews_router.get("/my/course/{course_id}")
def get_my_review(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    review = db.execute(text("""
        SELECT id, course_id, user_id, username, rating, review, created_at
        FROM reviews
        WHERE course_id = :course_id AND user_id = :user_id
    """), {"course_id": course_id, "user_id": current_user["id"]}).mappings().first()

    if not review:
        return {"has_review": False, "review": None}
    return {"has_review": True, "review": dict(review)}


# ─── GET: Mere saare reviews ─────────────────────────
@reviews_router.get("/my/all")
def get_my_all_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    reviews = db.execute(text("""
        SELECT r.id, r.course_id, c.title AS course_title,
               r.rating, r.review, r.created_at
        FROM reviews r
        JOIN courses c ON c.id = r.course_id
        WHERE r.user_id = :user_id
        ORDER BY r.created_at DESC
    """), {"user_id": current_user["id"]}).mappings().all()

    return {
        "username":      current_user["username"],
        "total_reviews": len(reviews),
        "reviews":       [dict(r) for r in reviews]
    }


# ─── GET: Top rated courses ───────────────────────────
@reviews_router.get("/top-rated")
def top_rated_courses(db: Session = Depends(get_db)):
    results = db.execute(text("""
        SELECT
            c.id, c.title, c.instructor, c.category, c.price,
            c.is_published,
            COUNT(r.id)                       AS total_reviews,
            ROUND(AVG(r.rating)::numeric, 2)  AS avg_rating
        FROM courses c
        JOIN reviews r ON r.course_id = c.id
        GROUP BY c.id, c.title, c.instructor, c.category, c.price, c.is_published
        HAVING COUNT(r.id) >= 1
        ORDER BY avg_rating DESC, total_reviews DESC
        LIMIT 10
    """)).mappings().all()

    return {
        "total": len(results),
        "top_rated": [dict(r) for r in results]
    }


# ─── DELETE: Admin kisi bhi review ko hata sakta hai ─
@reviews_router.delete("/admin/{review_id}")
def admin_delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    existing = db.execute(
        text("SELECT id FROM reviews WHERE id = :id"), {"id": review_id}
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Review nahi mila")

    db.execute(text("DELETE FROM reviews WHERE id = :id"), {"id": review_id})
    db.commit()
    return {"message": f"Review #{review_id} admin ne delete kiya ✅"}
