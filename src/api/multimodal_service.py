"""Lazy, checkpoint-backed research inference for the multimodal API."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import torch

from src.models.calibration import TemperatureScalingCalibrator
from src.models.multimodal_fusion import AblationModel


DEFAULT_CHECKPOINT = Path(__file__).resolve().parents[2] / "data/checkpoints/multimodal_best.pt"


@lru_cache(maxsize=1)
def load_multimodal_artifacts():
    """Load only local model assets; never silently instantiate random text weights."""
    from transformers import AutoModel, AutoTokenizer

    checkpoint_path = Path(os.getenv("MCDSS_CHECKPOINT", str(DEFAULT_CHECKPOINT)))
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Multimodal checkpoint unavailable: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    config = checkpoint["model_config"]
    model = AblationModel(mode=checkpoint["model_mode"], **config)
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.eval()

    text_model = checkpoint["text_model"]
    tokenizer = AutoTokenizer.from_pretrained(text_model, local_files_only=True)
    backbone = AutoModel.from_pretrained(text_model, local_files_only=True).eval()
    calibrator = TemperatureScalingCalibrator(float(checkpoint["temperature"])).eval()
    return checkpoint, model, tokenizer, backbone, calibrator


def predict_checkpoint(tabular_features: dict, deidentified_note: str) -> tuple[dict, list[float]]:
    checkpoint, model, tokenizer, backbone, calibrator = load_multimodal_artifacts()
    preprocessing = checkpoint["preprocessing"]
    numerical = torch.tensor(
        [[
            (float(tabular_features[name]) - float(preprocessing["scaler_mean"][index]))
            / float(preprocessing["scaler_scale"][index])
            for index, name in enumerate(preprocessing["numerical_features"])
        ]],
        dtype=torch.float32,
    )
    categorical = torch.tensor(
        [[
            next(
                (index + 1 for index, value in enumerate(preprocessing["category_values"][name])
                 if str(tabular_features[name]) == str(value)),
                0,
            )
            for name in preprocessing["categorical_features"]
        ]],
        dtype=torch.long,
    )
    tokens = tokenizer(
        deidentified_note,
        padding="max_length",
        truncation=True,
        max_length=int(checkpoint["max_length"]),
        return_tensors="pt",
    )
    with torch.inference_mode():
        hidden = backbone(
            input_ids=tokens["input_ids"], attention_mask=tokens["attention_mask"]
        ).last_hidden_state
        logits = model(numerical, categorical, hidden, tokens["attention_mask"])
        probabilities = calibrator.predict_proba(logits)[0].tolist()
    return checkpoint, probabilities
