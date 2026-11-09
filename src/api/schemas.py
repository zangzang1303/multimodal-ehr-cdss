"""
Core Pydantic v2 Schemas for Multimodal EHR CDSS
Defines Data Contracts for Tabular Features, Clinical Notes, and Baseline Predictions.
Aligned with configs/data_schema.yaml
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class GenderEnum(str, Enum):
    M = "M"
    F = "F"
    OTHER = "OTHER"


class SmokingStatusEnum(str, Enum):
    NEVER = "NEVER"
    FORMER = "FORMER"
    CURRENT = "CURRENT"


class DiseaseLabel(str, Enum):
    ASTHMA = "ASTHMA"
    COPD = "COPD"
    CONGESTIVE_HEART_FAILURE = "CONGESTIVE_HEART_FAILURE"
    COMMUNITY_ACQUIRED_PNEUMONIA = "COMMUNITY_ACQUIRED_PNEUMONIA"


class TabularFeatures(BaseModel):
    """
    Validation schema for 9 continuous vital signs/lab results and 4 categorical variables.
    Values outside physiological ranges are rejected.
    """

    # 9 Continuous Features
    age: int = Field(
        ...,
        ge=18,
        le=110,
        description="Patient age in years (18-110)",
        examples=[65],
    )
    systolic_bp: float = Field(
        ...,
        ge=60.0,
        le=240.0,
        description="Systolic Blood Pressure in mmHg (60-240)",
        examples=[135.0],
    )
    diastolic_bp: float = Field(
        ...,
        ge=40.0,
        le=140.0,
        description="Diastolic Blood Pressure in mmHg (40-140)",
        examples=[85.0],
    )
    heart_rate: float = Field(
        ...,
        ge=30.0,
        le=220.0,
        description="Resting heart rate in beats per minute (30-220)",
        examples=[88.0],
    )
    respiratory_rate: float = Field(
        ...,
        ge=8.0,
        le=50.0,
        description="Respiratory rate in breaths per minute (8-50)",
        examples=[22.0],
    )
    spo2: float = Field(
        ...,
        ge=60.0,
        le=100.0,
        description="Blood oxygen saturation percentage (60-100)",
        examples=[93.0],
    )
    temperature: float = Field(
        ...,
        ge=35.0,
        le=42.0,
        description="Body temperature in Celsius (35.0-42.0)",
        examples=[38.4],
    )
    wbc_count: float = Field(
        ...,
        ge=1.0,
        le=50.0,
        description="White blood cell count in 10^9/L (1.0-50.0)",
        examples=[14.2],
    )
    crp: float = Field(
        ...,
        ge=0.0,
        le=300.0,
        description="C-Reactive Protein in mg/L (0.0-300.0)",
        examples=[48.5],
    )

    # 4 Categorical Features
    gender: Literal["M", "F", "OTHER"] = Field(
        ...,
        description="Patient biological / administrative sex",
        examples=["M"],
    )
    smoking_status: Literal["NEVER", "FORMER", "CURRENT"] = Field(
        ...,
        description="Smoking status",
        examples=["FORMER"],
    )
    history_hypertension: Literal[0, 1] = Field(
        ...,
        description="History of hypertension (0: No, 1: Yes)",
        examples=[1],
    )
    history_diabetes: Literal[0, 1] = Field(
        ...,
        description="History of diabetes mellitus (0: No, 1: Yes)",
        examples=[0],
    )

    @model_validator(mode="after")
    def validate_blood_pressure(self) -> "TabularFeatures":
        """Validate systolic BP is greater than diastolic BP."""
        if self.systolic_bp <= self.diastolic_bp:
            raise ValueError(
                f"Systolic BP ({self.systolic_bp}) must be greater than Diastolic BP ({self.diastolic_bp})"
            )
        return self


class ClinicalNoteInput(BaseModel):
    """
    Validation schema for unstructured clinical progress notes.
    """

    patient_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Unique patient identifier (e.g., PT-0001)",
        examples=["PT-0001"],
    )
    encounter_timestamp: str = Field(
        ...,
        min_length=1,
        description="ISO 8601 encounter timestamp (e.g. 2026-09-10T08:30:00)",
        examples=["2026-09-10T08:30:00"],
    )
    raw_text: str = Field(
        ...,
        min_length=5,
        description="Clinical text notes including history of present illness and physical exam",
        examples=["Patient presents with acute onset dyspnea, wheezing on expiration, and cough."],
    )

    @field_validator("encounter_timestamp")
    @classmethod
    def validate_timestamp_format(cls, v: str) -> str:
        """Validate that the encounter timestamp is a valid ISO format string."""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(f"encounter_timestamp '{v}' is not a valid ISO 8601 format timestamp")
        return v


class BaselinePredictionResult(BaseModel):
    """
    Schema for single baseline model prediction outcome.
    Includes disease prediction, probability score, baseline identifier, and per-class breakdown.
    """

    baseline_name: str = Field(
        ...,
        description="Name of the baseline model executing inference",
        examples=["XGBoost", "FT-Transformer", "Bio_ClinicalBERT"],
    )
    disease_name: DiseaseLabel = Field(
        ...,
        description="Predicted diagnosis class",
        examples=["COMMUNITY_ACQUIRED_PNEUMONIA"],
    )
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Prediction probability / confidence score (0.0 to 1.0)",
        examples=[0.884],
    )
    probabilities: Optional[Dict[str, float]] = Field(
        default=None,
        description="Probability distribution across all 4 target pathologies",
        examples=[
            {
                "ASTHMA": 0.02,
                "COPD": 0.05,
                "CONGESTIVE_HEART_FAILURE": 0.046,
                "COMMUNITY_ACQUIRED_PNEUMONIA": 0.884,
            }
        ],
    )
    model_version: Optional[str] = Field(
        default="1.0.0-phase1",
        description="Model checkpoint or artifact version",
    )


class BaselineModelResult(BaseModel):
    """
    Result for an individual baseline model.
    """

    predicted_class: str = Field(..., description="Predicted disease class label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model prediction confidence score")


class PatientInferenceRequest(BaseModel):
    """
    Request payload for baseline inference containing tabular features and optional clinical note.
    """

    patient_id: str = Field(
        default="PT-001",
        description="Patient unique identifier",
        examples=["PT-001"],
    )
    tabular_features: TabularFeatures = Field(
        ...,
        description="Continuous vital signs and categorical indicators",
    )
    clinical_notes: Optional[str] = Field(
        default="",
        description="Unstructured clinical notes / free text",
        examples=["Patient presents with cough and dyspnea..."],
    )


class PatientInferenceResponse(BaseModel):
    """
    Response payload returning predictions across the 3 baseline models.
    """

    patient_id: str = Field(..., description="Patient identifier")
    baseline_results: Dict[str, BaselineModelResult] = Field(
        ...,
        description="Results from 3 baseline models: classical_tabular, tabular_deep, text_only",
    )


# ---------------------------------------------------------
# Agentic RAG & Explainability Schemas (Backlog 05 - Member 2)
# ---------------------------------------------------------

class EvidenceSpan(BaseModel):
    """
    Character offset span mapped onto the active de-identified clinical note.
    Guarantees note[start:end] == text.
    """
    text: str = Field(..., description="Exact substring slice from clinical note")
    start: int = Field(..., ge=0, description="Start character offset index")
    end: int = Field(..., ge=0, description="End character offset index")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Span confidence score")
    match_type: str = Field(default="exact", description="Match type: exact, case_insensitive, normalized, fuzzy_candidate")


class ClaimAudit(BaseModel):
    """
    Validation audit of a clinical claim produced by the agent.
    """
    claim: str = Field(..., description="Clinical claim or assertion text")
    status: Literal["verified", "candidate", "unverified"] = Field(
        default="unverified",
        description="Claim grounding verification status",
    )
    spans: list[EvidenceSpan] = Field(default_factory=list, description="Grounding spans in note")
    confidence: float = Field(default=0.0, description="Overall verification confidence")
    match_type: str = Field(default="none", description="Resolution strategy")
    clinical_interpretation_note: Optional[str] = Field(
        default=None,
        description="Explicit note separating character offset tracking from clinical interpretation",
    )
    reason: Optional[str] = Field(default=None, description="Rejection reason if unverified")


class GuidelineCitation(BaseModel):
    """
    Digitalized clinical practice guideline excerpt cited by the RAG system.
    """
    chunk_id: str = Field(..., description="Unique chunk identifier")
    source_id: str = Field(..., description="Guideline source authority: GINA_2024, GOLD_2024, ESC_2023, BYT_VN_CAP_2020")
    version: str = Field(..., description="Guideline official version/year")
    target_disease: str = Field(..., description="Target disease entity")
    section_title: str = Field(..., description="Guideline section or table header")
    page_or_section: str = Field(..., description="Page or chapter reference")
    clinical_category: str = Field(..., description="Category: DIAGNOSTIC_CRITERIA, DIFFERENTIAL, RED_FLAGS, etc.")
    evidence_level: Optional[str] = Field(default=None, description="Evidence grade (e.g. Evidence A/Level_A) if stated")
    text_content: str = Field(..., description="Full text excerpt from official guideline")


class AgentExplainRequest(BaseModel):
    """
    Payload for POST /api/v1/agent/explain.
    Accepts de-identified clinical note (S) and optional model probabilities.
    Treats client-supplied patient_id and target_diagnosis as untrusted.
    """
    clinical_note: str = Field(
        ...,
        min_length=10,
        description="De-identified clinical note (S) displayed to the clinician",
        examples=["Bệnh nhân khó thở tăng dần, tiền sử hút thuốc lá 35 bao-năm, FEV1/FVC = 0.58..."],
    )
    patient_id: Optional[str] = Field(
        default="ANON_PATIENT",
        description="Untrusted client identifier",
    )
    target_diagnosis: Optional[str] = Field(
        default=None,
        description="Client-suggested diagnosis label (treated as unverified input, not ground truth)",
    )
    calibrated_probabilities: Optional[Dict[str, float]] = Field(
        default=None,
        description="Calibrated probability distribution from multimodal model",
    )
    tabular_features: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional physiological vitals and lab measurements",
    )


class AgentExplainResponse(BaseModel):
    """
    Output payload for POST /api/v1/agent/explain.
    Contains grounded claims, character spans, and guideline citations.
    """
    status: Literal["success", "insufficient_evidence", "error"] = Field(
        default="success",
        description="Overall endpoint execution status",
    )
    patient_id: str = Field(..., description="Echoed patient identifier")
    top1_diagnosis: str = Field(..., description="Primary hypothesis H1")
    top2_diagnosis: Optional[str] = Field(default=None, description="Differential hypothesis H2")
    differential_reasoning: str = Field(..., description="Structured clinical differential rationale")
    pro_evidence_claims: list[str] = Field(default_factory=list, description="Claims supporting H1")
    counter_evidence_claims: list[str] = Field(default_factory=list, description="Claims supporting H2 or refuting H1")
    red_flags: list[str] = Field(default_factory=list, description="Emergency red flags detected")
    verified_spans: list[EvidenceSpan] = Field(
        default_factory=list,
        description="Offset spans mapped onto clinical_note for UI highlighting",
    )
    claim_audits: list[ClaimAudit] = Field(
        default_factory=list,
        description="Complete verification audit for each claim",
    )
    guideline_citations: list[GuidelineCitation] = Field(
        default_factory=list,
        description="Verifiable clinical guidelines with official IDs and sections",
    )
    has_insufficient_evidence: bool = Field(
        default=False,
        description="Flag set when guideline sources cannot be retrieved or claims lack grounding",
    )
    warning: Optional[str] = Field(
        default=None,
        description="Clinical cautionary warning (e.g., untrusted client label ignored or missing guideline chunks)",
    )

