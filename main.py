from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers.courses import router
from routers.auth_router import auth_router
from routers.analytics_router import analytics_router
from routers.reviews_router import reviews_router
from routers.enrollment_router import enrollment_router    # ✅ Enrollments

app = FastAPI(title="CourseVault API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─── Routers ──────────────────────────────────────────
app.include_router(router)
app.include_router(auth_router)
app.include_router(analytics_router)
app.include_router(reviews_router)
app.include_router(enrollment_router)                      # ✅ Enrollments

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("static/index.html")
