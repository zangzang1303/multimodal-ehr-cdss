"""
Modular API Router Package
"""

from fastapi import APIRouter
from src.api.routes.inference import router as inference_router
from src.api.routes.benchmarks import router as benchmarks_router

router = APIRouter()
router.include_router(inference_router, tags=["Inference"])
router.include_router(benchmarks_router, tags=["Benchmarks"])
