-- ─── CourseVault Initial Database Setup ───────────────
-- Yeh file pehli baar Docker run karne pe automatically chalti hai

-- ─── courses table ────────────────────────────────────
CREATE TABLE IF NOT EXISTS courses (
    id               SERIAL PRIMARY KEY,
    title            VARCHAR(200) NOT NULL,
    instructor       VARCHAR(100) NOT NULL,
    category         VARCHAR(100) NOT NULL,
    price            FLOAT        NOT NULL,
    duration_hours   INTEGER      NOT NULL,
    is_published     BOOLEAN      NOT NULL DEFAULT false,
    discount_percent FLOAT                 DEFAULT 0.0
);

-- ─── users table ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role            VARCHAR(20)  NOT NULL DEFAULT 'user',
    is_active       BOOLEAN               DEFAULT true
);

-- ─── reviews table ────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    id         SERIAL PRIMARY KEY,
    course_id  INTEGER     NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    user_id    INTEGER     NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    username   VARCHAR(50) NOT NULL,
    rating     INTEGER     NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review     TEXT,
    created_at TIMESTAMP            DEFAULT NOW(),
    CONSTRAINT uq_course_user_review UNIQUE (course_id, user_id)
);

-- ─── enrollments table ────────────────────────────────
CREATE TABLE IF NOT EXISTS enrollments (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER      NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    course_id    INTEGER      NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    username     VARCHAR(50)  NOT NULL,
    course_title VARCHAR(200) NOT NULL,
    enrolled_at  TIMESTAMP             DEFAULT NOW(),
    status       VARCHAR(20)  NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active', 'completed', 'cancelled')),
    CONSTRAINT uq_user_course_enrollment UNIQUE (user_id, course_id)
);

-- ─── Indexes ──────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_courses_category    ON courses(category);
CREATE INDEX IF NOT EXISTS idx_courses_published   ON courses(is_published);
CREATE INDEX IF NOT EXISTS idx_reviews_course      ON reviews(course_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user        ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_user    ON enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course  ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status  ON enrollments(status);

-- ─── Sample Data (optional) ───────────────────────────
INSERT INTO courses (title, instructor, category, price, duration_hours, is_published, discount_percent)
VALUES
    ('Python For Beginners',         'Aanya Sharma',  'programming',    499.0,  12, true,  10.0),
    ('Fastapi Full Course',          'Rohan Mehta',   'web development', 799.0,  20, true,   0.0),
    ('Data Structures & Algorithms', 'Priya Nair',    'computer science', 999.0, 35, true,  15.0),
    ('Machine Learning Basics',      'Karan Joshi',   'data science',   1299.0, 40, true,  20.0),
    ('React.Js Zero To Hero',        'Simran Kaur',   'web development', 849.0, 28, false,  0.0),
    ('Sql And Postgresql Mastery',   'Arjun Pillai',  'databases',       649.0, 18, true,   5.0),
    ('Docker And Kubernetes',        'Neha Gupta',    'devops',         1099.0, 22, true,   0.0),
    ('Ui/Ux Design Fundamentals',    'Vikram Desai',  'design',          599.0, 15, false,  0.0)
ON CONFLICT DO NOTHING;

-- ─── Done ─────────────────────────────────────────────
SELECT 'CourseVault DB initialized!' AS status;