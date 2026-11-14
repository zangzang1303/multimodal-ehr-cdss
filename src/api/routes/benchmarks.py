# ==============================================================================
# [CHÚ THÍCH MOCK FALLBACK - CHỜ KẾT QUẢ ABLATION STUDY TỪ THÀNH VIÊN 1]
# LƯU Ý: Endpoint /api/v1/benchmarks/baselines trả về kết quả thực nghiệm thật của
# Giai đoạn 1 (data/rebuilt_strict_results_2026-10-28.json). Tuy nhiên, endpoint
# /api/v1/benchmarks/ablation hiện đang đọc tệp data/ablation_results.json chứa
# dữ liệu giả lập (mock) phục vụ hiển thị biểu đồ UI của Thành viên 3 (Backlog 04 -
# Nhiệm vụ 3.3), chờ Thành viên 1 chạy xong 5-Fold Cross-Validation Ablation Study
# thực tế (Backlog 04 - Nhiệm vụ 1.4).
# ==============================================================================
"""
Baseline Benchmarks API Endpoints
Multimodal EHR CDSS - Phase 1 / Backlog 03 (Task 3.2)
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/benchmarks")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
STRICT_JSON_PATH = PROJECT_ROOT / "data" / "rebuilt_strict_results_2026-10-28.json"
BASELINE_JSON_PATH = PROJECT_ROOT / "data" / "baseline_results.json"
ABLATION_JSON_PATH = PROJECT_ROOT / "data" / "ablation_results.json"


@router.options("/baselines")
async def options_baselines():
    """Direct OPTIONS handler for benchmark baselines endpoint."""
    return {"status": "ok"}


@router.get("/baselines")
async def get_baseline_benchmarks():
    """
    Returns baseline model benchmark results from data/rebuilt_strict_results_2026-10-28.json or baseline_results.json.
    Includes validation metadata and calibration warnings.
    """
    target_path = STRICT_JSON_PATH if STRICT_JSON_PATH.exists() else BASELINE_JSON_PATH
    if target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as f:
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


@router.options("/ablation")
async def options_ablation():
    """Direct OPTIONS handler for ablation benchmarks endpoint."""
    return {"status": "ok"}


@router.get("/ablation")
async def get_ablation_benchmarks():
    """
    Returns ablation study benchmark results comparing Tabular-only, Text-only,
    Concat Fusion, and Cross-Attention Fusion from data/ablation_results.json.
    """
    if ABLATION_JSON_PATH.exists():
        try:
            with open(ABLATION_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            # The training pipeline writes the canonical `variants` format.  Keep
            # that artifact intact and adapt it for the evaluation dashboard.
            if "variants" not in data:
                return data
            names = {
                "tabular": ("tabular_only", "FT-Transformer (Tabular-only)", "Structured Tabular"),
                "text": ("text_only", "Frozen Bio_ClinicalBERT (Text-only)", "Clinical notes"),
                "concat": ("concat_fusion", "Concat Late Fusion", "Tabular + text"),
                "cross_attention": (
                    "cross_attention_fusion", "Cross-Attention Gated Fusion", "Tabular + text"
                ),
            }
            tabular_auroc = data["variants"]["tabular"]["test"]["macro_auroc"]
            models = {}
            for variant, (key, name, modality) in names.items():
                metrics = data["variants"][variant]["test"]
                models[key] = {
                    "id": key, "name": name, "modality": modality,
                    **metrics,
                    "net_gain_auroc": metrics["macro_auroc"] - tabular_auroc,
                    "description": "Kết quả trên tập kiểm thử strict split của đợt huấn luyện hiện hành.",
                }
            cross = models["cross_attention_fusion"]
            tabular = models["tabular_only"]
            return {
                "experiment_metadata": {
                    "evaluation_date": data["metadata"]["generated_at"],
                    "test_samples": data["metadata"]["split_rows"]["test"],
                    "num_classes": 4,
                    "split_strategy": "Strict group split",
                    "classes": ["ASTHMA", "COPD", "HEART_FAILURE", "PNEUMONIA"],
                },
                "models": models,
                "key_findings": {
                    "auroc_gain_over_tabular": cross["net_gain_auroc"],
                    "ece_reduction": (
                        f"ECE: {tabular['ece']:.4f} → {cross['ece']:.4f}"
                    ),
                    "best_configuration": max(models.values(), key=lambda m: m["macro_auroc"])["name"],
                    "conclusion": "Kết quả chỉ áp dụng cho tập kiểm thử strict split hiện hành.",
                },
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading ablation_results.json: {str(e)}",
            )

    raise HTTPException(
        status_code=503,
        detail="Ablation results are unavailable. data/ablation_results.json not found.",
    )
