from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.connection import get_db

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ─── 1. Most Popular Category ─────────────────────────
@analytics_router.get("/popular-category")
def most_popular_category(db: Session = Depends(get_db)):
    """Sabse zyada courses jis category mein hain"""
    result = db.execute(text("""
        SELECT 
            category,
            COUNT(*) AS total_courses,
            COUNT(CASE WHEN is_published = true THEN 1 END) AS published_courses
        FROM courses
        GROUP BY category
        ORDER BY total_courses DESC
    """)).mappings().all()

    if not result:
        raise HTTPException(status_code=404, detail="Koi data nahi mila")

    return {
        "most_popular": result[0]["category"],
        "total_courses": result[0]["total_courses"],
        "all_categories": [dict(r) for r in result]
    }


# ─── 2. Average Price Per Category ────────────────────
@analytics_router.get("/avg-price")
def average_price_per_category(db: Session = Depends(get_db)):
    """Har category ki average price"""
    result = db.execute(text("""
        SELECT
            category,
            ROUND(AVG(price)::numeric, 2)               AS avg_price,
            ROUND(MIN(price)::numeric, 2)               AS min_price,
            ROUND(MAX(price)::numeric, 2)               AS max_price,
            COUNT(*)                                     AS total_courses
        FROM courses
        GROUP BY category
        ORDER BY avg_price DESC
    """)).mappings().all()

    if not result:
        raise HTTPException(status_code=404, detail="Koi data nahi mila")

    return {
        "total_categories": len(result),
        "data": [dict(r) for r in result]
    }


# ─── 3. Total Revenue Per Category ────────────────────
@analytics_router.get("/revenue")
def total_revenue(db: Session = Depends(get_db)):
    """Har category ka total revenue (price × published courses)"""
    result = db.execute(text("""
        SELECT
            category,
            COUNT(*)                                            AS total_courses,
            COUNT(CASE WHEN is_published = true THEN 1 END)    AS published_courses,
            ROUND(SUM(price)::numeric, 2)                      AS gross_revenue,
            ROUND(
                SUM(price - (price * discount_percent / 100))::numeric
            , 2)                                               AS net_revenue_after_discount
        FROM courses
        GROUP BY category
        ORDER BY net_revenue_after_discount DESC
    """)).mappings().all()

    overall = db.execute(text("""
        SELECT
            ROUND(SUM(price)::numeric, 2)                           AS total_gross,
            ROUND(
                SUM(price - (price * discount_percent / 100))::numeric
            , 2)                                                    AS total_net
        FROM courses
        WHERE is_published = true
    """)).mappings().first()

    if not result:
        raise HTTPException(status_code=404, detail="Koi data nahi mila")

    return {
        "overall_gross_revenue":          overall["total_gross"],
        "overall_net_revenue_after_discount": overall["total_net"],
        "by_category": [dict(r) for r in result]
    }


# ─── 4. Top Instructors ───────────────────────────────
@analytics_router.get("/top-instructors")
def top_instructors(db: Session = Depends(get_db)):
    """Top instructors — courses count, avg price, total revenue ke basis pe"""
    result = db.execute(text("""
        SELECT
            instructor,
            COUNT(*)                                                AS total_courses,
            COUNT(CASE WHEN is_published = true THEN 1 END)        AS published_courses,
            ROUND(AVG(price)::numeric, 2)                          AS avg_price,
            ROUND(SUM(price)::numeric, 2)                          AS gross_revenue,
            ROUND(
                SUM(price - (price * discount_percent / 100))::numeric
            , 2)                                                   AS net_revenue,
            ROUND(AVG(duration_hours)::numeric, 1)                 AS avg_duration_hours
        FROM courses
        GROUP BY instructor
        ORDER BY total_courses DESC, net_revenue DESC
    """)).mappings().all()

    if not result:
        raise HTTPException(status_code=404, detail="Koi data nahi mila")

    return {
        "total_instructors": len(result),
        "top_instructor": result[0]["instructor"],
        "data": [dict(r) for r in result]
    }


# ─── 5. Full Dashboard Summary ────────────────────────
@analytics_router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    """Ek hi endpoint mein poora analytics dashboard"""
    summary = db.execute(text("""
        SELECT
            COUNT(*)                                                AS total_courses,
            COUNT(CASE WHEN is_published = true THEN 1 END)        AS published_courses,
            COUNT(CASE WHEN is_published = false THEN 1 END)       AS unpublished_courses,
            COUNT(DISTINCT category)                               AS total_categories,
            COUNT(DISTINCT instructor)                             AS total_instructors,
            ROUND(AVG(price)::numeric, 2)                          AS avg_price,
            ROUND(MIN(price)::numeric, 2)                          AS min_price,
            ROUND(MAX(price)::numeric, 2)                          AS max_price,
            ROUND(SUM(price)::numeric, 2)                          AS gross_revenue,
            ROUND(
                SUM(price - (price * discount_percent / 100))::numeric
            , 2)                                                   AS net_revenue,
            ROUND(AVG(duration_hours)::numeric, 1)                 AS avg_duration_hours
        FROM courses
    """)).mappings().first()

    top_category = db.execute(text("""
        SELECT category, COUNT(*) AS cnt
        FROM courses
        GROUP BY category
        ORDER BY cnt DESC
        LIMIT 1
    """)).mappings().first()

    top_instructor = db.execute(text("""
        SELECT instructor, COUNT(*) AS cnt
        FROM courses
        GROUP BY instructor
        ORDER BY cnt DESC
        LIMIT 1
    """)).mappings().first()

    return {
        "total_courses":        summary["total_courses"],
        "published_courses":    summary["published_courses"],
        "unpublished_courses":  summary["unpublished_courses"],
        "total_categories":     summary["total_categories"],
        "total_instructors":    summary["total_instructors"],
        "pricing": {
            "avg_price":    summary["avg_price"],
            "min_price":    summary["min_price"],
            "max_price":    summary["max_price"],
        },
        "revenue": {
            "gross_revenue": summary["gross_revenue"],
            "net_revenue":   summary["net_revenue"],
        },
        "avg_duration_hours":   summary["avg_duration_hours"],
        "most_popular_category": top_category["category"] if top_category else None,
        "top_instructor":        top_instructor["instructor"] if top_instructor else None,
    }
