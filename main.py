import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from routers.courses import router
from routers.auth_router import auth_router
from routers.analytics_router import analytics_router
from routers.reviews_router import reviews_router
from routers.enrollment_router import enrollment_router

from utils.logger import get_logger, get_access_logger
from utils.rate_limiter import rate_limit_middleware, get_rate_limit_status

# ─── Loggers ──────────────────────────────────────────
logger = get_logger("main")
access_logger = get_access_logger()


# ─── Lifespan (replaces on_event startup/shutdown) ────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──
    logger.info("🚀 CourseVault API starting up...")
    logger.info("=" * 60)
    logger.info("🎓 CourseVault API — STARTED")
    logger.info("📄 Docs:  http://127.0.0.1:8000/docs")
    logger.info("🌐 App:   http://127.0.0.1:8000/")
    logger.info("📁 Logs:  ./logs/")
    logger.info("🚦 Rate Limiting: ENABLED")
    logger.info("=" * 60)

    yield  # ← App yahan run karta hai

    # ── SHUTDOWN ──
    logger.info("🛑 CourseVault API — SHUTTING DOWN")


# ─── App (sirf ek baar!) ──────────────────────────────
app = FastAPI(title="CourseVault API", version="2.0", lifespan=lifespan)

# ─── CORS ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─── RATE LIMITING MIDDLEWARE ─────────────────────────
app.middleware("http")(rate_limit_middleware)


# ─── REQUEST LOGGING MIDDLEWARE ───────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    req_id = str(uuid.uuid4())[:8]
    start = time.time()
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url.path)
    query = str(request.url.query)
    full_path = url + (f"?{query}" if query else "")

    access_logger.info(
        f"→ REQ  [{req_id}] {method:6} {full_path} | IP: {client_ip}"
    )

    try:
        response = await call_next(request)
    except Exception as exc:
        duration = round((time.time() - start) * 1000, 2)
        logger.error(
            f"← ERR  [{req_id}] {method} {full_path} | "
            f"UNHANDLED: {type(exc).__name__}: {exc} | {duration}ms"
        )
        raise

    duration = round((time.time() - start) * 1000, 2)
    status_code = response.status_code
    level = "info" if status_code < 400 else (
        "warning" if status_code < 500 else "error")

    msg = (
        f"← RES  [{req_id}] {method:6} {full_path} | "
        f"STATUS: {status_code} | {duration}ms"
    )
    getattr(access_logger, level)(msg)

    if duration > 1000:
        logger.warning(
            f"🐢 SLOW REQUEST [{req_id}] {full_path} took {duration}ms")

    return response


# ─── GLOBAL EXCEPTION HANDLERS ────────────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    path = str(request.url.path)
    if exc.status_code == 429:
        logger.warning(f"RATE LIMIT hit on {path}")
        return JSONResponse(
            status_code=429,
            content=exc.detail if isinstance(exc.detail, dict) else {
                "detail": exc.detail},
            headers=dict(exc.headers) if exc.headers else {}
        )
    if exc.status_code >= 500:
        logger.error(f"HTTP {exc.status_code} on {path}: {exc.detail}")
    elif exc.status_code >= 400:
        logger.warning(f"HTTP {exc.status_code} on {path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    path = str(request.url.path)
    errors = exc.errors()
    logger.warning(
        f"VALIDATION ERROR on {path} | "
        f"{len(errors)} error(s): " +
        " | ".join([f"{e['loc']}: {e['msg']}" for e in errors])
    )
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    path = str(request.url.path)
    logger.critical(
        f"UNHANDLED EXCEPTION on {path}: "
        f"{type(exc).__name__}: {exc}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Logs mein dekho."}
    )


# ─── Routers ──────────────────────────────────────────
app.include_router(router)
logger.info("✅ Courses router loaded")

app.include_router(auth_router)
logger.info("✅ Auth router loaded")

app.include_router(analytics_router)
logger.info("✅ Analytics router loaded")

app.include_router(reviews_router)
logger.info("✅ Reviews router loaded")

app.include_router(enrollment_router)
logger.info("✅ Enrollment router loaded")


# ─── Rate Limit Status Endpoint (Admin monitoring) ────
@app.get("/admin/rate-limit-status", tags=["Admin"])
def rate_limit_status():
    """Dekho kaun kitni requests kar raha hai — Admin only"""
    return {
        "message": "Current rate limit status",
        "active_clients": get_rate_limit_status()
    }


# ─── Static files ─────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


# ─── Frontend ─────────────────────────────────────────
@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("static/index.html")
