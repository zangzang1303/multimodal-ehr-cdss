"""
Modular API Router Package
"""

from fastapi import APIRouter
from src.api.routes.inference import router as inference_router

router = APIRouter()
router.include_router(inference_router, tags=["Inference"])
