"""Guarded checkpoint writing (Phase 3 / Backlog 08 – M1 task 1.2).

``data/checkpoints/multimodal_best.pt`` was overwritten on 2026-11-05 by an
``--eval-only`` run that re-saved the file with ``epochs_total = 0``. This module
refuses such writes and stamps provenance (backbone revision, data manifest hash,
git commit) into every checkpoint that is saved.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[2]


class UnsafeCheckpointWrite(RuntimeError):
    """Raised when a run that did not train a model tries to save a checkpoint."""


def manifest_digest(manifest_path: Path = ROOT / "data" / "DATA_MANIFEST.json") -> str | None:
    if not manifest_path.is_file():
        return None
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    canonical = json.dumps(payload.get("splits", {}), sort_keys=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def save_checkpoint_safely(payload: dict[str, Any], path: Path, *, epochs_trained: int,
                           eval_only: bool = False, smoke_test: bool = False) -> Path:
    """Write ``payload`` to ``path`` only if this run actually trained a model.

    Smoke tests are redirected to ``<name>.smoke.pt`` so they can never replace the
    research checkpoint.
    """
    if eval_only or epochs_trained <= 0:
        raise UnsafeCheckpointWrite(
            f"Refusing to write {path}: run trained {epochs_trained} epochs (eval_only={eval_only}).")
    if smoke_test:
        path = path.with_name(path.stem + ".smoke" + path.suffix)
    payload = dict(payload)
    provenance = dict(payload.get("provenance", {}))
    provenance.setdefault("data_manifest_sha256", manifest_digest())
    provenance.setdefault("git_commit", git_commit())
    payload["provenance"] = provenance
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, tmp)
    tmp.replace(path)
    return path
