from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .setup.database import engine, Base
from .api.v1 import router as api_v1_router
import time

app = FastAPI(
    title="Faculty Appraisal API",
    description="Final Backend API for Faculty Appraisal System",
    version="2.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Latency Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include Versioned API
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Faculty Appraisal API",
        "status": "online",
        "version": "2.0.0"
    }
