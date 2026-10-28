"""Audit processed train/validation/test splits before model training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def audit(data_dir: Path) -> dict:
    frames = {name: pd.read_parquet(data_dir / f"{name}.parquet") for name in ("train", "val", "test")}
    report = {"rows": {name: len(frame) for name, frame in frames.items()}, "overlap": {}}
    failures = []
    for column in ("patient_id", "source_patient_group", "source_note_group"):
        if any(column not in frame for frame in frames.values()):
            report["overlap"][column] = "missing"
            failures.append(f"missing {column}")
            continue
        values = {name: set(frame[column].dropna().astype(str)) for name, frame in frames.items()}
        counts = {
            "train_val": len(values["train"] & values["val"]),
            "train_test": len(values["train"] & values["test"]),
            "val_test": len(values["val"] & values["test"]),
        }
        report["overlap"][column] = counts
        if any(counts.values()):
            failures.append(f"{column} crosses split boundaries")
    report["class_counts"] = {
        name: frame["diagnosis_label"].value_counts().sort_index().to_dict()
        for name, frame in frames.items()
    }
    expected_classes = {0, 1, 2, 3}
    for name, counts in report["class_counts"].items():
        missing_classes = sorted(expected_classes - {int(label) for label in counts})
        if missing_classes:
            failures.append(f"{name} is missing target classes {missing_classes}")
    report["passed"] = not failures
    report["failures"] = failures
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.data_dir)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
