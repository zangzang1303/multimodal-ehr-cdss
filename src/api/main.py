"""
Main FastAPI Application Entrypoint
Multimodal Clinical Decision Support System (M-CDSS) - Phase 1
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: load resources, models, etc.
    yield
    # Shutdown logic: cleanup


app = FastAPI(
    title="Multimodal EHR CDSS API",
    description="Multimodal Clinical Decision Support System - Phase 1: Baselines & Research Benchmark",
    version="1.0.0-phase1",
    lifespan=lifespan,
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modular API routers
app.include_router(api_router, prefix="/api/v1")


@app.options("/health", tags=["System"])
async def health_options():
    """CORS / Direct OPTIONS handler for health endpoint."""
    return {"status": "ok"}


@app.get("/health", tags=["System"])
async def health_check():
    """
    System Health Check Endpoint
    Returns system status, version, and current UTC timestamp.
    """
    return {
        "status": "healthy",
        "version": "1.0.0-phase1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
