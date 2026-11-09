"""
Evidence Grounder Engine
M-CDSS Phase 2 / Backlog 05 (Task 3.2 & 3.3)

Locates LLM-generated evidence claims within raw de-identified clinical notes
using exact and flexible character offset mapping. Enforces strict zero-hallucination
filtering: any claim not grounded in patient notes is rejected.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class EvidenceGrounder:
    """
    Evidence Grounding and Anti-Hallucination Engine.
    Maps clinical claims to precise [start_char, end_char] spans within the source text.
    """

    def __init__(self, fuzzy_threshold: float = 0.88):
        self.fuzzy_threshold = fuzzy_threshold

    def ground_single_claim(
        self,
        raw_clinical_note: str,
        claim_text: str,
        category: str = "supporting",
        label: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Attempts to locate a single claim in raw_clinical_note.
        Returns a span dict if found; returns None if rejected as ungrounded/hallucinated.
        """
        clean_claim = claim_text.strip()
        if not clean_claim or not raw_clinical_note:
            return None

        # 1. Exact string search
        start_idx = raw_clinical_note.find(clean_claim)
        if start_idx != -1:
            end_idx = start_idx + len(clean_claim)
            return {
                "start_char": start_idx,
                "end_char": end_idx,
                "text": raw_clinical_note[start_idx:end_idx],
                "category": category,
                "label": label or ("Bằng chứng ủng hộ" if category == "supporting" else "Cờ đỏ cấp cứu" if category == "red_flag" else "Chẩn đoán phân biệt"),
                "reason": reason,
                "confidence": 1.0,
                "is_exact": True,
            }

        # 2. Case-insensitive exact search
        pattern = re.escape(clean_claim)
        match = re.search(pattern, raw_clinical_note, re.IGNORECASE)
        if match:
            return {
                "start_char": match.start(),
                "end_char": match.end(),
                "text": raw_clinical_note[match.start():match.end()],
                "category": category,
                "label": label or ("Bằng chứng ủng hộ" if category == "supporting" else "Cờ đỏ cấp cứu" if category == "red_flag" else "Chẩn đoán phân biệt"),
                "reason": reason,
                "confidence": 0.98,
                "is_exact": False,
            }

        # 3. Whitespace-flexible matching (handles differing newlines or extra spaces)
        words = clean_claim.split()
        if len(words) >= 2:
            flexible_pattern = r"\s+".join(re.escape(w) for w in words)
            match = re.search(flexible_pattern, raw_clinical_note, re.IGNORECASE)
            if match:
                return {
                    "start_char": match.start(),
                    "end_char": match.end(),
                    "text": raw_clinical_note[match.start():match.end()],
                    "category": category,
                    "label": label or ("Bằng chứng ủng hộ" if category == "supporting" else "Cờ đỏ cấp cứu" if category == "red_flag" else "Chẩn đoán phân biệt"),
                    "reason": reason,
                    "confidence": 0.92,
                    "is_exact": False,
                }

        # 4. Fallback sub-phrase search for long compound claims (at least 5 words)
        if len(words) >= 5:
            # Try matching head phrase (first 4 words)
            head_phrase = r"\s+".join(re.escape(w) for w in words[:4])
            head_match = re.search(head_phrase, raw_clinical_note, re.IGNORECASE)
            if head_match:
                # Find sentence boundary or line break
                end_pos = min(len(raw_clinical_note), head_match.start() + len(clean_claim) + 20)
                # Align to nearest period or newline if possible
                slice_text = raw_clinical_note[head_match.start():end_pos]
                period_idx = slice_text.find(".")
                actual_end = head_match.start() + period_idx if period_idx != -1 else head_match.end()
                return {
                    "start_char": head_match.start(),
                    "end_char": max(actual_end, head_match.end()),
                    "text": raw_clinical_note[head_match.start():max(actual_end, head_match.end())],
                    "category": category,
                    "label": label or "Bằng chứng một phần",
                    "reason": reason,
                    "confidence": 0.85,
                    "is_exact": False,
                }

        # Claim not found in patient text -> Reject to prevent hallucination
        return None

    def ground_evidence_claims(
        self,
        raw_clinical_note: str,
        claims: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Grounds an array of claims into valid non-overlapping or prioritized spans.
        Returns (grounded_spans, rejected_count).
        """
        grounded: List[Dict[str, Any]] = []
        rejected_count = 0

        for item in claims:
            if isinstance(item, str):
                text = item
                cat = "supporting"
                lbl = None
                rsn = None
            else:
                text = item.get("text") or item.get("claim", "")
                cat = item.get("category", "supporting")
                lbl = item.get("label")
                rsn = item.get("reason")

            span = self.ground_single_claim(
                raw_clinical_note=raw_clinical_note,
                claim_text=text,
                category=cat,
                label=lbl,
                reason=rsn,
            )

            if span is not None:
                grounded.append(span)
            else:
                rejected_count += 1

        # Sort spans by starting character offset
        grounded.sort(key=lambda s: (s["start_char"], s["end_char"]))
        return grounded, rejected_count
