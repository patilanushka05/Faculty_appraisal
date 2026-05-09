from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.exc import SQLAlchemyError
import logging
import time
import os
import traceback
from .api.v1 import router as api_v1_router
from .setup.admin_views import create_admin

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Faculty Appraisal API",
    description="Final Backend API for Faculty Appraisal System",
    version="2.0.0",
)

# Mount Local Storage (for local migration support)
# This allows serving files from the 'uploads' folder via http://backend/uploads/...
if os.path.exists("./uploads"):
    app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")
elif os.getenv("USE_LOCAL_STORAGE", "false").lower() == "true":
    os.makedirs("./uploads", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://dypfacultyappraisal.netlify.app",
    "https://69fd1393a8684b0fbfe337b7--facultyappraisalportal.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

# SessionMiddleware is required by sqladmin for its /admin web UI login flow.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("JWT_SECRET_KEY", "fallback-secret-change-in-production"),
)

def _cors_headers(request: Request) -> dict:
    """Return CORS headers for the request's origin, if it is allowed."""
    origin = request.headers.get("origin", "")
    if origin in ALLOWED_ORIGINS:
        return {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true"}
    return {}

# Logging & Latency Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Request {request.method} {request.url.path} completed in {process_time:.4f}s")
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        # Return JSONResponse instead of re-raising — re-raising inside BaseHTTPMiddleware
        # bypasses CORSMiddleware's response wrapper, making 500 errors appear as CORS errors.
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "type": type(e).__name__, "path": request.url.path},
            headers=_cors_headers(request),
        )

# Exception Handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error on {request.method} {request.url.path}: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred", "error": str(exc), "type": "SQLAlchemyError"},
        headers=_cors_headers(request),
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    error_type = type(exc).__name__
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {error_type}: {error_msg}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": error_msg, "type": error_type, "path": request.url.path},
        headers=_cors_headers(request),
    )

# Include Versioned API
app.include_router(api_v1_router, prefix="/api/v1")

# Mount sqladmin at /admin (login-protected, admin role only)
create_admin(app)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Faculty Appraisal API",
        "status": "online",
        "version": "2.0.0"
    }
