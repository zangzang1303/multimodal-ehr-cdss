"""
Canonical Data Pipeline Rebuilder
M-CDSS Phase 3 / Backlog 08 (Member 2 task, corrected during Member 1 review 2026-11-23)

Rebuilds ``data/processed_rebuilt_strict/`` with the ORIGINAL Phase 1 strict pipeline
(``process_and_save_patient_splits``) applied to ``data/raw_rebuilt/`` and the improved
Phase 3 de-identifier. This keeps every ``patient_id`` in the same split as the
2026-10-28 strict benchmark and only changes the de-identified note text.

Why this replaces the previous version of this script
-----------------------------------------------------
The 2026-11-18 version read the legacy ``data/raw/`` export (no target-diagnosis
redaction, MTSamples bodies reused across patients), relabelled patients to force
500 cases per class, and re-randomised the split while hashing note groups per
patient. On that output a TF-IDF model with every number masked reached macro AUROC
0.962 and 42% of test note bodies appeared verbatim in train, i.e. the Phase 1
leakage controls were silently undone. See CHANGELOG.md (2026-11-23).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.audit_data_leakage import audit  # noqa: E402
from src.data_pipeline.dataset_loader import process_and_save_patient_splits  # noqa: E402
from src.data_pipeline.manifest import generate_manifest, verify_manifest  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = ROOT_DIR / "data" / "raw_rebuilt"
CANONICAL_DIR = ROOT_DIR / "data" / "processed_rebuilt_strict"
EXPECTED_ROWS = {"train": 1425, "val": 273, "test": 302}


def rebuild_canonical_dataset(raw_dir: Path = RAW_DIR, output_dir: Path = CANONICAL_DIR,
                              seed: int = 42, write_manifest: bool = True) -> dict:
    logger.info("Rebuilding canonical strict split from %s", raw_dir)
    train_df, val_df, test_df = process_and_save_patient_splits(
        raw_data_dir=raw_dir, processed_data_dir=output_dir, seed=seed)
    rows = {"train": len(train_df), "val": len(val_df), "test": len(test_df)}
    if rows != EXPECTED_ROWS:
        raise RuntimeError(f"Strict split row counts changed: {rows} != {EXPECTED_ROWS}")

    report = audit(output_dir)
    (ROOT_DIR / "data" / "rebuilt_strict_split_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if not report["passed"]:
        raise RuntimeError(f"Leakage audit failed: {report['failures']}")

    if write_manifest:
        generate_manifest(data_dir=output_dir,
                          reproduce_command="python scripts/rebuild_canonical_dataset.py")
        verify_manifest(output_dir)
    logger.info("[OK] Canonical dataset rebuilt, audited and manifested: %s", rows)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=CANONICAL_DIR)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-manifest", action="store_true",
                        help="Do not overwrite data/DATA_MANIFEST.json (for dry runs)")
    args = parser.parse_args()
    rebuild_canonical_dataset(args.raw_dir, args.output_dir, args.seed, not args.no_manifest)


if __name__ == "__main__":
    main()
