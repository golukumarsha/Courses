from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


# ─── Course Table ─────────────────────────────────────
class CourseDB(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    instructor = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    duration_hours = Column(Integer, nullable=False)
    is_published = Column(Boolean, nullable=False, default=False)
    discount_percent = Column(Float, default=0.0)


# ─── User Table ───────────────────────────────────────
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50),  nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20),  nullable=False, default="user")
    is_active = Column(Boolean, default=True)


# ─── Review Table ─────────────────────────────────────
class ReviewDB(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(50), nullable=False)
    rating = Column(Integer, nullable=False)
    review = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('course_id', 'user_id', name='uq_course_user_review'),
    )


# ─── Enrollment Table ─────────────────────────────────
class EnrollmentDB(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    username = Column(String(50),  nullable=False)
    course_title = Column(String(200), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), nullable=False, default="active")
    # status: "active", "completed", "cancelled"

    __table_args__ = (
        UniqueConstraint('user_id', 'course_id',
                         name='uq_user_course_enrollment'),
    )
