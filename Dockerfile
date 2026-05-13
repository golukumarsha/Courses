# ─── Base Image ───────────────────────────────────────
FROM python:3.11-slim

# ─── Environment Variables ────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# ─── Work Directory ───────────────────────────────────
WORKDIR /app

# ─── System Dependencies ──────────────────────────────
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ─── Install Python Dependencies ──────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─── Copy Project Files ───────────────────────────────
COPY . .

# ─── Create logs directory ────────────────────────────
RUN mkdir -p logs

# ─── Expose Port ──────────────────────────────────────
EXPOSE 8000

# ─── Health Check ─────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/home || exit 1

# ─── Start Command ────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]