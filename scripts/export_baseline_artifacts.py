"""Copy the seed-42 RQ1 baseline models into data/checkpoints/baselines/ with a manifest
so POST /api/v1/predict/baseline can serve fitted models (never heuristics)."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RUNS = ROOT / "data" / "checkpoints" / "runs"
OUT = ROOT / "data" / "checkpoints" / "baselines"
PRED = ROOT / "data" / "predictions" / "rq1"


def main() -> None:
    import torch

    OUT.mkdir(parents=True, exist_ok=True)
    deploy = torch.load(ROOT / "data" / "checkpoints" / "multimodal_best.pt", map_location="cpu", weights_only=True)
    files = {"classical_tabular": ("catboost_seed42.joblib", "catboost"),
             "tabular_deep": ("ft_transformer_seed42.pt", "ft_transformer"),
             "text_only": ("bert_ft_seed42.pt", "bert_ft")}
    manifest = {"source": "scripts/run_research_experiments.py rq1, seed 42 (data/processed_rebuilt_strict)",
                "preprocessing": deploy["preprocessing"]}
    for key, (name, model) in files.items():
        shutil.copy2(RUNS / name, OUT / name)
        temperature = float(np.load(PRED / f"{model}_seed42.npz")["temperature"])
        manifest[key] = {"file": name, "model": model, "temperature": temperature,
                         "sha256": hashlib.sha256((OUT / name).read_bytes()).hexdigest()}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "preprocessing"}, indent=2))


if __name__ == "__main__":
    main()
