"""
Baseline Benchmarks API Endpoints
Multimodal EHR CDSS - Phase 1 / Backlog 03 (Task 3.2)
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/benchmarks")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BASELINE_JSON_PATH = PROJECT_ROOT / "data" / "baseline_results.json"


@router.options("/baselines")
async def options_baselines():
    """Direct OPTIONS handler for benchmark baselines endpoint."""
    return {"status": "ok"}


@router.get("/baselines")
async def get_baseline_benchmarks():
    """
    Returns baseline model benchmark results from data/baseline_results.json.
    Includes validation metadata and calibration warnings.
    """
    if BASELINE_JSON_PATH.exists():
        try:
            with open(BASELINE_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading baseline_results.json: {str(e)}",
            )

    raise HTTPException(
        status_code=503,
        detail="Baseline results are unavailable. Run scripts/run_baselines.py first.",
    )
