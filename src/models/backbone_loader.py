"""Fail-fast loading of pretrained text backbones (Phase 3 / Backlog 08 – M1 task 1.1).

Before Phase 3, three code paths silently fell back to ``AutoModel.from_config`` when
pretrained weights were not cached, producing randomly initialised BERT embeddings
and meaningless metrics. Every caller must now go through this module: missing
weights raise, and a random backbone is only possible with an explicit flag that is
meant for unit tests.
"""

from __future__ import annotations

from pathlib import Path

from torch import nn

DEFAULT_TEXT_MODEL = "emilyalsentzer/Bio_ClinicalBERT"


class MissingPretrainedWeightsError(RuntimeError):
    """Raised when a pretrained backbone is requested but its weights are unavailable."""


def resolve_backbone_revision(model_name: str) -> str | None:
    """Return the Hugging Face cache snapshot hash used for ``model_name``, if cached."""
    try:
        from huggingface_hub import try_to_load_from_cache
    except ImportError:  # pragma: no cover - huggingface_hub ships with transformers
        return None
    for filename in ("config.json", "model.safetensors", "pytorch_model.bin"):
        cached = try_to_load_from_cache(model_name, filename)
        if isinstance(cached, str):
            return Path(cached).parent.name
    return None


def load_pretrained_text_backbone(model_name: str = DEFAULT_TEXT_MODEL, *,
                                  local_files_only: bool = False,
                                  allow_random_backbone: bool = False) -> tuple[nn.Module, str | None]:
    """Load ``AutoModel.from_pretrained(model_name)`` or raise.

    Returns ``(backbone, revision)``. ``allow_random_backbone=True`` instantiates the
    architecture from its config with random weights; it exists only for offline unit
    tests and must never be used for reported results.
    """
    from transformers import AutoConfig, AutoModel

    try:
        backbone = AutoModel.from_pretrained(model_name, local_files_only=local_files_only)
        return backbone, resolve_backbone_revision(model_name)
    except (OSError, ValueError) as exc:
        if not allow_random_backbone:
            raise MissingPretrainedWeightsError(
                f"Pretrained weights for '{model_name}' are unavailable ({exc}). "
                f"Download them first, e.g. `huggingface-cli download {model_name}`. "
                "Random initialisation is disabled for research runs."
            ) from exc
    config = AutoConfig.from_pretrained(model_name, local_files_only=local_files_only)
    return AutoModel.from_config(config), "RANDOM_INIT_TEST_ONLY"
