# 🐳 CourseVault — Docker Setup Guide

## 📁 Project Structure
```
CourseVault/
├── Dockerfile
├── docker-compose.yml
├── .env.example          ← copy karke .env banao
├── .dockerignore
├── .gitignore
├── init.sql              ← DB tables auto-create
├── requirements.txt
├── main.py
├── database/
├── models/
├── routers/
├── utils/
├── static/
└── tests/
```

---

## 🚀 Pehli Baar Run Karna

### Step 1 — .env file banao
```bash
copy .env.example .env
```

### Step 2 — Docker Compose se sab start karo
```bash
docker-compose up --build
```

### Step 3 — Browser mein kholein
```
App:   http://localhost:8000
Docs:  http://localhost:8000/docs
```

---

## ⚡ Common Commands

```bash
# Start (background mein)
docker-compose up -d

# Start with logs visible
docker-compose up

# Pehli baar ya code change ke baad
docker-compose up --build

# Band karo
docker-compose down

# Band karo + database bhi hata do (fresh start)
docker-compose down -v

# Logs dekho
docker-compose logs -f app
docker-compose logs -f db

# Container ke andar jaao
docker exec -it coursevault_app bash
docker exec -it coursevault_db psql -U coursevault -d coursevault_db

# Status dekho
docker-compose ps
```

---

## 🔧 Environment Variables (.env)

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_USER` | coursevault | DB username |
| `POSTGRES_PASSWORD` | coursevault123 | DB password |
| `POSTGRES_DB` | coursevault_db | DB name |
| `DATABASE_URL` | auto | Full connection string |
| `SECRET_KEY` | change-this! | JWT secret |

---

## 🐛 Troubleshooting

### Port already in use
```bash
# 8000 port band karo
netstat -ano | findstr :8000   # Windows
lsof -i :8000                  # Mac/Linux
```

### Database connect nahi ho raha
```bash
docker-compose logs db
docker-compose restart db
```

### Fresh start chahiye
```bash
docker-compose down -v
docker-compose up --build
```