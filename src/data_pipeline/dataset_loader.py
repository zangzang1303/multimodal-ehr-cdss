

from __future__ import annotations

import json
import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
import torch
from torch.utils.data import DataLoader, Dataset

from src.data_pipeline.deidentifier import ClinicalDeidentifier
from src.data_pipeline.imputer import ClinicalImputer
from src.data_pipeline.temporal_aligner import TemporalAligner

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


NUMERICAL_COLS_DEFAULT: List[str] = [
    "age",
    "systolic_bp",
    "diastolic_bp",
    "heart_rate",
    "respiratory_rate",
    "spo2",
    "temperature",
    "wbc_count",
    "crp",
]

CATEGORICAL_COLS_DEFAULT: List[str] = [
    "gender",
    "smoking_status",
    "history_hypertension",
    "history_diabetes",
]

GENDER_MAP = {"M": 0.0, "F": 1.0, "OTHER": 2.0}
SMOKING_MAP = {"NEVER": 0.0, "FORMER": 1.0, "CURRENT": 2.0}


def create_patient_level_splits(
    df: pd.DataFrame,
    patient_col: str = "patient_id",
    target_col: str = "diagnosis_label",
    test_size: float = 0.15,
    val_size: float = 0.15,
    seed: int = 42,
    group_cols: Optional[Sequence[str]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
   
    if patient_col not in df.columns:
        raise ValueError(f"patient_col '{patient_col}' not found in DataFrame.")
    if target_col not in df.columns:
        raise ValueError(f"target_col '{target_col}' not found in DataFrame.")

    total_rows = len(df)
    if total_rows == 0:
        raise ValueError("Cannot split an empty DataFrame.")

    requested_group_cols = list(group_cols or [patient_col])
    missing_group_cols = [col for col in requested_group_cols if col not in df.columns]
    if missing_group_cols:
        raise ValueError(f"group columns not found: {missing_group_cols}")

    parent = list(range(total_rows))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for column in requested_group_cols:
        first_seen: Dict[str, int] = {}
        for index, value in enumerate(df[column]):
            if pd.isna(value) or str(value).strip() == "":
                continue
            key = str(value)
            if key in first_seen:
                union(index, first_seen[key])
            else:
                first_seen[key] = index

    groups = np.asarray([find(index) for index in range(total_rows)])
    n_splits_test = max(2, int(round(1.0 / test_size)))
    sgkf_test = StratifiedGroupKFold(n_splits=n_splits_test, shuffle=True, random_state=seed)

    target_test_count = total_rows * test_size
    best_test_idx = None
    best_diff = float("inf")

    for train_val_fold_idx, test_fold_idx in sgkf_test.split(
        df, y=df[target_col], groups=groups
    ):
        diff = abs(len(test_fold_idx) - target_test_count)
        if diff < best_diff:
            best_diff = diff
            best_test_idx = test_fold_idx

    test_df = df.iloc[best_test_idx].copy().reset_index(drop=True)
    train_val_indices = [i for i in range(total_rows) if i not in set(best_test_idx)]
    train_val_df = df.iloc[train_val_indices].copy().reset_index(drop=True)
    train_val_groups = groups[train_val_indices]

    effective_val_ratio = val_size / (1.0 - (len(test_df) / total_rows))
    n_splits_val = max(2, int(round(1.0 / effective_val_ratio)))
    sgkf_val = StratifiedGroupKFold(n_splits=n_splits_val, shuffle=True, random_state=seed)

    target_val_count = total_rows * val_size
    best_val_idx = None
    best_val_diff = float("inf")

    for train_fold_idx, val_fold_idx in sgkf_val.split(
        train_val_df, y=train_val_df[target_col], groups=train_val_groups
    ):
        diff = abs(len(val_fold_idx) - target_val_count)
        if diff < best_val_diff:
            best_val_diff = diff
            best_val_idx = val_fold_idx

    val_df = train_val_df.iloc[best_val_idx].copy().reset_index(drop=True)
    train_indices = [i for i in range(len(train_val_df)) if i not in set(best_val_idx)]
    train_df = train_val_df.iloc[train_indices].copy().reset_index(drop=True)

    train_patients = set(train_df[patient_col])
    val_patients = set(val_df[patient_col])
    test_patients = set(test_df[patient_col])

    overlap_train_val = train_patients & val_patients
    overlap_train_test = train_patients & test_patients
    overlap_val_test = val_patients & test_patients

    if overlap_train_val or overlap_train_test or overlap_val_test:
        raise RuntimeError(
            f"Patient leakage detected! Overlap sizes: "
            f"Train-Val={len(overlap_train_val)}, "
            f"Train-Test={len(overlap_train_test)}, "
            f"Val-Test={len(overlap_val_test)}"
        )

    for column in requested_group_cols:
        split_values = [set(frame[column].dropna().astype(str)) for frame in (train_df, val_df, test_df)]
        if split_values[0] & split_values[1] or split_values[0] & split_values[2] or split_values[1] & split_values[2]:
            raise RuntimeError(f"Provenance leakage detected for group column: {column}")

    logger.info(
        "Patient-level split completed successfully: "
        "Train=%d (%.1f%%, %d pts), Val=%d (%.1f%%, %d pts), Test=%d (%.1f%%, %d pts)",
        len(train_df),
        100.0 * len(train_df) / total_rows,
        len(train_patients),
        len(val_df),
        100.0 * len(val_df) / total_rows,
        len(val_patients),
        len(test_df),
        100.0 * len(test_df) / total_rows,
        len(test_patients),
    )

    return train_df, val_df, test_df


def _get_default_tokenizer():
    try:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")
        return tokenizer
    except Exception as exc:
        logger.warning(
            "Could not load online HuggingFace tokenizer (%s). Initializing lightweight fallback tokenizer.",
            exc,
        )

        class LightweightClinicalTokenizer:
            def __init__(self, max_length: int = 512):
                self.max_length = max_length
                self.vocab_size = 30522

            def __call__(
                self,
                text: str,
                max_length: Optional[int] = None,
                padding: str = "max_length",
                truncation: bool = True,
                return_tensors: Optional[str] = None,
            ) -> Dict[str, Any]:
                max_len = max_length or self.max_length
                words = str(text).lower().split()
                token_ids = [101] + [abs(hash(w)) % 28000 + 1000 for w in words]
                if truncation and len(token_ids) > max_len - 1:
                    token_ids = token_ids[: max_len - 1]
                token_ids.append(102)

                mask = [1] * len(token_ids)
                if padding == "max_length" and len(token_ids) < max_len:
                    pad_len = max_len - len(token_ids)
                    token_ids.extend([0] * pad_len)
                    mask.extend([0] * pad_len)

                if return_tensors == "pt":
                    return {
                        "input_ids": torch.tensor([token_ids], dtype=torch.int64),
                        "attention_mask": torch.tensor([mask], dtype=torch.int64),
                    }
                return {
                    "input_ids": token_ids,
                    "attention_mask": mask,
                }

        return LightweightClinicalTokenizer()


class MultimodalEHRDataset(Dataset):


    def __init__(
        self,
        df: pd.DataFrame,
        notes_dict: Optional[Dict[str, str]] = None,
        tokenizer: Optional[Any] = None,
        max_length: int = 512,
        numerical_cols: Optional[Sequence[str]] = None,
        categorical_cols: Optional[Sequence[str]] = None,
        scaler: Optional[StandardScaler] = None,
        fit_scaler: bool = False,
        target_col: str = "diagnosis_label",
    ) -> None:
        super().__init__()
        self.df = df.copy().reset_index(drop=True)
        self.notes_dict = notes_dict or {}
        self.max_length = max_length
        self.target_col = target_col

        self.numerical_cols = list(numerical_cols or NUMERICAL_COLS_DEFAULT)
        self.categorical_cols = list(categorical_cols or CATEGORICAL_COLS_DEFAULT)

        if tokenizer is None:
            self.tokenizer = _get_default_tokenizer()
        else:
            self.tokenizer = tokenizer

        self.scaler = scaler
        if fit_scaler or (self.scaler is None):
            self.scaler = StandardScaler()
            available_num = [c for c in self.numerical_cols if c in self.df.columns]
            if available_num:
                self.scaler.fit(self.df[available_num].values)

        self.tabular_features = self._build_tabular_matrix()

    def _build_tabular_matrix(self) -> np.ndarray:
        available_num = [c for c in self.numerical_cols if c in self.df.columns]
        if available_num and self.scaler is not None:
            num_data = self.scaler.transform(self.df[available_num].values)
        else:
            num_data = np.zeros((len(self.df), len(self.numerical_cols)), dtype=np.float32)

        cat_data = np.zeros((len(self.df), len(self.categorical_cols)), dtype=np.float32)
        for j, col in enumerate(self.categorical_cols):
            if col in self.df.columns:
                series = self.df[col]
                if col == "gender":
                    cat_data[:, j] = series.map(GENDER_MAP).fillna(0.0).values
                elif col == "smoking_status":
                    cat_data[:, j] = series.map(SMOKING_MAP).fillna(0.0).values
                else:
                    cat_data[:, j] = pd.to_numeric(series, errors="coerce").fillna(0.0).values

        return np.hstack([num_data, cat_data]).astype(np.float32)

    def _get_note_text(self, row: pd.Series) -> str:
        pid = str(row.get("patient_id", ""))
        enc_id = str(row.get("encounter_id", ""))

        if enc_id in self.notes_dict:
            return self.notes_dict[enc_id]
        if pid in self.notes_dict:
            return self.notes_dict[pid]

        for text_field in ["clinical_note", "text", "raw_text"]:
            if text_field in row and pd.notna(row[text_field]) and str(row[text_field]).strip():
                return str(row[text_field])

        parts = []
        for part_name in ["chief_complaint", "history_of_present_illness", "physical_examination_notes"]:
            if part_name in row and pd.notna(row[part_name]):
                parts.append(str(row[part_name]))

        return " ".join(parts) if parts else "Bệnh nhân nhập viện không có ghi chú lâm sàng chi tiết."

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        row = self.df.iloc[idx]

        tabular_vec = torch.tensor(self.tabular_features[idx], dtype=torch.float32)

        text = self._get_note_text(row)
        encoded = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        input_ids = encoded["input_ids"].squeeze(0).to(dtype=torch.int64)
        attention_mask = encoded["attention_mask"].squeeze(0).to(dtype=torch.int64)

        label_val = int(row.get(self.target_col, 0))
        label_tensor = torch.tensor(label_val, dtype=torch.int64)

        return {
            "tabular_tensor": tabular_vec,
            "tabular": tabular_vec,
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "label": label_tensor,
            "patient_id": str(row.get("patient_id", "")),
            "encounter_id": str(row.get("encounter_id", "")),
        }


def get_data_loaders(
    train_df: Optional[pd.DataFrame] = None,
    val_df: Optional[pd.DataFrame] = None,
    test_df: Optional[pd.DataFrame] = None,
    data_dir: Union[str, Path] = "data/processed",
    tokenizer: Optional[Any] = None,
    batch_size: int = 64,
    max_length: int = 512,
    num_workers: int = 0,
    shuffle_train: bool = True,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    data_dir_path = Path(data_dir)

    if train_df is None:
        train_path = data_dir_path / "train.parquet"
        if not train_path.exists():
            raise FileNotFoundError(f"Train parquet file not found at {train_path}")
        train_df = pd.read_parquet(train_path)

    if val_df is None:
        val_path = data_dir_path / "val.parquet"
        if not val_path.exists():
            raise FileNotFoundError(f"Val parquet file not found at {val_path}")
        val_df = pd.read_parquet(val_path)

    if test_df is None:
        test_path = data_dir_path / "test.parquet"
        if not test_path.exists():
            raise FileNotFoundError(f"Test parquet file not found at {test_path}")
        test_df = pd.read_parquet(test_path)

    if tokenizer is None:
        tokenizer = _get_default_tokenizer()

    train_dataset = MultimodalEHRDataset(
        df=train_df,
        tokenizer=tokenizer,
        max_length=max_length,
        fit_scaler=True,
    )

    val_dataset = MultimodalEHRDataset(
        df=val_df,
        tokenizer=tokenizer,
        max_length=max_length,
        scaler=train_dataset.scaler,
        fit_scaler=False,
    )

    test_dataset = MultimodalEHRDataset(
        df=test_df,
        tokenizer=tokenizer,
        max_length=max_length,
        scaler=train_dataset.scaler,
        fit_scaler=False,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle_train,
        num_workers=num_workers,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )

    return train_loader, val_loader, test_loader


def process_and_save_patient_splits(
    raw_data_dir: Union[str, Path] = "data/raw",
    processed_data_dir: Union[str, Path] = "data/processed",
    test_size: float = 0.15,
    val_size: float = 0.15,
    seed: int = 42,
    use_ner_deid: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    raw_dir = Path(raw_data_dir)
    proc_dir = Path(processed_data_dir)
    proc_dir.mkdir(parents=True, exist_ok=True)

    patients_path = raw_dir / "patients_raw.parquet"
    notes_path = raw_dir / "clinical_notes_raw.jsonl"

    if not patients_path.exists():
        raise FileNotFoundError(f"Raw patients file not found: {patients_path}")

    logger.info("Loading raw tabular patients from: %s", patients_path)
    patients_df = pd.read_parquet(patients_path)

    notes_by_enc: Dict[str, Dict[str, Any]] = {}
    if notes_path.exists():
        logger.info("Loading raw clinical notes from: %s", notes_path)
        with open(notes_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    note = json.loads(line)
                    enc_id = note.get("encounter_id") or note.get("patient_id")
                    if enc_id:
                        notes_by_enc[enc_id] = note

    logger.info("Step 1/5: Running Temporal Aligner...")
    aligner = TemporalAligner()
    clean_df = aligner.remove_gold_standard_leakage(patients_df)
    if (
        "encounter_timestamp" in clean_df.columns
        and "diagnostic_confirmed_timestamp" in clean_df.columns
    ):
        initial_len = len(clean_df)
        clean_df = aligner.filter_events_by_time(
            clean_df,
            event_time_col="encounter_timestamp",
            diag_time_col="diagnostic_confirmed_timestamp",
        )
        dropped_leaks = initial_len - len(clean_df)
        logger.info("Filtered %d post-diagnostic encounter records.", dropped_leaks)

    logger.info("Step 2/5: De-identifying clinical notes...")
    deid = ClinicalDeidentifier(spacy_model=None, use_ner=use_ner_deid)

    notes_text_list = []
    chief_complaints = []
    histories = []
    physicals = []
    source_note_groups = []

    for _, row in clean_df.iterrows():
        enc_id = str(row.get("encounter_id", ""))
        pid = str(row.get("patient_id", ""))
        note_entry = notes_by_enc.get(enc_id) or notes_by_enc.get(pid, {})

        raw_note_text = note_entry.get("raw_text", "")
        if raw_note_text:
            deid_text = deid.deidentify_text(raw_note_text)
        else:
            deid_text = "Không có ghi chú lâm sàng."

        notes_text_list.append(deid_text)
        chief_complaints.append(note_entry.get("chief_complaint", ""))
        histories.append(note_entry.get("history_of_present_illness", ""))
        physicals.append(note_entry.get("physical_examination_notes", ""))
        source_note_groups.append(note_entry.get("source_note_group", ""))

    clean_df["clinical_note"] = notes_text_list
    clean_df["text"] = notes_text_list
    clean_df["chief_complaint"] = chief_complaints
    clean_df["history_of_present_illness"] = histories
    clean_df["physical_examination_notes"] = physicals
    clean_df["source_note_group"] = source_note_groups

    if "source_patient_group" not in clean_df:
        clean_df["source_patient_group"] = clean_df["patient_id"].astype(str)
    note_basis = (
        clean_df["chief_complaint"].fillna("").astype(str)
        + "\n" + clean_df["history_of_present_illness"].fillna("").astype(str)
        + "\n" + clean_df["physical_examination_notes"].fillna("").astype(str)
    )
    generated_note_groups = note_basis.map(
        lambda text: hashlib.sha256(" ".join(text.lower().split()).encode("utf-8")).hexdigest()
    )
    empty_note_group = clean_df["source_note_group"].fillna("").astype(str).str.strip().eq("")
    clean_df.loc[empty_note_group, "source_note_group"] = generated_note_groups[empty_note_group]

    logger.info("Step 3/5: Partitioning data at patient level (StratifiedGroupKFold)...")
    train_df, val_df, test_df = create_patient_level_splits(
        df=clean_df,
        patient_col="patient_id",
        target_col="diagnosis_label",
        test_size=test_size,
        val_size=val_size,
        seed=seed,
        group_cols=["source_patient_group", "source_note_group"],
    )

    logger.info("Step 4/5: Performing MICE imputation with strict Fit-Transform discipline...")
    imputer = ClinicalImputer(
        max_iter=10,
        random_state=seed,
        numerical_cols=NUMERICAL_COLS_DEFAULT,
        categorical_cols=CATEGORICAL_COLS_DEFAULT,
        create_indicators=True,
    )

    train_df = imputer.fit_transform(train_df)
    val_df = imputer.transform(val_df)
    test_df = imputer.transform(test_df)

    all_features = NUMERICAL_COLS_DEFAULT + CATEGORICAL_COLS_DEFAULT
    for name, split in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        nans = split[all_features].isna().sum().sum()
        if nans > 0:
            raise RuntimeError(f"Split {name} contains {nans} residual NaNs after imputation!")

    logger.info("Step 5/5: Exporting processed Parquet files to: %s", proc_dir)
    train_path = proc_dir / "train.parquet"
    val_path = proc_dir / "val.parquet"
    test_path = proc_dir / "test.parquet"

    train_df.to_parquet(train_path, index=False, engine="pyarrow")
    val_df.to_parquet(val_path, index=False, engine="pyarrow")
    test_df.to_parquet(test_path, index=False, engine="pyarrow")

    logger.info("[✓] Processing complete:")
    logger.info("    - Train saved to: %s (shape: %s)", train_path, train_df.shape)
    logger.info("    - Val saved to: %s (shape: %s)", val_path, val_df.shape)
    logger.info("    - Test saved to: %s (shape: %s)", test_path, test_df.shape)

    return train_df, val_df, test_df


if __name__ == "__main__":
    process_and_save_patient_splits()
