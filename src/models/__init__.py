"""Model implementations for M-CDSS (Phase 1 Baselines & Phase 2 Multimodal Core)."""

from src.models.baselines import (
    ClassicalTabularBaseline,
    TabularDeepBaseline,
    TextOnlyBaseline,
)
from src.models.calibration import TemperatureScalingCalibrator
from src.models.multimodal_fusion import CrossAttentionFusion
from src.models.tabular_encoder import FTTransformerEncoder, TabularTokenizer
from src.models.text_encoder import ClinicalTextEncoder

__all__ = [
    "ClassicalTabularBaseline",
    "TabularDeepBaseline",
    "TextOnlyBaseline",
    "TabularTokenizer",
    "FTTransformerEncoder",
    "ClinicalTextEncoder",
    "CrossAttentionFusion",
    "TemperatureScalingCalibrator",
]
