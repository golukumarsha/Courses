from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.connection import get_db
from models.review_model import ReviewCreate, ReviewOut
from utils.auth import get_current_user, require_admin
from utils.logger import get_logger

reviews_router = APIRouter(prefix="/reviews", tags=["Reviews & Ratings"])
logger = get_logger("routers.reviews")


@reviews_router.post("/course/{course_id}", response_model=ReviewOut)
def submit_review(course_id: int, payload: ReviewCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    logger.info(
        f"REVIEW submit — user='{current_user['username']}' course_id={course_id} rating={payload.rating}")
    course = db.execute(text("SELECT id FROM courses WHERE id = :id"), {
                        "id": course_id}).first()
    if not course:
        logger.warning(
            f"REVIEW submit failed — course_id={course_id} not found")
        raise HTTPException(status_code=404, detail="Course nahi mila")
    existing = db.execute(text("SELECT id FROM reviews WHERE course_id=:cid AND user_id=:uid"), {
                          "cid": course_id, "uid": current_user["id"]}).first()
    if existing:
        logger.warning(
            f"REVIEW duplicate — user='{current_user['username']}' already reviewed course_id={course_id}")
        raise HTTPException(
            status_code=400, detail="Aap pehle se is course ka review de chuke hain. Update karein.")
    result = db.execute(text("""
        INSERT INTO reviews (course_id, user_id, username, rating, review)
        VALUES (:course_id, :user_id, :username, :rating, :review)
        RETURNING id, course_id, user_id, username, rating, review, created_at
    """), {"course_id": course_id, "user_id": current_user["id"], "username": current_user["username"], "rating": payload.rating, "review": payload.review})
    db.commit()
    logger.info(
        f"REVIEW created — user='{current_user['username']}' course_id={course_id} rating={payload.rating}")
    return dict(result.mappings().first())


@reviews_router.put("/course/{course_id}", response_model=ReviewOut)
def update_review(course_id: int, payload: ReviewCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    logger.info(
        f"REVIEW update — user='{current_user['username']}' course_id={course_id}")
    existing = db.execute(text("SELECT id FROM reviews WHERE course_id=:cid AND user_id=:uid"), {
                          "cid": course_id, "uid": current_user["id"]}).first()
    if not existing:
        logger.warning(
            f"REVIEW update failed — no review found for user='{current_user['username']}' course_id={course_id}")
        raise HTTPException(
            status_code=404, detail="Aapka koi review nahi mila. Pehle submit karein.")
    result = db.execute(text("""
        UPDATE reviews SET rating=:rating, review=:review WHERE course_id=:cid AND user_id=:uid
        RETURNING id, course_id, user_id, username, rating, review, created_at
    """), {"rating": payload.rating, "review": payload.review, "cid": course_id, "uid": current_user["id"]})
    db.commit()
    logger.info(
        f"REVIEW updated — user='{current_user['username']}' course_id={course_id} new_rating={payload.rating}")
    return dict(result.mappings().first())


@reviews_router.delete("/course/{course_id}")
def delete_review(course_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    logger.info(
        f"REVIEW delete — user='{current_user['username']}' course_id={course_id}")
    existing = db.execute(text("SELECT id FROM reviews WHERE course_id=:cid AND user_id=:uid"), {
                          "cid": course_id, "uid": current_user["id"]}).first()
    if not existing:
        logger.warning(
            f"REVIEW delete failed — not found for user='{current_user['username']}' course_id={course_id}")
        raise HTTPException(status_code=404, detail="Review nahi mila")
    db.execute(text("DELETE FROM reviews WHERE course_id=:cid AND user_id=:uid"), {
               "cid": course_id, "uid": current_user["id"]})
    db.commit()
    logger.info(
        f"REVIEW deleted — user='{current_user['username']}' course_id={course_id}")
    return {"message": f"Course #{course_id} ka review delete ho gaya ✅"}


@reviews_router.get("/course/{course_id}")
def get_course_reviews(course_id: int, db: Session = Depends(get_db)):
    course = db.execute(text("SELECT id, title FROM courses WHERE id=:id"), {
                        "id": course_id}).mappings().first()
    if not course:
        logger.warning(f"GET reviews — course_id={course_id} not found")
        raise HTTPException(status_code=404, detail="Course nahi mila")
    reviews = db.execute(text("SELECT id,course_id,user_id,username,rating,review,created_at FROM reviews WHERE course_id=:cid ORDER BY created_at DESC"), {
                         "cid": course_id}).mappings().all()
    stats = db.execute(text("""
        SELECT COUNT(*) AS total_reviews, ROUND(AVG(rating)::numeric,2) AS avg_rating,
        COUNT(CASE WHEN rating=5 THEN 1 END) AS five_star, COUNT(CASE WHEN rating=4 THEN 1 END) AS four_star,
        COUNT(CASE WHEN rating=3 THEN 1 END) AS three_star, COUNT(CASE WHEN rating=2 THEN 1 END) AS two_star,
        COUNT(CASE WHEN rating=1 THEN 1 END) AS one_star FROM reviews WHERE course_id=:cid
    """), {"cid": course_id}).mappings().first()
    logger.debug(
        f"GET reviews course_id={course_id} — {stats['total_reviews']} reviews, avg={stats['avg_rating']}")
    return {"course_id": course_id, "course_title": course["title"], "stats": dict(stats), "reviews": [dict(r) for r in reviews]}


@reviews_router.get("/my/course/{course_id}")
def get_my_review(course_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    review = db.execute(text("SELECT id,course_id,user_id,username,rating,review,created_at FROM reviews WHERE course_id=:cid AND user_id=:uid"), {
                        "cid": course_id, "uid": current_user["id"]}).mappings().first()
    return {"has_review": bool(review), "review": dict(review) if review else None}


@reviews_router.get("/my/all")
def get_my_all_reviews(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    reviews = db.execute(text("""
        SELECT r.id,r.course_id,c.title AS course_title,r.rating,r.review,r.created_at
        FROM reviews r JOIN courses c ON c.id=r.course_id WHERE r.user_id=:uid ORDER BY r.created_at DESC
    """), {"uid": current_user["id"]}).mappings().all()
    logger.debug(
        f"GET my reviews — user='{current_user['username']}' total={len(reviews)}")
    return {"username": current_user["username"], "total_reviews": len(reviews), "reviews": [dict(r) for r in reviews]}


@reviews_router.get("/top-rated")
def top_rated_courses(db: Session = Depends(get_db)):
    results = db.execute(text("""
        SELECT c.id,c.title,c.instructor,c.category,c.price,c.is_published,
        COUNT(r.id) AS total_reviews, ROUND(AVG(r.rating)::numeric,2) AS avg_rating
        FROM courses c JOIN reviews r ON r.course_id=c.id
        GROUP BY c.id,c.title,c.instructor,c.category,c.price,c.is_published
        HAVING COUNT(r.id)>=1 ORDER BY avg_rating DESC, total_reviews DESC LIMIT 10
    """)).mappings().all()
    logger.info(f"TOP RATED — {len(results)} courses")
    return {"total": len(results), "top_rated": [dict(r) for r in results]}


@reviews_router.delete("/admin/{review_id}")
def admin_delete_review(review_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    logger.warning(
        f"ADMIN DELETE review id={review_id} by admin='{current_user['username']}'")
    existing = db.execute(text("SELECT id FROM reviews WHERE id=:id"), {
                          "id": review_id}).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Review nahi mila")
    db.execute(text("DELETE FROM reviews WHERE id=:id"), {"id": review_id})
    db.commit()
    logger.info(
        f"ADMIN review id={review_id} deleted by '{current_user['username']}'")
    return {"message": f"Review #{review_id} admin ne delete kiya ✅"}
