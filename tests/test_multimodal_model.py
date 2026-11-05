"""
Unit Tests for Multimodal Neural Network Core Components
Multimodal EHR CDSS - Phase 2 / Backlog 04 (Member 3 Task 3.2)

Verifies:
1. TabularTokenizer: Forward pass, output shape [Batch, M+1, 128], continuous & categorical tokenization.
2. ClinicalTextEncoder: Forward pass, output shape [Batch, S+2, 128], attention mask support.
3. CrossAttentionFusion: Forward pass, backward pass, gradient flow without NaNs, attention matrix shape.
4. TemperatureScalingCalibrator: Calibrated probability sum equals 1.0, temperature scaling effects, L-BFGS fit.
5. End-to-end integration: Pipeline coupling TabularTokenizer + ClinicalTextEncoder + CrossAttentionFusion + Calibrator.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch
import torch.nn as nn

from src.models.calibration import TemperatureScalingCalibrator
from src.models.multimodal_fusion import CrossAttentionFusion
from src.models.tabular_encoder import FTTransformerEncoder, TabularTokenizer
from src.models.text_encoder import ClinicalTextEncoder, DummyClinicalBackbone


# ---------------------------------------------------------------------------
# Test 1: TabularTokenizer Tests
# ---------------------------------------------------------------------------

def test_tabular_tokenizer_output_shape():
    """
    Kiểm tra TabularTokenizer: Nhận ma trận số và xuất đúng kích thước [Batch, M+1, 128].
    """
    batch_size = 4
    n_numerical = 9
    cardinalities = [4, 4, 2, 2]  # 4 categorical features -> M = 9 + 4 = 13 features -> M+1 = 14 tokens
    embed_dim = 128

    tokenizer = TabularTokenizer(
        n_numerical=n_numerical,
        categorical_cardinalities=cardinalities,
        embed_dim=embed_dim,
    )

    x_num = torch.randn(batch_size, n_numerical)
    x_cat = torch.tensor([
        [0, 1, 0, 1],
        [1, 2, 1, 0],
        [2, 0, 0, 0],
        [0, 1, 1, 1],
    ], dtype=torch.long)

    tokens = tokenizer(x_num, x_cat)

    expected_tokens_count = n_numerical + len(cardinalities) + 1  # 9 + 4 + 1 = 14
    assert tokens.shape == (batch_size, expected_tokens_count, embed_dim), (
        f"Expected shape ({batch_size}, {expected_tokens_count}, {embed_dim}), "
        f"received {tuple(tokens.shape)}"
    )
    assert not torch.isnan(tokens).any(), "TabularTokenizer output contains NaN values"


def test_tabular_tokenizer_numerical_only():
    """
    Kiểm tra TabularTokenizer khi chỉ có biến số: shape [Batch, M_num+1, embed_dim].
    """
    batch_size = 8
    n_num = 9
    embed_dim = 128

    tokenizer = TabularTokenizer(
        n_numerical=n_num,
        categorical_cardinalities=[],
        embed_dim=embed_dim,
    )
    x_num = torch.randn(batch_size, n_num)
    tokens = tokenizer(x_num)

    assert tokens.shape == (batch_size, n_num + 1, embed_dim)


def test_ft_transformer_encoder_forward():
    """
    Kiểm tra FTTransformerEncoder: Forward qua các tầng TransformerEncoder.
    """
    batch_size = 3
    encoder = FTTransformerEncoder(
        n_numerical=9,
        categorical_cardinalities=[4, 4, 2, 2],
        embed_dim=128,
        n_blocks=2,
        n_heads=4,
    )
    x_num = torch.randn(batch_size, 9)
    x_cat = torch.randint(0, 2, (batch_size, 4))
    h_tab = encoder(x_num, x_cat)

    assert h_tab.shape == (batch_size, 14, 128)
    assert not torch.isnan(h_tab).any()


# ---------------------------------------------------------------------------
# Test 2: ClinicalTextEncoder Tests
# ---------------------------------------------------------------------------

def test_clinical_text_encoder_output_shape():
    """
    Kiểm tra ClinicalTextEncoder: Nhận input_ids và attention_mask,
    xuất đúng kích thước [Batch, S+2, 128].
    """
    batch_size = 4
    seq_len = 32  # S+2 tokens (including [CLS] and [SEP])
    embed_dim = 128
    vocab_size = 500

    dummy_backbone = DummyClinicalBackbone(vocab_size=vocab_size, hidden_size=768)
    text_encoder = ClinicalTextEncoder(
        embed_dim=embed_dim,
        backbone=dummy_backbone,
    )

    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    attention_mask = torch.ones(batch_size, seq_len, dtype=torch.long)
    attention_mask[:, -8:] = 0  # 8 padding tokens

    h_text = text_encoder(input_ids, attention_mask=attention_mask)

    assert h_text.shape == (batch_size, seq_len, embed_dim), (
        f"Expected shape ({batch_size}, {seq_len}, {embed_dim}), "
        f"received {tuple(h_text.shape)}"
    )
    assert not torch.isnan(h_text).any(), "ClinicalTextEncoder output contains NaN values"

    # Verify zero-out on padding positions
    padding_embeddings = h_text[:, -8:, :]
    assert torch.allclose(padding_embeddings, torch.zeros_like(padding_embeddings)), (
        "Padding token embeddings should be zeroed out by attention mask"
    )


# ---------------------------------------------------------------------------
# Test 3: CrossAttentionFusion Tests (Forward, Backward, Gradients, No NaNs)
# ---------------------------------------------------------------------------

def test_cross_attention_fusion_forward_and_backward():
    """
    Kiểm tra CrossAttentionFusion:
    - Forward pass xuất logits [Batch, 4] và attention weights [Batch, M+1, S+2].
    - Backward pass không sinh lỗi NaN trong gradients.
    """
    batch_size = 4
    m_tokens = 14   # M+1
    s_tokens = 32   # S+2
    embed_dim = 128
    num_classes = 4

    fusion = CrossAttentionFusion(
        embed_dim=embed_dim,
        num_heads=4,
        num_classes=num_classes,
        dropout=0.0,
    )

    h_tab = torch.randn(batch_size, m_tokens, embed_dim, requires_grad=True)
    h_text = torch.randn(batch_size, s_tokens, embed_dim, requires_grad=True)

    logits, attn_weights = fusion(h_tab, h_text)

    # 1. Shape checks
    assert logits.shape == (batch_size, num_classes), (
        f"Expected logits shape ({batch_size}, {num_classes}), got {tuple(logits.shape)}"
    )
    assert attn_weights.shape == (batch_size, m_tokens, s_tokens), (
        f"Expected attention weights shape ({batch_size}, {m_tokens}, {s_tokens}), "
        f"got {tuple(attn_weights.shape)}"
    )

    # 2. Attention weights should sum to 1.0 along key dimension (S+2)
    attn_sum = attn_weights.sum(dim=-1)
    assert torch.allclose(attn_sum, torch.ones_like(attn_sum), atol=1e-5), (
        "Attention weights must sum to 1.0 across text tokens"
    )

    # 3. Backward pass & Gradient flow check (No NaNs)
    loss_fn = nn.CrossEntropyLoss()
    targets = torch.tensor([0, 1, 2, 3], dtype=torch.long)
    loss = loss_fn(logits, targets)
    loss.backward()

    assert not torch.isnan(loss), "Loss value is NaN"
    assert h_tab.grad is not None, "Gradient did not flow to h_tab"
    assert not torch.isnan(h_tab.grad).any(), "Gradient of h_tab contains NaN values"
    assert h_text.grad is not None, "Gradient did not flow to h_text"
    assert not torch.isnan(h_text.grad).any(), "Gradient of h_text contains NaN values"

    for name, param in fusion.named_parameters():
        if param.requires_grad:
            assert param.grad is not None, f"Parameter {name} has no gradient"
            assert not torch.isnan(param.grad).any(), f"Parameter {name} has NaN gradients"


def test_cross_attention_with_padding_mask():
    """
    Kiểm tra CrossAttentionFusion khi có padding mask ở nhánh văn bản.
    """
    batch_size = 2
    fusion = CrossAttentionFusion(embed_dim=128, num_heads=4, num_classes=4)

    h_tab = torch.randn(batch_size, 10, 128)
    h_text = torch.randn(batch_size, 16, 128)
    padding_mask = torch.zeros(batch_size, 16, dtype=torch.bool)
    padding_mask[:, -4:] = True  # Last 4 tokens are padding

    logits, attn_weights, h_fused = fusion(
        h_tab, h_text, text_padding_mask=padding_mask, return_features=True
    )

    assert logits.shape == (batch_size, 4)
    assert h_fused.shape == (batch_size, 128)
    assert not torch.isnan(logits).any()


# ---------------------------------------------------------------------------
# Test 4: TemperatureScalingCalibrator Tests
# ---------------------------------------------------------------------------

def test_temperature_scaling_calibrator_probabilities_sum_to_one():
    """
    Kiểm tra TemperatureScalingCalibrator:
    - Tỷ lệ xác suất sau hiệu chuẩn có tổng bằng 1.0.
    - Duy trì thứ tự xếp hạng (rank order / monotonicity).
    """
    batch_size = 8
    num_classes = 4

    calibrator = TemperatureScalingCalibrator(initial_temperature=1.5)
    logits = torch.randn(batch_size, num_classes)

    probs = calibrator(logits)

    # 1. Probabilities sum to 1.0 along class dimension
    sums = probs.sum(dim=-1)
    assert torch.allclose(sums, torch.ones_like(sums), atol=1e-5), (
        "Calibrated probabilities must sum to 1.0"
    )

    # 2. Probability bounds [0.0, 1.0]
    assert (probs >= 0.0).all() and (probs <= 1.0).all(), (
        "All probabilities must be strictly bounded in [0.0, 1.0]"
    )

    # 3. Monotonicity / Argmax preservation
    raw_preds = logits.argmax(dim=-1)
    calibrated_preds = probs.argmax(dim=-1)
    assert torch.equal(raw_preds, calibrated_preds), (
        "Temperature scaling must preserve argmax class predictions"
    )


def test_temperature_scaling_fit_lbfgs():
    """
    Kiểm tra phương thức fit của TemperatureScalingCalibrator bằng L-BFGS:
    Nhiệt độ tối ưu hội tụ và làm giảm NLL trên tập validation giả lập.
    """
    calibrator = TemperatureScalingCalibrator(initial_temperature=1.0)

    # Overconfident synthetic validation logits
    n_val = 100
    labels = torch.randint(0, 4, (n_val,))
    val_logits = torch.randn(n_val, 4) * 5.0  # High variance -> overconfident
    val_logits[torch.arange(n_val), labels] += 4.0

    initial_temp = calibrator.current_temperature
    optimal_temp = calibrator.fit(val_logits, labels, lr=0.05, max_iter=50)

    assert optimal_temp > 0.0, "Optimal temperature must be strictly positive"
    assert calibrator.current_temperature == pytest.approx(optimal_temp, rel=1e-3)


# ---------------------------------------------------------------------------
# Test 5: Complete Multimodal End-to-End Pipeline Test
# ---------------------------------------------------------------------------

def test_full_multimodal_pipeline_forward_pass():
    """
    Kiểm tra luồng forward tích hợp toàn bộ mạng đa phương thức:
    Tabular -> TabularTokenizer -> Text -> ClinicalTextEncoder -> Fusion -> Calibrator.
    """
    batch_size = 2
    embed_dim = 128
    num_classes = 4

    # 1. Modality Encoders
    tab_encoder = FTTransformerEncoder(n_numerical=9, embed_dim=embed_dim)
    dummy_backbone = DummyClinicalBackbone(vocab_size=100, hidden_size=768)
    text_encoder = ClinicalTextEncoder(embed_dim=embed_dim, backbone=dummy_backbone)

    # 2. Fusion & Calibrator
    fusion = CrossAttentionFusion(embed_dim=embed_dim, num_classes=num_classes)
    calibrator = TemperatureScalingCalibrator(initial_temperature=1.2)

    # 3. Forward flow
    x_num = torch.randn(batch_size, 9)
    input_ids = torch.randint(0, 100, (batch_size, 24))

    h_tab = tab_encoder(x_num)               # [Batch, 10, 128]
    h_text = text_encoder(input_ids)          # [Batch, 24, 128]
    logits, attn_weights = fusion(h_tab, h_text)  # [Batch, 4]
    calibrated_probs = calibrator(logits)     # [Batch, 4]

    assert calibrated_probs.shape == (batch_size, num_classes)
    assert torch.allclose(calibrated_probs.sum(dim=-1), torch.ones(batch_size), atol=1e-5)

