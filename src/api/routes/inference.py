"""
Inference API Endpoints for Baselines
"""

from fastapi import APIRouter

router = APIRouter(prefix="/predict")


@router.get("/status")
async def inference_status():
    """Check inference service status."""
    return {
        "status": "inference_service_ready",
        "supported_baselines": ["classical", "tabular_deep", "text_only"],
    }
