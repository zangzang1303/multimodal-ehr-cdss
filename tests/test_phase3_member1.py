"""Phase 3 Member 1 tests: fail-fast backbone loading, guarded checkpoints, note variants,
statistics and the content-level leakage audit."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import torch

from scripts.audit_data_leakage import content_checks
from src.data_pipeline.note_variants import VARIANTS, inject_cue, mask_numbers, narrative_only, remove_vitals
from src.evaluation.stats import (
    bootstrap_ci, ece_equal_mass, holm, macro_auroc, net_benefit, net_benefit_treat_all,
    net_reduction_in_interventions, paired_bootstrap,
)
from src.models.backbone_loader import MissingPretrainedWeightsError, load_pretrained_text_backbone
from src.models.checkpoint_io import UnsafeCheckpointWrite, save_checkpoint_safely

TEMPLATE_NOTE = (
    "CLINICAL ENCOUNTER NOTE - [REDACTED_HOSPITAL]\nPatient Name: [REDACTED_NAME]| Gender: M | Age: 70\n"
    "----\nCHIEF COMPLAINT:\nPatient presents with cough.\n\nHISTORY OF PRESENT ILLNESS:\n"
    "Patient 70yo presents with cough, shortness of breath.\n\nPHYSICAL EXAMINATION:\n"
    "BP: 126.8/80.7 mmHg, HR: 67.5 bpm, SpO2: 69.3%.\n\nMEDICATIONS:\nInhalers as prescribed.\n"
)
MTSAMPLES_NOTE = (
    "HEADER\n=====\nVITALS AT ADMISSION:\nBP: 127/80 mmHg | HR: 65 bpm | SpO2: 97.3%\nWBC: 8.1 x10^9/L | CRP: 12 mg/L\n"
    "-----\nCHIEF COMPLAINT:\nGI bleed.\n\nHISTORY OF PRESENT ILLNESS:\nAn 80-year-old woman with fatigue.\n\n"
    "PHYSICAL EXAMINATION:\nVital signs recorded. Crackles at bases.\n\nMEDICATIONS:\nLasix 40 mg b.i.d.\n"
)


# ----------------------------------------------------------------- backbone / checkpoint
def test_missing_pretrained_weights_raise_instead_of_random_init():
    with pytest.raises(MissingPretrainedWeightsError):
        load_pretrained_text_backbone("this-org/does-not-exist-bert", local_files_only=True)


def test_checkpoint_guard_refuses_untrained_runs(tmp_path):
    target = tmp_path / "multimodal_best.pt"
    with pytest.raises(UnsafeCheckpointWrite):
        save_checkpoint_safely({"model_state": {}}, target, epochs_trained=0)
    with pytest.raises(UnsafeCheckpointWrite):
        save_checkpoint_safely({"model_state": {}}, target, epochs_trained=5, eval_only=True)
    assert not target.exists()


def test_checkpoint_guard_redirects_smoke_runs_and_stamps_provenance(tmp_path):
    target = tmp_path / "multimodal_best.pt"
    saved = save_checkpoint_safely({"model_state": {"w": torch.ones(1)}}, target, epochs_trained=2, smoke_test=True)
    assert saved.name == "multimodal_best.smoke.pt" and not target.exists()
    saved = save_checkpoint_safely({"model_state": {"w": torch.ones(1)}}, target, epochs_trained=3)
    payload = torch.load(saved, weights_only=True)
    assert "data_manifest_sha256" in payload["provenance"]


# ------------------------------------------------------------------------- note variants
def test_mask_numbers_removes_every_digit():
    assert not any(ch.isdigit() for ch in mask_numbers(TEMPLATE_NOTE))


@pytest.mark.parametrize("note", [TEMPLATE_NOTE, MTSAMPLES_NOTE])
def test_remove_vitals_drops_numeric_vitals_but_keeps_narrative(note):
    out = remove_vitals(note)
    assert "SpO2: 97" not in out and "SpO2: 69" not in out and "CRP: 12" not in out
    assert "CHIEF COMPLAINT:" in out and "MEDICATIONS:" in out


def test_narrative_only_keeps_three_sections():
    out = narrative_only(MTSAMPLES_NOTE)
    assert "GI bleed" in out and "Lasix" in out
    assert "VITALS" not in out and "PHYSICAL EXAMINATION" not in out and "Crackles" not in out


def test_variants_registry_and_cue_injection_is_deterministic():
    assert set(VARIANTS) == {"full", "num_masked", "no_vitals", "narrative_only"}
    a = inject_cue(TEMPLATE_NOTE, 2, "PT-1", rho=1.0)
    assert a == inject_cue(TEMPLATE_NOTE, 2, "PT-1", rho=1.0) and a != TEMPLATE_NOTE
    assert inject_cue(TEMPLATE_NOTE, 2, "PT-1", rho=0.0) == TEMPLATE_NOTE
    hits = sum(inject_cue(TEMPLATE_NOTE, 0, f"PT-{i}", rho=0.5) != TEMPLATE_NOTE for i in range(2000))
    assert 900 < hits < 1100


# ---------------------------------------------------------------------------- statistics
def _toy(n=400, seed=0, strength=2.0):
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 4, n)
    logits = rng.normal(size=(n, 4))
    logits[np.arange(n), y] += strength
    p = np.exp(logits) / np.exp(logits).sum(1, keepdims=True)
    return y, p


def test_bootstrap_ci_contains_estimate_and_paired_difference_of_identical_models_is_zero():
    y, p = _toy()
    ci = bootstrap_ci(y, p, n_boot=200)
    assert ci["ci95"][0] <= ci["estimate"] <= ci["ci95"][1]
    same = paired_bootstrap(y, p, p, n_boot=200)
    assert same["delta"] == 0 and same["p_value"] == 1.0


def test_paired_bootstrap_detects_a_clearly_better_model():
    y, strong = _toy(strength=3.0)
    _, weak = _toy(seed=1, strength=0.3)
    res = paired_bootstrap(y, strong, weak, n_boot=300)
    assert res["delta"] > 0.2 and res["ci95"][0] > 0 and res["p_value"] < 0.01
    assert macro_auroc(y, strong) > macro_auroc(y, weak)


def test_holm_adjustment_matches_textbook_example():
    assert np.allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


def test_net_benefit_and_vickers_net_reduction_formula():
    y = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    risk = np.array([0.9, 0.8, 0.7, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
    pt = 0.2
    assert net_benefit(y, risk, pt) == pytest.approx(2 / 10 - 1 / 10 * 0.25)
    assert net_benefit_treat_all(y, pt) == pytest.approx(0.2 - 0.8 * 0.25)
    # (0.175 - 0.0) * (0.8 / 0.2) * 100 = 70 interventions avoided per 100 patients
    assert net_reduction_in_interventions(0.175, 0.0, pt) == pytest.approx(70.0)


def test_equal_mass_ece_is_zero_for_perfectly_calibrated_confidence():
    y = np.array([0, 0, 1, 1])
    p = np.array([[1.0, 0, 0, 0], [1.0, 0, 0, 0], [0, 1.0, 0, 0], [0, 1.0, 0, 0]])
    assert ece_equal_mass(y, p, n_bins=2) == pytest.approx(0.0)


# ------------------------------------------------------------------------- leakage audit
def _frames(train_notes, test_notes, train_labels, test_labels):
    mk = lambda notes, labels: pd.DataFrame({"clinical_note": notes, "diagnosis_label": labels})  # noqa: E731
    return {"train": mk(train_notes, train_labels), "val": mk(test_notes, test_labels),
            "test": mk(test_notes, test_labels)}


def test_audit_flags_unredacted_diagnoses_and_label_specific_reused_notes():
    frames = _frames(["pt with pneumonia", "copd flare 2", "asthma attack", "chf"],
                     ["copd flare 7", "pneumonia again"], [3, 1, 0, 2], [1, 3])
    report, failures = content_checks(frames)
    assert report["unredacted_target_term_rate"]["train"] == 1.0
    assert report["label_informative_duplicate_rate"]["test"] == 0.5  # "copd flare <NUM>" reused, same label
    assert failures


def test_audit_allows_generic_templates_shared_by_all_classes():
    template = "patient presents for evaluation of respiratory condition"
    frames = _frames([template] * 8, [template] * 2, [0, 1, 2, 3, 0, 1, 2, 3], [0, 2])
    report, failures = content_checks(frames)
    assert report["note_body_duplicated_from_train_rate"]["test"] == 1.0
    assert report["label_informative_duplicate_rate"]["test"] == 0.0
    assert not failures
