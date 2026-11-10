"""Unit tests for multimodal deep learning model components and evaluation metrics."""

from __future__ import annotations

import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import torch
import torch.nn.functional as F
from torch import nn

from src.evaluation.metrics import (
    compute_multiclass_metrics,
    compute_subgroup_fairness,
    expected_calibration_error,
    maximum_calibration_error,
    plot_reliability_diagram,
)
from src.models.baselines import DummyTextBackbone
from src.models.calibration import TemperatureScalingCalibrator
from src.models.multimodal_fusion import AblationModel, ConcatFusion, CrossAttentionFusion
from src.models.tabular_encoder import FTTransformerEncoder, TabularTokenizer
from src.models.text_encoder import ClinicalTextEncoder


def test_tabular_tokenizer_and_fttransformer():
    """Verify TabularTokenizer output shape [Batch, M+1, 128] and gradient flow."""
    batch_size = 4
    n_num = 9
    n_cat = 4
    d_token = 128

    numerical = torch.randn(batch_size, n_num)
    categorical = torch.tensor([[1, 2, 1, 2], [3, 0, 2, 1], [0, 1, 0, 0], [2, 1, 1, 0]])

    tokenizer = TabularTokenizer(n_numerical=n_num, categorical_cardinalities=[4, 4, 3, 3], d_token=d_token)
    tokens = tokenizer(numerical, categorical)
    assert tokens.shape == (batch_size, n_num + n_cat + 1, d_token)

    encoder = FTTransformerEncoder(
        n_numerical=n_num,
        categorical_cardinalities=[4, 4, 3, 3],
        d_token=d_token,
        n_blocks=2,
        n_heads=4,
    )
    encoded = encoder(numerical, categorical)
    assert encoded.shape == (batch_size, n_num + n_cat + 1, d_token)

    loss = encoded.sum()
    loss.backward()
    assert encoder.tokenizer.numeric_weight.grad is not None
    assert not torch.isnan(encoder.tokenizer.numeric_weight.grad).any()


def test_clinical_text_encoder_shapes_and_gradients():
    """Verify ClinicalTextEncoder extracts [Batch, L, 128] representation."""
    batch_size = 3
    seq_len = 16
    hidden_size = 32
    d_token = 128

    dummy_backbone = DummyTextBackbone(vocab_size=100, hidden_size=hidden_size)
    encoder = ClinicalTextEncoder(
        backbone=dummy_backbone,
        d_token=d_token,
        max_length=seq_len,
        dropout=0.0,
    )

    input_ids = torch.randint(0, 100, (batch_size, seq_len))
    attention_mask = torch.ones(batch_size, seq_len)
    attention_mask[:, 10:] = 0

    h_text = encoder(input_ids, attention_mask)
    assert h_text.shape == (batch_size, seq_len, d_token)

    loss = h_text.sum()
    loss.backward()
    assert encoder.proj.weight.grad is not None
    assert not torch.isnan(encoder.proj.weight.grad).any()


def test_cross_attention_fusion_handles_padding_and_missing_modality():
    """Verify cross attention ignores padding text tokens and preserves gradients."""
    d_token = 64
    fusion = CrossAttentionFusion(d_token=d_token, num_classes=4, n_heads=4, dropout=0.0).eval()

    batch_size = 2
    n_tab_tokens = 14
    seq_len = 8

    tab_tokens = torch.randn(batch_size, n_tab_tokens, d_token, requires_grad=True)
    text_tokens = torch.randn(batch_size, seq_len, d_token, requires_grad=True)
    attention_mask = torch.tensor([[1, 1, 1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0, 0, 0]])

    logits = fusion(tab_tokens, text_tokens, attention_mask)
    assert logits.shape == (batch_size, 4)

    disturbed_text = text_tokens.clone()
    disturbed_text[0, 4:] += 999.0
    disturbed_text[1, 2:] += 999.0
    disturbed_logits = fusion(tab_tokens, disturbed_text, attention_mask)
    assert torch.allclose(logits, disturbed_logits, atol=1e-5)

    loss = logits.sum()
    loss.backward()
    assert not torch.isnan(fusion.head.weight.grad).any()
    assert not torch.isnan(fusion.gate.weight.grad).any()


def test_temperature_scaling_calibrator_properties():
    """Verify T > 0, sum(prob) == 1, NLL reduction, and state dictionary round-trip."""
    logits = torch.tensor([[5.0, 1.0, 0.5, 0.2], [1.0, 6.0, 0.2, 0.1], [0.2, 0.4, 7.0, 0.1], [0.1, 0.2, 0.3, 5.5]])
    labels = torch.tensor([0, 1, 2, 3])

    calibrator = TemperatureScalingCalibrator().fit(logits, labels)
    assert calibrator.temperature > 0.0

    probs = calibrator.predict_proba(logits)
    assert torch.allclose(probs.sum(dim=-1), torch.ones(len(logits)), atol=1e-5)

    saved_state = calibrator.state_dict()
    new_calibrator = TemperatureScalingCalibrator()
    new_calibrator.load_state_dict(saved_state)
    assert new_calibrator.temperature == calibrator.temperature
    assert torch.allclose(new_calibrator.predict_proba(logits), probs)


def test_calibration_metrics_ece_and_mce():
    """Verify mathematical definitions of ECE and MCE."""
    y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3])
    probs_perfect = np.zeros((8, 4))
    for i, label in enumerate(y_true):
        probs_perfect[i, label] = 1.0

    assert expected_calibration_error(y_true, probs_perfect, n_bins=10) == 0.0
    assert maximum_calibration_error(y_true, probs_perfect, n_bins=10) == 0.0

    metrics = compute_multiclass_metrics(y_true, probs_perfect, n_bins=10)
    assert metrics["accuracy"] == 1.0
    assert metrics["macro_f1"] == 1.0
    assert metrics["ece"] == 0.0
    assert metrics["mce"] == 0.0
    assert metrics["brier_score"] == 0.0


def test_reliability_diagram_and_fairness_audit():
    """Verify artifact generation of calibration curve and fairness audit report."""
    np.random.seed(42)
    n = 100
    y_true = np.random.choice([0, 1, 2, 3], size=n)
    probs_uncal = np.random.dirichlet([1, 1, 1, 1], size=n)
    probs_cal = np.random.dirichlet([2, 2, 2, 2], size=n)

    df_test = pd.DataFrame({
        "diagnosis_label": y_true,
        "gender": np.random.choice(["M", "F"], size=n),
        "age": np.random.randint(20, 85, size=n),
    })

    with tempfile.TemporaryDirectory() as tmp_dir:
        plot_path = Path(tmp_dir) / "test_calibration.png"
        out = plot_reliability_diagram(y_true, probs_uncal, probs_cal, output_path=plot_path)
        assert out.is_file()
        assert out.stat().st_size > 1000

        fairness_path = Path(tmp_dir) / "test_fairness.json"
        rep = compute_subgroup_fairness(df_test, probs_cal, output_path=fairness_path, n_bootstrap=50)
        assert fairness_path.is_file()
        assert "gender_M" in rep["subgroups"]
        assert "gender_F" in rep["subgroups"]
        assert "age_under_65" in rep["subgroups"]
        assert "disclaimer" in rep["metadata"]

