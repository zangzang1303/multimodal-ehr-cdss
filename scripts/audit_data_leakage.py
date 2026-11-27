"""Audit processed train/validation/test splits before model training."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

# Target diagnoses must never appear verbatim in model input (they are replaced by
# [REDACTED_DIAGNOSIS] at conversion time). Threshold allows incidental mentions.
TARGET_TERMS = re.compile(
    r"\b(asthma|status asthmaticus|copd|chronic obstructive|emphysema|"
    r"congestive heart failure|heart failure|chf|pneumonia|bronchopneumonia)\b",
    re.IGNORECASE,
)
MAX_TARGET_TERM_RATE = 0.02
# A reused note body is only leakage when it predicts the label: generic templates
# shared by every class (train-label purity ~0.3) are allowed, reused MTSamples
# narratives that map to one diagnosis (purity >= 0.8) are not.
INFORMATIVE_PURITY = 0.8
MAX_INFORMATIVE_DUPLICATE_RATE = 0.02


def _note_body(text: str) -> str:
    """Note text without redaction tokens and numbers, to detect reused narratives."""
    text = re.sub(r"\[REDACTED_[A-Z]+\]", " ", str(text))
    text = re.sub(r"\d+(?:\.\d+)?", " ", text)
    return " ".join(text.lower().split())


def content_checks(frames: dict[str, pd.DataFrame]) -> tuple[dict, list[str]]:
    """Label-leakage checks on the note text itself (added 2026-11-23)."""
    if any("clinical_note" not in frame for frame in frames.values()):
        return {"skipped": "clinical_note missing"}, []
    failures = []
    term_rate = {name: round(float(frame.clinical_note.astype(str).map(
        lambda text: bool(TARGET_TERMS.search(text))).mean()), 4) for name, frame in frames.items()}
    for name, rate in term_rate.items():
        if rate > MAX_TARGET_TERM_RATE:
            failures.append(f"{name}: {rate:.1%} of notes contain an unredacted target diagnosis")
    train = frames["train"].assign(body=frames["train"].clinical_note.map(_note_body))
    purity = train.groupby("body").diagnosis_label.agg(lambda s: s.value_counts(normalize=True).max())
    informative = set(purity[purity >= INFORMATIVE_PURITY].index)
    duplicates, informative_dup = {}, {}
    for name in ("val", "test"):
        bodies = frames[name].clinical_note.map(_note_body)
        duplicates[name] = round(float(bodies.isin(purity.index).mean()), 4)
        informative_dup[name] = round(float(bodies.isin(informative).mean()), 4)
        if informative_dup[name] > MAX_INFORMATIVE_DUPLICATE_RATE:
            failures.append(f"{name}: {informative_dup[name]:.1%} of notes reuse a label-specific train note body")
    return {"unredacted_target_term_rate": term_rate,
            "note_body_duplicated_from_train_rate": duplicates,
            "label_informative_duplicate_rate": informative_dup}, failures


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
    report["content"], content_failures = content_checks(frames)
    failures.extend(content_failures)
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
