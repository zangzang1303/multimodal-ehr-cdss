"""
System Latency Benchmark Script (Backlog 09 - Task 3.4 [CORE], Member 3)

Measures cold-start and 200 warm-request p50/p95/p99/mean latencies (in milliseconds)
for /api/v1/agent/explain, /api/v1/predict/baseline, and /api/v1/predict/multimodal,
along with CPU/RAM/note-length specs.
Writes real metrics to results/latency_report.json and results/registry.json["latency"].
"""

from __future__ import annotations

import json
import os
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi.testclient import TestClient

from src.api.main import app


REPO_ROOT = Path(__file__).resolve().parents[1]

SAMPLE_NOTE = (
    "CHIEF COMPLAINT: Patient presents with progressive dyspnea and nocturnal wheezing.\n"
    "HISTORY OF PRESENT ILLNESS: Reports 5-day worsening shortness of breath, dry cough, and fatigue.\n"
    "PHYSICAL EXAMINATION: BP: 122/78 mmHg, HR: 82 bpm, SpO2: 95%. Lungs show expiratory wheezes.\n"
    "MEDICATIONS: Prescribed inhaler therapy and maintenance controller."
)

SAMPLE_INFER_PAYLOAD = {
    "patient_id": "PT-LATENCY-01",
    "tabular_features": {
        "age": 48,
        "systolic_bp": 122.0,
        "diastolic_bp": 78.0,
        "heart_rate": 82.0,
        "respiratory_rate": 18.0,
        "spo2": 95.0,
        "temperature": 37.0,
        "wbc_count": 7.5,
        "crp": 6.2,
        "gender": "F",
        "smoking_status": "NEVER",
        "history_hypertension": 0,
        "history_diabetes": 0,
    },
    "clinical_notes": SAMPLE_NOTE,
}

SAMPLE_EXPLAIN_PAYLOAD = {
    "patient_id": "PT-LATENCY-01",
    "clinical_notes": SAMPLE_NOTE,
    "target_diagnosis": "ASTHMA",
    "calibrated_probabilities": {
        "ASTHMA": 0.78,
        "COPD": 0.14,
        "HEART_FAILURE": 0.05,
        "PNEUMONIA": 0.03,
    },
}


def percentile(sorted_vals: List[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def benchmark_endpoint(
    client: TestClient,
    path: str,
    payload: Dict[str, Any],
    n_warm: int = 200,
) -> Dict[str, Any]:
    # Cold call
    t0 = time.perf_counter()
    cold_resp = client.post(path, json=payload)
    cold_ms = (time.perf_counter() - t0) * 1000.0

    # 200 warm calls
    warm_times: List[float] = []
    status_codes = set()
    for _ in range(n_warm):
        s0 = time.perf_counter()
        resp = client.post(path, json=payload)
        warm_times.append((time.perf_counter() - s0) * 1000.0)
        status_codes.add(resp.status_code)

    sorted_t = sorted(warm_times)
    return {
        "status_codes_observed": sorted(status_codes),
        "cold_ms": round(cold_ms, 2),
        "mean_ms": round(statistics.mean(sorted_t), 2),
        "p50_ms": round(percentile(sorted_t, 50.0), 2),
        "p95_ms": round(percentile(sorted_t, 95.0), 2),
        "p99_ms": round(percentile(sorted_t, 99.0), 2),
        "cold_status_code": cold_resp.status_code,
    }


def main() -> None:
    client = TestClient(app)
    explain_stats = benchmark_endpoint(
        client, "/api/v1/agent/explain", SAMPLE_EXPLAIN_PAYLOAD, n_warm=200
    )
    baseline_stats = benchmark_endpoint(
        client, "/api/v1/predict/baseline", SAMPLE_INFER_PAYLOAD, n_warm=200
    )

    # Check if /predict/multimodal has HF offline weights available or returns 503
    mm_probe = client.post("/api/v1/predict/multimodal", json=SAMPLE_INFER_PAYLOAD)
    if mm_probe.status_code == 200:
        multimodal_stats = benchmark_endpoint(
            client, "/api/v1/predict/multimodal", SAMPLE_INFER_PAYLOAD, n_warm=200
        )
        multimodal_stats["note"] = "Checkpoint + local Bio_ClinicalBERT inference measured on host CPU."
    else:
        multimodal_stats = benchmark_endpoint(
            client, "/api/v1/predict/multimodal", SAMPLE_INFER_PAYLOAD, n_warm=200
        )
        multimodal_stats["note"] = (
            "HTTP 503 safeguard measured on CPU because local Bio_ClinicalBERT weights are missing from HF cache."
        )

    latency_report = {
        "is_mock": False,
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "device_info": f"{platform.system()} {platform.release()} | {platform.machine()} | CPU ({os.cpu_count()} logical cores)",
        "note_length_chars": len(SAMPLE_NOTE),
        "num_warm_requests": 200,
        "endpoints": {
            "/api/v1/agent/explain": explain_stats,
            "/api/v1/predict/baseline": baseline_stats,
            "/api/v1/predict/multimodal": multimodal_stats,
        },
    }

    results_dir = REPO_ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    report_path = results_dir / "latency_report.json"
    report_path.write_text(json.dumps(latency_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    registry_path = results_dir / "registry.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["latency"] = latency_report
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(latency_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
