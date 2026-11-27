"""Cached Bio_ClinicalBERT states + trainable/frozen last encoder block (Phase 3, RQ1/RQ2).

Running all 12 BERT layers for every epoch does not fit a 4 GB laptop GPU for the
number of runs in the analysis plan. Layers 1-11 are always frozen in this study, so
their output is computed once per note variant and cached with variable length. The
last encoder block (``BertTail``) is then run on the fly:

* frozen tail  -> identical to ``AutoModel(...).last_hidden_state`` (verified: max
  absolute difference 0.0), i.e. the "frozen backbone" regime of Phase 2;
* trainable tail -> "fine-tune the last encoder block", the Phase 1 text-baseline regime.

This makes the frozen vs fine-tuned comparison of text-only and fusion models fair.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import torch
from torch import Tensor, nn

from src.models.backbone_loader import DEFAULT_TEXT_MODEL, load_pretrained_text_backbone
from src.models.multimodal_fusion import AblationModel


@dataclass
class TextStates:
    """Variable-length layer-11 states for a list of notes (fp16, CPU)."""

    flat: Tensor          # [sum(L_i), hidden]
    offsets: Tensor       # [n + 1]
    revision: str | None = None

    def __len__(self) -> int:
        return len(self.offsets) - 1

    def batch(self, indices: Sequence[int]) -> tuple[Tensor, Tensor]:
        lengths = [int(self.offsets[i + 1] - self.offsets[i]) for i in indices]
        width = max(lengths)
        hidden = torch.zeros(len(indices), width, self.flat.shape[1], dtype=self.flat.dtype)
        mask = torch.zeros(len(indices), width, dtype=torch.long)
        for row, (index, length) in enumerate(zip(indices, lengths)):
            start = int(self.offsets[index])
            hidden[row, :length] = self.flat[start:start + length]
            mask[row, :length] = 1
        return hidden, mask

    def subset(self, indices: Sequence[int]) -> "TextStates":
        pieces, offsets = [], [0]
        for index in indices:
            piece = self.flat[int(self.offsets[index]):int(self.offsets[index + 1])]
            pieces.append(piece)
            offsets.append(offsets[-1] + len(piece))
        return TextStates(torch.cat(pieces), torch.tensor(offsets), self.revision)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"flat": self.flat, "offsets": self.offsets, "revision": self.revision}, path)

    @classmethod
    def load(cls, path: Path) -> "TextStates":
        payload = torch.load(path, map_location="cpu", weights_only=True)
        return cls(payload["flat"], payload["offsets"], payload.get("revision"))


def load_backbone(device: torch.device, local_files_only: bool = True):
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(DEFAULT_TEXT_MODEL, local_files_only=local_files_only)
    backbone, revision = load_pretrained_text_backbone(DEFAULT_TEXT_MODEL, local_files_only=local_files_only)
    backbone.set_attn_implementation("eager") if hasattr(backbone, "set_attn_implementation") else None
    return tokenizer, backbone.to(device).eval(), revision


@torch.inference_mode()
def encode_layer11(notes: Sequence[str], tokenizer, backbone, device: torch.device,
                   max_length: int = 512, batch_size: int = 16, revision: str | None = None) -> TextStates:
    """Encode notes and keep the input of the last encoder block, unpadded, in fp16."""
    order = sorted(range(len(notes)), key=lambda i: len(notes[i]))  # length-bucketing for speed
    chunks: dict[int, Tensor] = {}
    for start in range(0, len(order), batch_size):
        idx = order[start:start + batch_size]
        batch = tokenizer([notes[i] for i in idx], padding=True, truncation=True,
                          max_length=max_length, return_tensors="pt")
        out = backbone(input_ids=batch["input_ids"].to(device),
                       attention_mask=batch["attention_mask"].to(device), output_hidden_states=True)
        h11 = out.hidden_states[-2].half().cpu()
        lengths = batch["attention_mask"].sum(1).tolist()
        for row, i in enumerate(idx):
            chunks[i] = h11[row, :lengths[row]].clone()
    pieces = [chunks[i] for i in range(len(notes))]
    offsets = torch.tensor([0] + [len(p) for p in pieces]).cumsum(0)
    return TextStates(torch.cat(pieces), offsets, revision)


class BertTail(nn.Module):
    """Copy of the last BERT encoder block; frozen or trainable."""

    def __init__(self, backbone: nn.Module, trainable: bool) -> None:
        super().__init__()
        self.layer = copy.deepcopy(backbone.encoder.layer[-1])
        self.trainable = trainable
        for parameter in self.layer.parameters():
            parameter.requires_grad_(trainable)

    def forward(self, h11: Tensor, mask: Tensor) -> Tensor:
        extended = (1.0 - mask[:, None, None, :].float()) * torch.finfo(torch.float32).min
        if self.trainable:
            out = self.layer(h11.float(), attention_mask=extended)
        else:
            self.layer.eval()
            with torch.no_grad():
                out = self.layer(h11.float(), attention_mask=extended)
        return out[0] if isinstance(out, (tuple, list)) else out


class TailedModel(nn.Module):
    """``BertTail`` (if the mode uses text) followed by a Phase 2 ``AblationModel``."""

    def __init__(self, mode: str, backbone: nn.Module | None, trainable_tail: bool = False,
                 **ablation_kwargs) -> None:
        super().__init__()
        self.mode = mode
        self.head_model = AblationModel(mode, **ablation_kwargs)
        self.tail = BertTail(backbone, trainable_tail) if mode != "tabular" else None

    def forward(self, numerical: Tensor, categorical: Tensor, h11: Tensor, mask: Tensor) -> Tensor:
        text = self.tail(h11, mask) if self.tail is not None else h11
        return self.head_model(numerical, categorical, text, mask)
