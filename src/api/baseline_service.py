"""Fitted baseline inference for POST /api/v1/predict/baseline (Phase 3, Backlog 08 M1-1.3 / M3-3.2).

Artifacts are produced by ``scripts/run_research_experiments.py rq1`` (seed 42) and
copied to ``data/checkpoints/baselines/`` by ``scripts/export_baseline_artifacts.py``.
When they are absent the endpoint returns HTTP 503 - it never returns heuristic numbers.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASELINE_DIR = Path(os.getenv("MCDSS_BASELINE_DIR", str(ROOT / "data" / "checkpoints" / "baselines")))
CLASSES = ("ASTHMA", "COPD", "HEART_FAILURE", "PNEUMONIA")


def artifacts_available() -> bool:
    return (BASELINE_DIR / "manifest.json").is_file()


@lru_cache(maxsize=1)
def _load():
    import joblib
    import torch

    from src.models.text_tail import TailedModel, load_backbone

    manifest = json.loads((BASELINE_DIR / "manifest.json").read_text(encoding="utf-8"))
    catboost = joblib.load(BASELINE_DIR / manifest["classical_tabular"]["file"])
    ft_payload = torch.load(BASELINE_DIR / manifest["tabular_deep"]["file"], map_location="cpu", weights_only=False)
    ft = TailedModel("tabular", None)
    ft.load_state_dict(ft_payload["state"])
    ft.eval()
    tokenizer, backbone, _ = load_backbone(torch.device("cpu"))
    text_payload = torch.load(BASELINE_DIR / manifest["text_only"]["file"], map_location="cpu", weights_only=False)
    text = TailedModel("text", backbone, trainable_tail=True)
    text.load_state_dict(text_payload["state"])
    text.eval()
    return manifest, catboost, ft, text, tokenizer, backbone


def _tabular_tensors(features: dict, preprocessing: dict):
    import torch

    num = [(float(features[n]) - preprocessing["scaler_mean"][i]) / preprocessing["scaler_scale"][i]
           for i, n in enumerate(preprocessing["numerical_features"])]
    cat = [next((i + 1 for i, v in enumerate(preprocessing["category_values"][n]) if str(features[n]) == str(v)), 0)
           for n in preprocessing["categorical_features"]]
    return torch.tensor([num], dtype=torch.float32), torch.tensor([cat], dtype=torch.long)


def _softmax(logits: np.ndarray, temperature: float) -> np.ndarray:
    z = logits / temperature
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


def predict_baselines(features: dict, deidentified_note: str) -> dict[str, dict]:
    """Return calibrated probabilities from the three fitted baselines."""
    import pandas as pd
    import torch

    manifest, catboost, ft, text, tokenizer, backbone = _load()
    prep = manifest["preprocessing"]
    out = {}
    frame = pd.DataFrame([features])
    cb_probs = catboost.predict_proba(frame)[0]
    out["classical_tabular"] = _softmax(np.log(np.clip(cb_probs, 1e-7, 1)), manifest["classical_tabular"]["temperature"])
    num, cat = _tabular_tensors(features, prep)
    with torch.inference_mode():
        dummy_h, dummy_m = torch.zeros(1, 1, 768), torch.ones(1, 1, dtype=torch.long)
        out["tabular_deep"] = _softmax(ft(num, cat, dummy_h, dummy_m)[0].numpy(), manifest["tabular_deep"]["temperature"])
        if deidentified_note.strip():
            tokens = tokenizer(deidentified_note, truncation=True, max_length=512, return_tensors="pt")
            h11 = backbone(**tokens, output_hidden_states=True).hidden_states[-2]
            logits = text(num, cat, h11, tokens["attention_mask"])[0].numpy()
            out["text_only"] = _softmax(logits, manifest["text_only"]["temperature"])
    return {name: {"probabilities": {c: float(p) for c, p in zip(CLASSES, probs)},
                   "predicted_class": CLASSES[int(np.argmax(probs))], "confidence": float(np.max(probs))}
            for name, probs in out.items()}
