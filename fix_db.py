"""
Run this script ONCE to fix/create all tables.
Command: python fix_db.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

sql = """
-- ─── courses id fix ───────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'courses_id_seq') THEN
        CREATE SEQUENCE courses_id_seq;
    END IF;
    ALTER TABLE courses ALTER COLUMN id SET DEFAULT nextval('courses_id_seq');
    PERFORM setval('courses_id_seq', COALESCE((SELECT MAX(id) FROM courses), 0) + 1, false);
END $$;

-- ─── users id fix ─────────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'users_id_seq') THEN
        CREATE SEQUENCE users_id_seq;
    END IF;
    ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq');
    PERFORM setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 0) + 1, false);
END $$;

-- ─── reviews table ────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    id         SERIAL PRIMARY KEY,
    course_id  INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    username   VARCHAR(50) NOT NULL,
    rating     INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review     TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_course_user_review UNIQUE (course_id, user_id)
);

-- ─── enrollments table ────────────────────────────────
CREATE TABLE IF NOT EXISTS enrollments (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL,
    course_id    INTEGER NOT NULL,
    username     VARCHAR(50)  NOT NULL,
    course_title VARCHAR(200) NOT NULL,
    enrolled_at  TIMESTAMP DEFAULT NOW(),
    status       VARCHAR(20) NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active', 'completed', 'cancelled')),
    CONSTRAINT uq_user_course_enrollment UNIQUE (user_id, course_id)
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_enrollments_user_id   ON enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status    ON enrollments(status);
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()
    print("✅ Saari tables ready hain!")
    print("   - courses   ✅")
    print("   - users     ✅")
    print("   - reviews   ✅")
    print("   - enrollments ✅")
    print("\n🚀 Ab: uvicorn main:app --reload")
