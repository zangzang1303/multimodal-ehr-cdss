from datetime import datetime
import random

import numpy as np

from scripts.convert_sources_to_raw import create_single_record, redact_target_diagnoses


def test_explicit_target_names_are_removed_from_model_text():
    text = "Known COPD with heart failure and community-acquired pneumonia; prior asthma."
    redacted = redact_target_diagnoses(text).lower()
    for term in ("copd", "heart failure", "pneumonia", "asthma"):
        assert term not in redacted


def test_fallback_features_do_not_depend_on_target_label():
    patient = {"birthdate": datetime(1970, 1, 1), "gender": "M", "city": "Hanoi"}
    records = []
    for label in range(4):
        random.seed(123)
        np.random.seed(123)
        record, _ = create_single_record(
            record_idx=1,
            p_id="SOURCE-PATIENT",
            e_id="SOURCE-ENCOUNTER",
            enc_dt=datetime(2026, 1, 1),
            diag_label=label,
            p_info=patient,
            obs_map={},
            obs_pat_fallback={},
            htn_patients=set(),
            dm_patients=set(),
        )
        records.append(record)

    feature_columns = (
        "age", "systolic_bp", "diastolic_bp", "heart_rate",
        "respiratory_rate", "spo2", "temperature", "wbc_count", "crp",
        "gender", "smoking_status", "history_hypertension", "history_diabetes",
    )
    reference = {column: records[0][column] for column in feature_columns}
    for record in records[1:]:
        assert {column: record[column] for column in feature_columns} == reference
