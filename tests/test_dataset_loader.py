from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import torch

from src.data_pipeline.dataset_loader import (
    CATEGORICAL_COLS_DEFAULT,
    NUMERICAL_COLS_DEFAULT,
    MultimodalEHRDataset,
    create_patient_level_splits,
    get_data_loaders,
)


@pytest.fixture
def synthetic_patient_df() -> pd.DataFrame:
    """Fixture providing a multi-encounter synthetic patient DataFrame."""
    np.random.seed(42)
    n_encounters = 300
    n_patients = 100

    patient_ids = [f"PT-{i:04d}" for i in np.random.choice(n_patients, size=n_encounters)]
    diagnosis_labels = np.random.choice([0, 1, 2, 3], size=n_encounters)

    data = {
        "patient_id": patient_ids,
        "encounter_id": [f"ENC-{i:05d}" for i in range(n_encounters)],
        "encounter_timestamp": ["2026-03-01T08:00:00"] * n_encounters,
        "diagnostic_confirmed_timestamp": ["2026-03-01T12:00:00"] * n_encounters,
        "diagnosis_label": diagnosis_labels,
        "age": np.random.randint(20, 85, size=n_encounters).astype(float),
        "systolic_bp": np.random.normal(120, 15, size=n_encounters),
        "diastolic_bp": np.random.normal(80, 10, size=n_encounters),
        "heart_rate": np.random.normal(75, 12, size=n_encounters),
        "respiratory_rate": np.random.normal(18, 4, size=n_encounters),
        "spo2": np.random.normal(96, 3, size=n_encounters),
        "temperature": np.random.normal(37.0, 0.7, size=n_encounters),
        "wbc_count": np.random.normal(7.5, 2.0, size=n_encounters),
        "crp": np.random.exponential(5.0, size=n_encounters),
        "gender": np.random.choice(["M", "F", "OTHER"], size=n_encounters),
        "smoking_status": np.random.choice(["NEVER", "FORMER", "CURRENT"], size=n_encounters),
        "history_hypertension": np.random.choice([0, 1], size=n_encounters),
        "history_diabetes": np.random.choice([0, 1], size=n_encounters),
        "clinical_note": [f"Bệnh nhân {p} nhập viện vì ho, khó thở." for p in patient_ids],
    }
    return pd.DataFrame(data)


def test_patient_level_splits_zero_leakage(synthetic_patient_df):
    """Assert 100% zero patient overlap between Train, Val, and Test splits."""
    train_df, val_df, test_df = create_patient_level_splits(
        df=synthetic_patient_df,
        patient_col="patient_id",
        target_col="diagnosis_label",
        test_size=0.15,
        val_size=0.15,
        seed=42,
    )

    train_pts = set(train_df["patient_id"])
    val_pts = set(val_df["patient_id"])
    test_pts = set(test_df["patient_id"])

    # Group constraint assertion
    assert len(train_pts & val_pts) == 0, f"Leakage Train-Val: {train_pts & val_pts}"
    assert len(train_pts & test_pts) == 0, f"Leakage Train-Test: {train_pts & test_pts}"
    assert len(val_pts & test_pts) == 0, f"Leakage Val-Test: {val_pts & test_pts}"

    # Verify completeness
    assert len(train_pts | val_pts | test_pts) == len(set(synthetic_patient_df["patient_id"]))

    # Verify all 4 target classes are present in every split
    assert set(train_df["diagnosis_label"].unique()) == {0, 1, 2, 3}
    assert set(val_df["diagnosis_label"].unique()) == {0, 1, 2, 3}
    assert set(test_df["diagnosis_label"].unique()) == {0, 1, 2, 3}


def test_multimodal_ehr_dataset_tensor_shapes(synthetic_patient_df):
    """Assert MultimodalEHRDataset yields correct tensor keys, shapes, and dtypes."""
    dataset = MultimodalEHRDataset(
        df=synthetic_patient_df,
        max_length=512,
        fit_scaler=True,
    )

    assert len(dataset) == len(synthetic_patient_df)
    sample = dataset[0]

    # Required keys
    assert "tabular_tensor" in sample
    assert "tabular" in sample
    assert "input_ids" in sample
    assert "attention_mask" in sample
    assert "label" in sample

    # Shapes and dtypes
    assert isinstance(sample["tabular_tensor"], torch.Tensor)
    assert sample["tabular_tensor"].dtype == torch.float32
    assert sample["tabular_tensor"].shape == (
        13,
    ), f"Expected [13], got {sample['tabular_tensor'].shape}"

    assert isinstance(sample["input_ids"], torch.Tensor)
    assert sample["input_ids"].dtype == torch.int64
    assert sample["input_ids"].shape == (512,)

    assert isinstance(sample["attention_mask"], torch.Tensor)
    assert sample["attention_mask"].dtype == torch.int64
    assert sample["attention_mask"].shape == (512,)

    assert isinstance(sample["label"], torch.Tensor)
    assert sample["label"].dtype == torch.int64
    assert sample["label"].ndim == 0 or sample["label"].shape == ()


def test_get_data_loaders_batch_streaming(synthetic_patient_df):
    """Verify DataLoader batches stream properly with correct batch shapes."""
    train_df, val_df, test_df = create_patient_level_splits(synthetic_patient_df, seed=42)

    batch_size = 16
    train_loader, val_loader, test_loader = get_data_loaders(
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        batch_size=batch_size,
    )

    batch = next(iter(train_loader))
    assert batch["tabular_tensor"].shape == (batch_size, 13)
    assert batch["input_ids"].shape == (batch_size, 512)
    assert batch["attention_mask"].shape == (batch_size, 512)
    assert batch["label"].shape == (batch_size,)


def test_processed_files_integrity():
    """Verify that data/processed parquet files exist, have zero overlap, and 0 NaNs."""
    data_dir = Path("data/processed")
    train_path = data_dir / "train.parquet"
    val_path = data_dir / "val.parquet"
    test_path = data_dir / "test.parquet"

    assert train_path.exists(), "train.parquet missing"
    assert val_path.exists(), "val.parquet missing"
    assert test_path.exists(), "test.parquet missing"

    train_df = pd.read_parquet(train_path)
    val_df = pd.read_parquet(val_path)
    test_df = pd.read_parquet(test_path)

    # 1. No patient leakage
    s_tr = set(train_df["patient_id"])
    s_va = set(val_df["patient_id"])
    s_te = set(test_df["patient_id"])
    assert len(s_tr & s_va) == 0, "Patient leakage Train-Val"
    assert len(s_tr & s_te) == 0, "Patient leakage Train-Test"
    assert len(s_va & s_te) == 0, "Patient leakage Val-Test"

    # 2. No residual NaNs in feature columns
    all_features = NUMERICAL_COLS_DEFAULT + CATEGORICAL_COLS_DEFAULT
    assert train_df[all_features].isna().sum().sum() == 0, "Residual NaNs in train"
    assert val_df[all_features].isna().sum().sum() == 0, "Residual NaNs in val"
    assert test_df[all_features].isna().sum().sum() == 0, "Residual NaNs in test"

    # 3. Missingness indicators exist
    assert "wbc_count_is_missing" in train_df.columns
    assert "crp_is_missing" in train_df.columns
