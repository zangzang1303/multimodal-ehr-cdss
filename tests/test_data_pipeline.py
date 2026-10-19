"""
Unit Tests for Medical Data Pipeline & Privacy Compliance
Multimodal EHR CDSS - Phase 1 / Backlog 02 (Task 3.1)
Verifies:
1. HIPAA De-identification (Safe Harbor tokens: [REDACTED_*])
2. PROBAST Temporal Alignment & Gold-Standard Blacklist Filtering
3. MICE Multivariate Imputation & Binary Missingness Indicators
"""

import numpy as np
import pandas as pd


from src.data_pipeline.deidentifier import ClinicalDeidentifier
from src.data_pipeline.temporal_aligner import TemporalAligner
from src.data_pipeline.imputer import ClinicalImputer, ClinicalMICEImputer


# =====================================================================
# 1. TEST DE-IDENTIFIER (Khử định danh PHI / PII)
# =====================================================================
def test_deidentifier():
    """
    Test that sensitive patient & doctor identifying information (CCCD, VN phone,
    email, person names, dates, hospitals) are 100% removed and replaced with standard tokens:
    [REDACTED_NAME], [REDACTED_DATE], [REDACTED_HOSPITAL], [REDACTED_PHONE].
    """
    raw_text = (
        "Bác sĩ Nguyễn Văn A khám cho bệnh nhân Trần Thị B tại Bệnh viện Bạch Mai "
        "ngày 12/03/2026. Số điện thoại: +84912345678, CCCD: 012345678901, email: tranb@example.com."
    )

    deid = ClinicalDeidentifier()
    sanitized_text = deid.deidentify_text(raw_text)

    # 1. Assert 100% of sensitive terms are removed
    sensitive_terms = [
        "Nguyễn Văn A",
        "Trần Thị B",
        "Bạch Mai",
        "12/03/2026",
        "+84912345678",
        "012345678901",
        "tranb@example.com",
    ]
    for term in sensitive_terms:
        assert term not in sanitized_text, f"Sensitive term '{term}' leaked in sanitized output!"

    # 2. Assert surrogate tokens are correctly inserted
    required_tokens = [
        "[REDACTED_NAME]",
        "[REDACTED_DATE]",
        "[REDACTED_HOSPITAL]",
        "[REDACTED_PHONE]",
    ]
    for token in required_tokens:
        assert token in sanitized_text, f"Expected surrogate token '{token}' not found in output!"


def test_deidentifier_edge_cases():
    """
    Verify deidentifier handles empty strings and variations of VN phone numbers.
    """
    deid = ClinicalDeidentifier()
    assert deid.deidentify_text("") == ""

    text_with_09_phone = "Liên hệ người nhà bệnh nhân qua số 0912345678 vào ngày 2026-09-10."
    sanitized = deid.deidentify_text(text_with_09_phone)
    assert "0912345678" not in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "2026-09-10" not in sanitized
    assert "[REDACTED_DATE]" in sanitized


# =====================================================================
# 2. TEST TEMPORAL ALIGNER & BLACKLIST (Khóa thời gian & Chống rò rỉ nhãn)
# =====================================================================
def test_temporal_aligner():
    """
    Test time-locking mechanism and gold-standard target leakage prevention:
    - Events at or after diagnosis time (10:00 vs 09:30) must be discarded.
    - Blacklisted variables ('fev1', 'lvef') must be detected and removed.
    """
    aligner = TemporalAligner()

    # Part A: Time-locking verification
    events_data = {
        "event_id": ["E1", "E2", "E3"],
        "event_time": ["2026-09-14 09:00:00", "2026-09-14 09:30:00", "2026-09-14 10:00:00"],
        "diag_time": ["2026-09-14 09:30:00", "2026-09-14 09:30:00", "2026-09-14 09:30:00"],
        "description": ["Pre-diagnosis lab test", "Diagnosis confirmation", "Post-diagnosis medication"],
    }
    events_df = pd.DataFrame(events_data)
    filtered_df = aligner.filter_events_by_time(events_df, "event_time", "diag_time")

    # Assert: Event occurring at 10:00 (E3) and at 09:30 (E2) must be excluded
    event_times_kept = list(filtered_df["event_time"])
    assert "2026-09-14 10:00:00" not in event_times_kept, "Event at 10:00 was not filtered out!"
    assert len(filtered_df) == 1
    assert filtered_df.iloc[0]["event_id"] == "E1"

    # Part B: Blacklist detection and leakage removal
    leakage_df = pd.DataFrame({
        "age": [65, 72, 58],
        "systolic_bp": [130.0, 140.0, 120.0],
        "heart_rate": [78.0, 85.0, 92.0],
        "fev1": [1.4, 1.8, 2.1],          # Gold standard for COPD
        "lvef": [35.0, 45.0, 55.0],       # Gold standard for Heart Failure
    })

    # Assert blacklisted columns are detected
    assert aligner.is_blacklisted("fev1") is True
    assert aligner.is_blacklisted("lvef") is True
    detected_leakage = aligner.detect_gold_standard_leakage(leakage_df)
    assert "fev1" in detected_leakage
    assert "lvef" in detected_leakage

    # Assert gold standard features are completely eliminated
    cleaned_df = aligner.remove_gold_standard_leakage(leakage_df)
    assert "fev1" not in cleaned_df.columns
    assert "lvef" not in cleaned_df.columns
    assert "age" in cleaned_df.columns
    assert "systolic_bp" in cleaned_df.columns
    assert "heart_rate" in cleaned_df.columns


# =====================================================================
# 3. TEST IMPUTER (Gán dữ liệu khuyết MICE)
# =====================================================================
def test_imputer():
    """
    Test MICE multivariate imputation on continuous clinical features:
    - Input dataframe has 20% random NaNs across vital signs.
    - After fit_transform(): df.isna().sum().sum() == 0.
    - Binary indicator columns '_is_missing' are generated and contain only 0 and 1.
    """
    np.random.seed(42)
    n_samples = 100

    # 9 Continuous vital signs / laboratory features
    data = {
        "age": np.random.randint(20, 85, size=n_samples).astype(float),
        "systolic_bp": np.random.uniform(90.0, 180.0, size=n_samples),
        "diastolic_bp": np.random.uniform(60.0, 110.0, size=n_samples),
        "heart_rate": np.random.uniform(60.0, 120.0, size=n_samples),
        "respiratory_rate": np.random.uniform(12.0, 32.0, size=n_samples),
        "spo2": np.random.uniform(88.0, 99.0, size=n_samples),
        "temperature": np.random.uniform(36.0, 39.5, size=n_samples),
        "wbc_count": np.random.uniform(4.0, 20.0, size=n_samples),
        "crp": np.random.uniform(0.5, 120.0, size=n_samples),
    }
    df = pd.DataFrame(data)

    # Inject approximately 20% random NaN values across continuous columns
    mask = np.random.rand(*df.shape) < 0.20
    df[mask] = np.nan

    # Ensure there are missing values to begin with
    total_missing_before = df.isna().sum().sum()
    assert total_missing_before > 0, "Initial dataframe must contain missing values for the test."

    imputer = ClinicalImputer(max_iter=10, random_state=42)
    imputed_df = imputer.fit_transform(df)

    # 1. Assert: No remaining NaNs in the output dataframe
    assert imputed_df.isna().sum().sum() == 0, "Imputed dataframe still contains NaN values!"

    # 2. Assert: '_is_missing' columns exist for features with missing values
    missing_cols_original = [col for col in df.columns if df[col].isna().any()]
    assert len(missing_cols_original) > 0

    for col in missing_cols_original:
        indicator_col = f"{col}_is_missing"
        assert indicator_col in imputed_df.columns, f"Indicator '{indicator_col}' missing from output!"

        unique_vals = set(imputed_df[indicator_col].unique())
        assert unique_vals.issubset({0, 1}), f"Column '{indicator_col}' must contain binary {0, 1} values."

        # Verify indicator aligns with the ground truth missing mask
        expected_indicator = df[col].isna().astype(int)
        np.testing.assert_array_equal(
            imputed_df[indicator_col].values,
            expected_indicator.values,
            err_msg=f"Indicator '{indicator_col}' does not match original missingness pattern!",
        )


def test_imputer_alias_compatibility():
    """
    Ensure ClinicalMICEImputer alias can be instantiated and works identically.
    """
    imputer = ClinicalMICEImputer()
    df = pd.DataFrame({"crp": [1.0, np.nan, 3.0], "wbc_count": [5.0, 6.0, np.nan]})
    res = imputer.fit_transform(df)
    assert res.isna().sum().sum() == 0
    assert "crp_is_missing" in res.columns
    assert "wbc_count_is_missing" in res.columns
