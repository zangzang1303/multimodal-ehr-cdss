"""Behavioral checks for the Phase 2 Member 1 model interfaces."""

import pytest
import torch
from torch.nn import functional as F

from src.models.calibration import TemperatureScalingCalibrator
from src.models.multimodal_fusion import AblationModel, CrossAttentionFusion
from src.models.tabular_encoder import FTTransformerEncoder, TabularTokenizer


def test_tokenizer_and_encoder_shapes_and_gradients():
    numerical = torch.randn(3, 9)
    categorical = torch.tensor([[1, 2, 1, 2], [3, 0, 2, 1], [0, 1, 0, 0]])
    tokenizer = TabularTokenizer()
    assert tokenizer(numerical, categorical).shape == (3, 14, 128)
    encoder = FTTransformerEncoder(n_blocks=2)
    encoded = encoder(numerical, categorical)
    assert encoded.shape == (3, 14, 128)
    encoded.sum().backward()
    assert encoder.tokenizer.numeric_weight.grad is not None
    with pytest.raises(ValueError):
        tokenizer(numerical, torch.full_like(categorical, 99))


def test_cross_attention_ignores_padding_and_handles_missing_text():
    torch.manual_seed(3)
    model = CrossAttentionFusion(dropout=0).eval()
    tab = torch.randn(2, 14, 128)
    text = torch.randn(2, 5, 128)
    mask = torch.tensor([[1, 1, 0, 0, 0], [0, 0, 0, 0, 0]])
    present = torch.tensor([True, False])
    original = model(tab, text, mask, text_present=present)
    changed = text.clone()
    changed[:, 2:] += 1000
    changed[1] += 1000
    updated = model(tab, changed, mask, text_present=present)
    assert torch.allclose(original, updated, atol=1e-5)
    with pytest.raises(ValueError):
        model(tab, text, mask, tabular_present=torch.tensor([False, False]), text_present=torch.tensor([False, False]))


@pytest.mark.parametrize("mode", AblationModel.MODES)
def test_all_ablation_modes_backpropagate(mode):
    model = AblationModel(mode, text_width=16, d_token=32, n_blocks=1, n_heads=4)
    numerical = torch.randn(2, 9)
    categorical = torch.ones(2, 4, dtype=torch.long)
    hidden = torch.randn(2, 6, 16)
    mask = torch.tensor([[1, 1, 1, 0, 0, 0], [1, 1, 0, 0, 0, 0]])
    logits = model(numerical, categorical, hidden, mask)
    assert logits.shape == (2, 4)
    F.cross_entropy(logits, torch.tensor([0, 1])).backward()
    assert any(p.grad is not None for p in model.parameters())


def test_temperature_uses_validation_logits_and_roundtrips_state():
    logits = torch.tensor([[8.0, 0.0], [8.0, 0.0], [0.0, 8.0], [0.0, 8.0]])
    labels = torch.tensor([0, 1, 1, 0])
    calibrator = TemperatureScalingCalibrator().fit(logits, labels)
    assert calibrator.temperature > 1
    before = F.cross_entropy(logits, labels)
    after = F.cross_entropy(calibrator(logits), labels)
    assert after < before
    assert torch.allclose(calibrator.predict_proba(logits).sum(1), torch.ones(4))
    restored = TemperatureScalingCalibrator()
    restored.load_state_dict(calibrator.state_dict())
    assert torch.allclose(restored(logits), calibrator(logits))
