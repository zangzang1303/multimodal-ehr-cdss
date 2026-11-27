"""
Data Provenance & Manifest Verification Module
M-CDSS Phase 3 / Backlog 08 - Task 2.1 (Member 2: Biomedical Data Engineer & Privacy)

Enforces 'One Source of Truth' across the entire research lifecycle:
- Computes and verifies SHA-256 checksums, sample counts, and class distributions.
- Every training and evaluation script calls `verify_manifest()` as the first line of execution.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = ROOT_DIR / "data" / "DATA_MANIFEST.json"
DEFAULT_CANONICAL_DIR = ROOT_DIR / "data" / "processed_rebuilt_strict"


def compute_sha256(file_path: Union[str, Path]) -> str:
    """Computes SHA-256 hash of a file."""
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found for hashing: {p}")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_content_sha256(df: pd.DataFrame) -> str:
    """Serialisation-independent hash of a split (column names, dtypes as text, values).

    Parquet bytes differ across pyarrow versions even for identical data, so the
    file SHA-256 alone cannot be checked on a teammate's machine. This hash is
    computed from the row-ordered values and is what verify_manifest() requires.
    """
    h = hashlib.sha256()
    h.update("|".join(map(str, df.columns)).encode("utf-8"))
    h.update(pd.util.hash_pandas_object(df.astype(str), index=False).values.tobytes())
    return h.hexdigest()


def generate_manifest(
    data_dir: Union[str, Path] = DEFAULT_CANONICAL_DIR,
    output_path: Union[str, Path] = DEFAULT_MANIFEST_PATH,
    commit_hash: Optional[str] = None,
    reproduce_command: str = "python scripts/reproduce_all.py",
) -> Dict[str, Any]:
    """Generates the canonical data manifest dictionary and writes DATA_MANIFEST.json."""
    data_path = Path(data_dir)
    manifest = {
        "manifest_version": "1.1.0",
        "canonical_data_dir": str(data_path.relative_to(ROOT_DIR) if data_path.is_relative_to(ROOT_DIR) else data_path).replace("\\", "/"),
        "recreation_command": reproduce_command,
        "commit": commit_hash or "HEAD",
        "description": "Canonical preprocessed multimodal EHR dataset with strict patient-level splitting and full de-identification.",
        "splits": {},
    }

    for split_name in ["train", "val", "test"]:
        parquet_file = data_path / f"{split_name}.parquet"
        if not parquet_file.exists():
            raise FileNotFoundError(f"Missing required split file: {parquet_file}")

        sha256 = compute_sha256(parquet_file)
        df = pd.read_parquet(parquet_file)
        row_count = len(df)
        class_dist = df["diagnosis_label"].value_counts().sort_index().to_dict()
        class_dist_formatted = {str(k): int(v) for k, v in class_dist.items()}

        rel_file_path = str(parquet_file.relative_to(ROOT_DIR)).replace("\\", "/")

        manifest["splits"][split_name] = {
            "path": rel_file_path,
            "sha256": sha256,
            "content_sha256": compute_content_sha256(df),
            "row_count": row_count,
            "class_distribution": class_dist_formatted,
            "features_count": len(df.columns),
        }

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info("Generated canonical DATA_MANIFEST.json at: %s", out_p)
    return manifest


def verify_manifest(
    data_dir: Optional[Union[str, Path]] = None,
    manifest_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Verifies that the dataset on disk matches the canonical DATA_MANIFEST.json.
    Halts execution by raising RuntimeError if:
    1. The manifest file does not exist.
    2. Any split file is missing.
    3. Any file SHA-256 hash does not match.
    4. Row count or class distribution does not match.
    """
    m_path = Path(manifest_path) if manifest_path else DEFAULT_MANIFEST_PATH
    if not m_path.exists():
        raise RuntimeError(
            f"[CRITICAL DATA INTEGRITY ERROR] Data manifest file not found: {m_path}.\n"
            f"Run data pipeline or restore canonical dataset before training/evaluating."
        )

    with open(m_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    d_dir = Path(data_dir) if data_dir else ROOT_DIR / manifest.get("canonical_data_dir", "data/processed_rebuilt_strict")

    failures = []
    splits = manifest.get("splits", {})
    if not splits:
        raise RuntimeError("DATA_MANIFEST.json has no 'splits' section.")

    for split_name, expected in splits.items():
        parquet_file = d_dir / f"{split_name}.parquet"
        if not parquet_file.exists():
            failures.append(f"Split file missing: {parquet_file}")
            continue

        # 1. SHA-256 verification
        actual_sha = compute_sha256(parquet_file)
        expected_content = expected.get("content_sha256")
        if expected_content:
            actual_content = compute_content_sha256(pd.read_parquet(parquet_file))
            if actual_content != expected_content:
                failures.append(
                    f"Content checksum mismatch for {split_name}.parquet: "
                    f"expected {expected_content[:16]}..., got {actual_content[:16]}..."
                )
            elif actual_sha != expected["sha256"]:
                logger.warning("%s.parquet: file bytes differ but content hash matches "
                               "(different pyarrow serialisation)", split_name)
        elif actual_sha != expected["sha256"]:
            failures.append(
                f"Checksum mismatch for {split_name}.parquet: "
                f"expected {expected['sha256'][:16]}..., got {actual_sha[:16]}..."
            )

        # 2. Row count and class distribution verification
        try:
            df = pd.read_parquet(parquet_file)
            actual_rows = len(df)
            if actual_rows != expected["row_count"]:
                failures.append(
                    f"Row count mismatch for {split_name}.parquet: "
                    f"expected {expected['row_count']}, got {actual_rows}"
                )

            actual_dist = {str(k): int(v) for k, v in df["diagnosis_label"].value_counts().sort_index().to_dict().items()}
            if actual_dist != expected["class_distribution"]:
                failures.append(
                    f"Class distribution mismatch for {split_name}.parquet: "
                    f"expected {expected['class_distribution']}, got {actual_dist}"
                )
        except Exception as e:
            failures.append(f"Failed to read/verify {parquet_file}: {e}")

    if failures:
        error_msg = (
            f"[CRITICAL DATA INTEGRITY VIOLATION]\n"
            f"Dataset at '{d_dir}' failed manifest verification against '{m_path}':\n"
            + "\n".join(f"  - {f}" for f in failures)
            + f"\nExecution aborted to preserve scientific reproducibility."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info("[✓] Data manifest verified successfully: all splits match canonical SHA-256 and distributions.")
    return manifest


if __name__ == "__main__":
    import sys

    target_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CANONICAL_DIR
    try:
        verify_manifest(target_dir)
        print(f"[✓] Manifest verification passed for: {target_dir}")
    except Exception as exc:
        print(f"[x] Verification failed: {exc}")
        sys.exit(1)
