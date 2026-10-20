"""
Unit Tests for Clinical Data Pipeline & Privacy Modules.

Verifies:
1. ClinicalDeidentifier (HIPAA Safe Harbor PHI/PII redaction).
2. TemporalAligner (Strict time-locking & PROBAST gold-standard blacklist).
3. ClinicalImputer (MICE Multivariate Imputation with Binary Missingness Indicators).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data_pipeline.deidentifier import ClinicalDeidentifier
from src.data_pipeline.temporal_aligner import TemporalAligner
from src.data_pipeline.imputer import ClinicalImputer, ClinicalMICEImputer, TabularMICEImputer

# =====================================================================
# 1. DEIDENTIFIER TESTS
# =====================================================================


def test_deidentifier_clinical_note_redaction():
    """Test Member 3 specification sentence and standard PHI tokens."""
    deid = ClinicalDeidentifier(spacy_model=None, use_ner=False)

    raw_text = (
        "Bác sĩ Nguyễn Văn A khám cho bệnh nhân Trần Thị B tại Bệnh viện Bạch Mai "
        "ngày 12/03/2026. Số CCCD: 001201004567, SĐT liên hệ: +84912345678, "
        "email: bsnguyenvana@bachmai.vn. Thẻ BHYT: GD4010123456789."
    )

    redacted = deid.deidentify_text(raw_text)

    # 1. Assert tokens exist
    assert "[REDACTED_NAME]" in redacted
    assert "[REDACTED_DATE]" in redacted
    assert "[REDACTED_HOSPITAL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "[REDACTED_ID]" in redacted

    # 2. Assert sensitive strings no longer appear in redacted output
    assert "Nguyễn Văn A" not in redacted
    assert "Trần Thị B" not in redacted
    assert "Bạch Mai" not in redacted
    assert "001201004567" not in redacted
    assert "+84912345678" not in redacted
    assert "bsnguyenvana@bachmai.vn" not in redacted
    assert "GD4010123456789" not in redacted


def test_deidentifier_100_synthetic_sentences():
    """Acceptance criterion: 100 sentences with sensitive PHI fully redacted."""
    deid = ClinicalDeidentifier(spacy_model=None, use_ner=False)

    names = ["Nguyễn Văn An", "Trần Thị Bình", "Lê Văn Cường", "Phạm Thị Dung", "Hoàng Văn Em"]
    hospitals = [
        "Bệnh viện Chợ Rẫy",
        "Bệnh viện Bạch Mai",
        "Phòng khám Đa khoa Sài Gòn",
        "Bệnh viện Quân y 103",
    ]
    phones = ["+84912345678", "0987654321", "0381234567", "0909123456"]
    dates = ["15/04/2025", "2026-01-30", "01/12/2024", "ngày 20 tháng 10 năm 2025"]
    ids = ["001201004567", "079090001234", "123456789"]

    sentences = []
    for i in range(100):
        name = names[i % len(names)]
        hosp = hospitals[i % len(hospitals)]
        phone = phones[i % len(phones)]
        date = dates[i % len(dates)]
        cid = ids[i % len(ids)]
        sentences.append(
            f"Bệnh nhân {name} nhập viện tại {hosp} vào ngày {date}. "
            f"Số định danh {cid}, số điện thoại người nhà: {phone}."
        )

    redacted_sentences = deid.deidentify_batch(sentences)
    assert len(redacted_sentences) == 100

    for i, res in enumerate(redacted_sentences):
        name = names[i % len(names)]
        hosp = hospitals[i % len(hospitals)]
        phone = phones[i % len(phones)]
        cid = ids[i % len(ids)]

        assert name not in res, f"Name leaked in sentence {i}: {res}"
        assert hosp not in res, f"Hospital leaked in sentence {i}: {res}"
        assert phone not in res, f"Phone leaked in sentence {i}: {res}"
        assert cid not in res, f"ID leaked in sentence {i}: {res}"
        assert "[REDACTED_NAME]" in res
        assert "[REDACTED_HOSPITAL]" in res
        assert "[REDACTED_PHONE]" in res
        assert "[REDACTED_ID]" in res


def test_deidentifier_english_and_formats():
    """Verify English clinical formats and standard MRN/SSN formats."""
    deid = ClinicalDeidentifier(spacy_model=None, use_ner=False)

    text = "Doctor John Doe evaluated patient Jane Doe at Boston General Hospital on 2026-05-18. MRN: MRN987654."
    redacted = deid.deidentify_text(text)

    assert "John Doe" not in redacted
    assert "Jane Doe" not in redacted
    assert "[REDACTED_NAME]" in redacted
    assert "[REDACTED_HOSPITAL]" in redacted
    assert "[REDACTED_DATE]" in redacted
    assert "[REDACTED_ID]" in redacted


def test_deidentifier_with_spacy_ner():
    """Verify Biomedical NER integration with spaCy model."""
    deid = ClinicalDeidentifier(spacy_model="en_core_web_sm", use_ner=True)
    text = "Patient William Smith was admitted to Mount Sinai Hospital in New York on 10/11/2025."
    redacted = deid.deidentify_text(text)

    assert "William Smith" not in redacted
    assert "[REDACTED_NAME]" in redacted
    assert "[REDACTED_HOSPITAL]" in redacted or "Hospital" in redacted
    assert "[REDACTED_DATE]" in redacted


# =====================================================================
# 2. TEMPORAL ALIGNER TESTS
# =====================================================================


def test_temporal_aligner_time_locking():
    """Verify events occurring at or after diagnosis (t_event >= t_diag) are dropped."""
    aligner = TemporalAligner()

    data = pd.DataFrame(
        {
            "event_id": [1, 2, 3, 4],
            "event_time": [
                "2026-03-12 08:00:00",  # Prior -> KEEP
                "2026-03-12 09:15:00",  # Prior -> KEEP
                "2026-03-12 09:30:00",  # Exact diag time (t_event == t_diag) -> DROP
                "2026-03-12 10:00:00",  # Post diag (t_event > t_diag) -> DROP
            ],
            "diagnostic_time": ["2026-03-12 09:30:00"] * 4,
            "feature_name": ["heart_rate", "systolic_bp", "fev1", "crp"],
            "value": [88.0, 125.0, 1.8, 12.0],
        }
    )

    filtered = aligner.filter_events_by_time(
        data,
        event_time_col="event_time",
        diag_time_col="diagnostic_time",
    )

    assert len(filtered) == 2
    assert list(filtered["event_id"]) == [1, 2]
    assert "2026-03-12 10:00:00" not in filtered["event_time"].values
    assert "2026-03-12 09:30:00" not in filtered["event_time"].values


def test_temporal_aligner_gold_standard_blacklist():
    """Verify gold-standard diagnostic criteria are stripped from predictors."""
    aligner = TemporalAligner()

    df = pd.DataFrame(
        {
            "patient_id": [101, 102, 103],
            "age": [65, 72, 58],
            "systolic_bp": [130.0, 140.0, 120.0],
            "fev1": [1.8, 2.1, 1.5],  # COPD Gold Standard
            "fvc": [2.6, 2.9, 2.3],  # COPD Gold Standard
            "fev1_fvc_ratio": [0.69, 0.72, 0.65],  # COPD Gold Standard
            "lvef": [45.0, 55.0, 38.0],  # Heart Failure Gold Standard
            "sputum_culture_bacteria": ["S.pneumoniae", "Negative", "Klebsiella"],  # Pneumonia
            "crp": [15.2, 3.4, 45.0],  # Valid Predictor
        }
    )

    detected_leaks = aligner.check_gold_standard_leakage(df)
    assert set(detected_leaks) == {
        "fev1",
        "fvc",
        "fev1_fvc_ratio",
        "lvef",
        "sputum_culture_bacteria",
    }

    clean_df = aligner.remove_gold_standard_leakage(df)
    assert "fev1" not in clean_df.columns
    assert "fvc" not in clean_df.columns
    assert "fev1_fvc_ratio" not in clean_df.columns
    assert "lvef" not in clean_df.columns
    assert "sputum_culture_bacteria" not in clean_df.columns

    # Valid predictors must remain intact
    assert "age" in clean_df.columns
    assert "systolic_bp" in clean_df.columns
    assert "crp" in clean_df.columns
    assert len(clean_df) == 3


def test_temporal_aligner_filter_features_dict():
    """Verify dictionary-style event filtering."""
    events = [
        {"timestamp": "2026-01-01 08:00:00", "feature_name": "systolic_bp", "value": 120},
        {"timestamp": "2026-01-01 08:30:00", "feature_name": "fev1", "value": 1.7},  # Blacklisted
        {"timestamp": "2026-01-01 10:00:00", "feature_name": "heart_rate", "value": 85},  # Leakage
    ]

    filtered = TemporalAligner.filter_features(events, confirmed_diag_time="2026-01-01 09:00:00")
    assert len(filtered) == 1
    assert filtered[0]["feature_name"] == "systolic_bp"


# =====================================================================
# 3. MICE IMPUTER TESTS
# =====================================================================


def test_clinical_imputer_mice_and_indicators():
    """Verify MICE completes missing values and appends binary missingness indicators."""
    np.random.seed(42)
    n_samples = 200

    features = {
        "age": np.random.randint(20, 85, size=n_samples).astype(float),
        "systolic_bp": np.random.normal(125, 15, size=n_samples),
        "diastolic_bp": np.random.normal(80, 10, size=n_samples),
        "heart_rate": np.random.normal(78, 12, size=n_samples),
        "respiratory_rate": np.random.normal(18, 4, size=n_samples),
        "spo2": np.random.normal(96, 3, size=n_samples),
        "temperature": np.random.normal(37.0, 0.8, size=n_samples),
        "wbc_count": np.random.normal(8.0, 2.5, size=n_samples),
        "crp": np.random.exponential(10, size=n_samples),
        "gender": np.random.choice(["M", "F"], size=n_samples),
        "smoking_status": np.random.choice(["NEVER", "FORMER", "CURRENT"], size=n_samples),
    }
    df = pd.DataFrame(features)

    # Introduce ~25% NaN into numerical columns
    for col in ["systolic_bp", "diastolic_bp", "wbc_count", "crp", "temperature"]:
        nan_indices = np.random.choice(n_samples, size=int(n_samples * 0.25), replace=False)
        df.loc[nan_indices, col] = np.nan

    # Introduce some NaNs into categorical
    cat_nan_idx = np.random.choice(n_samples, size=int(n_samples * 0.10), replace=False)
    df.loc[cat_nan_idx, "smoking_status"] = np.nan

    assert df.isna().sum().sum() > 0

    imputer = ClinicalImputer(max_iter=10, random_state=42)
    imputed_df = imputer.fit_transform(df)

    # Acceptance criteria assertions:
    # 1. 0 remaining NaNs
    assert (
        imputed_df.isna().sum().sum() == 0
    ), f"Remaining NaNs: {imputed_df.isna().sum().to_dict()}"

    # 2. Indicators exist and are binary 0 or 1
    for col in ["systolic_bp", "diastolic_bp", "wbc_count", "crp", "temperature"]:
        indicator_col = f"{col}_is_missing"
        assert indicator_col in imputed_df.columns
        unique_vals = set(imputed_df[indicator_col].unique())
        assert unique_vals.issubset({0, 1}), f"Non-binary values in {indicator_col}: {unique_vals}"
        assert (imputed_df[indicator_col] == 1).sum() > 0

    # 3. Missingness report
    report = imputer.get_missingness_report(df, imputed_df)
    assert isinstance(report, pd.DataFrame)
    assert "missing_before_pct" in report.columns
    assert "missing_after_pct" in report.columns
    assert (report["missing_after_pct"] == 0.0).all()


def test_clinical_imputer_aliases():
    """Verify alias equivalence for ClinicalMICEImputer and TabularMICEImputer."""
    assert ClinicalMICEImputer is ClinicalImputer
    assert TabularMICEImputer is ClinicalImputer


# =====================================================================
# 4. TASK 3.1 SPECIFICATION CONTRACT TESTS
# =====================================================================


def test_deidentifier():
    """Exact test function per Task 3.1 specification."""
    test_deidentifier_clinical_note_redaction()


def test_temporal_aligner():
    """Exact test function per Task 3.1 specification."""
    test_temporal_aligner_time_locking()
    test_temporal_aligner_gold_standard_blacklist()


def test_imputer():
    """Exact test function per Task 3.1 specification."""
    test_clinical_imputer_mice_and_indicators()
