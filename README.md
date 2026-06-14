# 🎓 CourseVault API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

**A full-featured REST API for managing online courses, users, enrollments, reviews & analytics.**

[Live Demo](#) • [API Docs](#api-documentation) • [Quick Start](#-quick-start)

</div>

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [Docker Setup](#-docker-setup)
- [Deployment on Render](#-deployment-on-render)
- [Rate Limiting](#-rate-limiting)
- [Logging System](#-logging-system)

---

## 📖 About the Project

**CourseVault API** ek complete backend system hai jo online course platform ke liye banaya gaya hai. Isme course management, user authentication (JWT), enrollment system, review system aur analytics sab kuch included hai.

Yeh project **FastAPI + PostgreSQL + SQLAlchemy** ke saath build kiya gaya hai aur **Render** pe deploy hua hai. Ek static frontend bhi included hai jo seedha `/` route pe serve hota hai.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **JWT Authentication** | Register, Login, Token-based auth (Admin & User roles) |
| 📚 **Course Management** | Create, Read, Update, Delete, Filter, Sort, Search courses |
| 🎓 **Enrollment System** | Enroll, Cancel, Status update, Top courses |
| ⭐ **Review System** | Add, Edit, Delete reviews with ratings per course |
| 📊 **Analytics Dashboard** | Revenue, avg price, top instructors, popular categories |
| 🚦 **Rate Limiting** | IP-based rate limiting middleware |
| 📁 **Advanced Logging** | Access logs, error logs, app logs in `./logs/` folder |
| 🐳 **Docker Support** | Full `docker-compose` setup with PostgreSQL |
| 🌐 **Static Frontend** | HTML/CSS/JS frontend served from `/` |
| ☁️ **Render Deployment** | Production-ready deployment on Render |

---

## 🛠 Tech Stack

```
Backend     →  FastAPI 0.110 + Uvicorn
Database    →  PostgreSQL 15 + SQLAlchemy 2.0
Auth        →  JWT (python-jose) + bcrypt (passlib)
Validation  →  Pydantic v2
Deployment  →  Render (Cloud) + Docker
Logging     →  Python logging (file + console)
Testing     →  Pytest + HTTPX
```

---

## 📁 Project Structure

```
Course_API/
│
├── main.py                    # FastAPI app entry point, middlewares, routers
│
├── database/
│   ├── connection.py          # SQLAlchemy engine, session, get_db dependency
│   ├── db_model.py            # Database table models (ORM)
│   └── __init__.py
│
├── routers/
│   ├── courses.py             # Course CRUD endpoints
│   ├── auth_router.py         # Register / Login / Me
│   ├── enrollment_router.py   # Enrollment endpoints
│   ├── reviews_router.py      # Review endpoints
│   └── analytics_router.py    # Analytics endpoints
│
├── models/
│   ├── course_model.py        # Pydantic schemas for courses
│   ├── auth_model.py          # Pydantic schemas for auth
│   ├── enrollment_model.py    # Pydantic schemas for enrollment
│   └── review_model.py        # Pydantic schemas for reviews
│
├── utils/
│   ├── auth.py                # JWT helpers, password hashing, dependencies
│   ├── logger.py              # Logging setup (app + access logger)
│   ├── rate_limiter.py        # IP-based rate limiting middleware
│   └── helpers.py
│
├── static/
│   ├── index.html             # Frontend HTML
│   ├── style.css              # Styles
│   └── script.js              # Frontend JS
│
├── tests/
│   ├── conftest.py
│   ├── test_courses.py
│   ├── test_auth.py
│   ├── test_enrollments.py
│   ├── test_reviews.py
│   ├── test_analytics.py
│   └── test_validation.py
│
├── logs/
│   ├── app.log                # Application logs
│   ├── access.log             # Request/Response logs
│   └── error.log              # Error logs
│
├── .env                       # Environment variables (git ignored)
├── .env.example               # Example env file
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image config
├── docker-compose.yml         # Docker Compose (app + db)
├── init.sql                   # Initial SQL setup
└── runtime.txt                # Python version for Render
```

---

## 🗄 Database Schema

### `courses` Table
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-increment ID |
| `title` | String(200) | Course title |
| `instructor` | String(100) | Instructor name |
| `category` | String(100) | Course category |
| `price` | Float | Course price |
| `duration_hours` | Integer | Duration in hours |
| `is_published` | Boolean | Published status |
| `discount_percent` | Float | Discount % (default 0.0) |

### `users` Table
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-increment ID |
| `username` | String(50) UNIQUE | Username |
| `email` | String(100) UNIQUE | Email address |
| `hashed_password` | String(255) | bcrypt hashed password |
| `role` | String(20) | `user` or `admin` |
| `is_active` | Boolean | Account status |

### `reviews` Table
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-increment ID |
| `course_id` | Integer | FK → courses.id |
| `user_id` | Integer | FK → users.id |
| `username` | String(50) | Reviewer username |
| `rating` | Integer | Rating (1–5) |
| `review` | Text | Review text |
| `created_at` | DateTime | Auto timestamp |

> **Constraint:** Ek user ek course ko sirf ek hi baar review kar sakta hai.

### `enrollments` Table
| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-increment ID |
| `user_id` | Integer | FK → users.id |
| `course_id` | Integer | FK → courses.id |
| `username` | String(50) | User's username |
| `course_title` | String(200) | Course title snapshot |
| `enrolled_at` | DateTime | Enrollment timestamp |
| `status` | String(20) | `active` / `completed` / `cancelled` |

> **Constraint:** Ek user ek course mein sirf ek baar enroll ho sakta hai.

---

## 📡 API Endpoints

### 🔐 Authentication — `/auth`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | New user register karo |
| `POST` | `/auth/login` | ❌ | Login karo, JWT token milega |
| `GET` | `/auth/me` | ✅ User | Apni profile dekho |

---

### 📚 Courses — `/courses`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/courses` | ❌ | Saare courses list |
| `GET` | `/course/{id}` | ❌ | ID se course fetch karo |
| `GET` | `/filter` | ❌ | Category, price, duration se filter |
| `GET` | `/sort` | ❌ | Sort by price/title/instructor etc. |
| `GET` | `/search` | ❌ | Title/instructor mein search |
| `GET` | `/items` | ❌ | Pagination ke saath courses |
| `POST` | `/create` | ✅ Admin | Naya course create karo |
| `PUT` | `/update/{id}` | ✅ Admin | Course update karo |
| `DELETE` | `/delete/{id}` | ✅ Admin | Course delete karo |

---

### 🎓 Enrollments — `/enrollments`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/enroll/{course_id}` | ✅ User | Course mein enroll karo |
| `DELETE` | `/cancel/{course_id}` | ✅ User | Enrollment cancel karo |
| `PUT` | `/status/{course_id}` | ✅ User | Status update karo |
| `GET` | `/my` | ✅ User | Apne enrollments dekho |
| `GET` | `/course/{course_id}` | ✅ Admin | Course ke sab enrolled users |
| `GET` | `/all` | ✅ Admin | Saare enrollments (admin) |
| `GET` | `/top-courses` | ❌ | Sabse popular courses |

---

### ⭐ Reviews — `/reviews`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/course/{course_id}` | ✅ User | Review add karo |
| `PUT` | `/course/{course_id}` | ✅ User | Apna review edit karo |
| `DELETE` | `/course/{course_id}` | ✅ User | Apna review delete karo |
| `GET` | `/course/{course_id}` | ❌ | Course ki saari reviews |
| `GET` | `/my/course/{course_id}` | ✅ User | Apna review for a course |
| `GET` | `/my/all` | ✅ User | Meri saari reviews |
| `GET` | `/top-rated` | ❌ | Top rated courses |
| `DELETE` | `/admin/{review_id}` | ✅ Admin | Admin: koi bhi review delete |

---

### 📊 Analytics — `/analytics`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/analytics/popular-category` | ❌ | Sabse popular category |
| `GET` | `/analytics/avg-price` | ❌ | Category-wise average price |
| `GET` | `/analytics/revenue` | ❌ | Gross & net revenue |
| `GET` | `/analytics/top-instructors` | ❌ | Top instructors by course count |

---

### 🔧 Admin & System

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/admin/rate-limit-status` | ❌ | Active clients ki rate limit status |
| `GET` | `/home` | ❌ | API health check |
| `GET` | `/` | ❌ | Frontend serve karta hai |
| `GET` | `/docs` | ❌ | Swagger UI (Auto-generated) |
| `GET` | `/redoc` | ❌ | ReDoc documentation |

---

## 🚀 Quick Start

### Option 1 — Local Setup (Python)

```bash
# 1. Repository clone karo
git clone https://github.com/your-username/CourseVault-API.git
cd CourseVault-API

# 2. Virtual environment banao
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Dependencies install karo
pip install -r requirements.txt

# 4. .env file banao
cp .env.example .env
# Apna DATABASE_URL aur SECRET_KEY daalo .env mein

# 5. Server start karo
uvicorn main:app --reload
```

> 🌐 App: http://127.0.0.1:8000  
> 📄 Docs: http://127.0.0.1:8000/docs

---

### Option 2 — Docker Setup

```bash
# .env file banao pehle
cp .env.example .env

# Docker Compose se start karo (app + PostgreSQL dono)
docker-compose up --build

# Background mein chalana ho to
docker-compose up -d --build
```

> App automatically `http://localhost:8000` pe available hoga

---

## 🔑 Environment Variables

`.env` file mein yeh variables daalne hain:

```env
# ─── Database ──────────────────────────────────────────
# Local development ke liye (External URL use karo Render ka)
DATABASE_URL="postgresql://user:password@host/dbname"

# ─── JWT Secret ────────────────────────────────────────
SECRET_KEY=your-super-secret-key-yahan-daalo

# ─── Local PostgreSQL (Docker use karne ke liye) ───────
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=courses
```

> ⚠️ **Important:** `.env` file ko kabhi bhi GitHub pe push mat karo!  
> `.gitignore` mein already add hai.

---

## 🐳 Docker Setup

Project mein full Docker support hai:

```yaml
Services:
  - coursevault_db   → PostgreSQL 15 (port 5432)
  - coursevault_app  → FastAPI App   (port 8000)
```

**Useful Docker Commands:**

```bash
# Start
docker-compose up -d --build

# Logs dekhna
docker-compose logs -f app

# Stop karna
docker-compose down

# Database bhi delete karna ho to
docker-compose down -v
```

---

## ☁️ Deployment on Render

Yeh project **Render** pe deployed hai. Render pe deploy karne ke steps:

### Step 1 — PostgreSQL Database banao Render pe
- Render Dashboard → **New PostgreSQL**
- Database ban jayega, 2 URLs milenge:
  - **Internal URL** → Render app ke liye
  - **External URL** → Local development ke liye

### Step 2 — Web Service banao
- Render Dashboard → **New Web Service**
- GitHub repo connect karo
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3 — Environment Variables set karo
Render ke **Environment** tab mein:

```
DATABASE_URL  =  (Internal Database URL from Step 1)
SECRET_KEY    =  (koi bhi random strong string)
```

### ⚠️ Local vs Render DATABASE_URL

| Environment | URL Type |
|---|---|
| **Local PC** | External Database URL (`.oregon-postgres.render.com` wala) |
| **Render Deploy** | Internal Database URL (`dpg-...` wala, without domain) |

---

## 🚦 Rate Limiting

API mein **IP-based rate limiting** implement ki gayi hai:

- Ek IP se zyada requests aane par `429 Too Many Requests` error milega
- Admin monitoring ke liye `/admin/rate-limit-status` endpoint available hai

---

## 📁 Logging System

Project mein 3 alag log files hain (`./logs/` folder mein):

| File | Description |
|---|---|
| `app.log` | Application events, startup, errors |
| `access.log` | Har request/response ka record (method, path, status, time) |
| `error.log` | Sirf errors aur warnings |

**Log Features:**
- Slow requests (>1000ms) automatically warn karta hai 🐢
- Har request ka unique `req_id` hota hai tracking ke liye
- Startup pe saare routers ka status log hota hai

---

## 🧪 Testing

```bash
# Saare tests run karo
pytest

# Specific file test karo
pytest tests/test_courses.py -v

# Coverage ke saath
pytest --tb=short -v
```

Test files cover karte hain:
- `test_auth.py` — Register, Login, Token validation
- `test_courses.py` — CRUD, Filter, Sort, Search
- `test_enrollments.py` — Enroll, Cancel, Status
- `test_reviews.py` — Add, Edit, Delete reviews
- `test_analytics.py` — Analytics endpoints
- `test_validation.py` — Input validation edge cases

---

## 👨‍💻 Author

**Golu Kumar**  
🔗 [GitHub](https://github.com/your-username)

---

## 📄 License

This project is for educational and personal use.

---

<div align="center">

Made with ❤️ using FastAPI + PostgreSQL

</div>