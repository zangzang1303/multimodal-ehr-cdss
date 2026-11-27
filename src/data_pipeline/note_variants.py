"""Clinical-note variants for the text-signal decomposition (RQ2) and the controlled
complementarity simulation (RQ3). Pre-registered in docs/11_ANALYSIS_PLAN.md, Appendix A.

All functions are pure and deterministic so every model sees identical inputs.
"""

from __future__ import annotations

import hashlib
import re
from typing import Callable

import numpy as np

NUMBER = re.compile(r"\d+(?:[.,]\d+)?")
SECTION = re.compile(r"^([A-Z][A-Z /&()-]{3,}):\s*$", re.MULTILINE)
VITAL_TOKENS = re.compile(r"\b(BP|HR|RR|SpO2|Temp|WBC|CRP|Smoking Status|Comorbidities)\b\s*:", re.IGNORECASE)
NARRATIVE_SECTIONS = ("CHIEF COMPLAINT", "HISTORY OF PRESENT ILLNESS", "MEDICATIONS")


def split_sections(note: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (preamble, [(header, body), ...]) using ``HEADER:`` lines as boundaries."""
    matches = list(SECTION.finditer(note))
    if not matches:
        return note, []
    preamble = note[:matches[0].start()]
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(note)
        sections.append((match.group(1), note[match.end():end]))
    return preamble, sections


def mask_numbers(note: str) -> str:
    """Replace every number with ``<NUM>`` (variant ``num_masked``)."""
    return NUMBER.sub("<NUM>", note)


def _drop_vital_fragments(text: str) -> str:
    kept_lines = []
    for line in text.splitlines():
        if VITAL_TOKENS.search(line) and NUMBER.search(line):
            # Template notes write vitals inline in one sentence; drop that sentence only.
            sentences = re.split(r"(?<=[.])\s+", line)
            sentences = [s for s in sentences if not (VITAL_TOKENS.search(s) and NUMBER.search(s))]
            line = " ".join(sentences)
        kept_lines.append(line)
    return "\n".join(kept_lines)


def remove_vitals(note: str) -> str:
    """Drop the VITALS block and every vital-sign/lab fragment that carries a number."""
    preamble, sections = split_sections(note)
    parts = [_drop_vital_fragments(preamble)]
    for header, body in sections:
        if header.startswith("VITALS"):
            continue
        parts.append(f"{header}:{_drop_vital_fragments(body)}")
    return "".join(parts)


def narrative_only(note: str) -> str:
    """Keep only CHIEF COMPLAINT, HISTORY OF PRESENT ILLNESS and MEDICATIONS."""
    _, sections = split_sections(note)
    kept = [f"{header}:{body.rstrip()}" for header, body in sections if header in NARRATIVE_SECTIONS]
    return "\n\n".join(kept).strip() or "No narrative available."


VARIANTS: dict[str, Callable[[str], str]] = {
    "full": lambda note: note,
    "num_masked": mask_numbers,
    "no_vitals": remove_vitals,
    "narrative_only": narrative_only,
}


# --- RQ3 controlled complementarity simulation -------------------------------------
# Class-specific cue sentences paraphrased from the diagnostic criteria in GINA 2024,
# GOLD 2024, ESC 2023 and the Vietnamese MoH CAP guideline (see data/guidelines/).
CUE_LEXICON: dict[int, tuple[str, ...]] = {
    0: ("Reports episodic wheeze triggered by allergens and exercise.",
        "Symptoms improve markedly after an inhaled bronchodilator.",
        "Night-time cough with variable airflow limitation.",
        "Known atopy with seasonal allergic rhinitis since childhood."),
    1: ("Long-standing productive cough with slowly progressive exertional dyspnoea.",
        "Heavy smoking history with persistent, poorly reversible airflow limitation.",
        "Barrel chest and prolonged expiratory phase on examination.",
        "Recurrent winter exacerbations previously treated with oral steroids."),
    2: ("Orthopnoea and paroxysmal nocturnal dyspnoea for several nights.",
        "Bilateral pitting ankle oedema and raised jugular venous pressure.",
        "Third heart sound and bibasal fine crackles on auscultation.",
        "Weight gain over the past week with reduced exercise tolerance."),
    3: ("Fever with purulent sputum and pleuritic chest pain since yesterday.",
        "Focal crackles and bronchial breathing over the right lower zone.",
        "Acute onset of rigors with productive cough.",
        "Dullness to percussion over the affected lung field."),
}


def _unit(key: str, salt: str) -> float:
    digest = hashlib.sha256(f"{salt}|{key}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16 ** 12)


def inject_cue(note: str, label: int, patient_id: str, rho: float, epsilon: float = 0.1,
               seed: int = 0) -> str:
    """Insert one class cue at the start of the HPI for a deterministic fraction ``rho``
    of patients; with probability ``epsilon`` the cue comes from a different class."""
    if _unit(patient_id, f"rho{seed}") >= rho:
        return note
    cue_class = int(label)
    if _unit(patient_id, f"eps{seed}") < epsilon:
        others = [c for c in CUE_LEXICON if c != cue_class]
        cue_class = others[int(_unit(patient_id, f"wrong{seed}") * len(others)) % len(others)]
    options = CUE_LEXICON[cue_class]
    cue = options[int(_unit(patient_id, f"pick{seed}") * len(options)) % len(options)]
    marker = "HISTORY OF PRESENT ILLNESS:"
    if marker in note:
        return note.replace(marker, f"{marker}\n{cue}", 1)
    return f"{cue}\n{note}"


def add_tabular_noise(values: np.ndarray, train_sd: np.ndarray, sigma: float,
                      seed: int = 0) -> np.ndarray:
    """Add N(0, (sigma * SD_train)^2) noise column-wise (RQ3 weaker tabular signal)."""
    if sigma <= 0:
        return values.copy()
    rng = np.random.default_rng(seed)
    return values + rng.normal(0.0, 1.0, size=values.shape) * (sigma * train_sd)
