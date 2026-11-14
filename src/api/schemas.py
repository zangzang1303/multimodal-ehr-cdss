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


class TopKPrediction(BaseModel):
    """
    Individual pathology prediction with probability score and calibrated risk tier.
    """

    disease: str = Field(..., description="Canonical disease identifier")
    disease_name: str = Field(..., description="Vietnamese clinical display name")
    probability: float = Field(..., ge=0.0, le=1.0, description="Calibrated probability (0.0 to 1.0)")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Formatted probability percentage")
    risk_level: Literal["low", "moderate", "high"] = Field(
        ...,
        description="Clinical risk level: low (<30%), moderate (30-70%), high (>70%)",
    )


class ModalityStreamResult(BaseModel):
    """
    Diagnostic prediction for an individual or fused modality stream.
    """

    stream_name: str = Field(..., description="Name of the stream (Tabular, Text, Cross-Attention Fusion)")
    predicted_disease: str = Field(..., description="Predicted diagnosis")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class MultimodalMockResponse(BaseModel):
    """
    Comprehensive response for Phase 2 Multimodal Core mock prediction endpoint.
    Includes top predicted pathology, calibrated probability, Top-K ranked list,
    and cross-modal comparison for DiagnosticCard component.
    """

    patient_id: str = Field(..., description="Patient identifier")
    prediction_source: Literal["mock", "checkpoint"] = Field(default="mock")
    model_version: Optional[str] = Field(default=None)
    predicted_disease: str = Field(..., description="Top predicted disease label")
    predicted_disease_name: str = Field(..., description="Vietnamese display name of top predicted disease")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Top-1 simulated score")
    calibrated: bool = Field(default=False, description="Whether a fitted validation calibrator was applied")
    temperature: Optional[float] = Field(default=None, description="Fitted validation temperature, if available")
    ece_score: Optional[float] = Field(default=None, description="Measured ECE, if available")
    top_k_predictions: List[TopKPrediction] = Field(
        ...,
        description="Ranked list of Top-K diseases by calibrated probability",
    )
    modality_streams: Dict[str, ModalityStreamResult] = Field(
        default_factory=dict,
        description="Predictions from individual streams (Tabular, Text) vs Multimodal Fusion",
    )
    fusion_gate_weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Dynamic attention gate weights (g_tab vs g_text)",
    )
    timestamp: str = Field(..., description="ISO 8601 prediction timestamp")



class EvidenceSpan(BaseModel):
    """
    Spans of characters within raw clinical text grounded to supporting evidence.
    """
    start_char: int = Field(..., ge=0, description="Start index in raw patient clinical notes")
    end_char: int = Field(..., ge=0, description="End index in raw patient clinical notes")
    text: str = Field(..., description="Exact substring matched within the note")
    category: Literal["supporting", "counter", "red_flag"] = Field(
        default="supporting",
        description="Category of evidence: supporting top-1 diagnosis, counter/differential, or red-flag emergency",
    )
    label: str = Field(..., description="Human-readable badge label (e.g., 'Bằng chứng ủng hộ', 'Dấu hiệu cờ đỏ')")
    reason: Optional[str] = Field(default=None, description="Clinical reason or guideline criteria why this text is significant")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Grounding confidence")
    is_exact: bool = Field(default=True, description="Whether matched exactly or via normalized regex")


class GuidelineReference(BaseModel):
    """
    Referenced snippet from clinical practice guidelines (GINA, GOLD, ESC, BYT).
    """
    chunk_id: str = Field(..., description="Unique chunk identifier")
    source_id: str = Field(default="", description="Stable source document identifier")
    version: str = Field(default="", description="Source edition or year")
    section_locator: str = Field(default="", description="Section or page locator")
    source_verified: bool = Field(default=False, description="Whether source metadata was verified")
    guideline_source: str = Field(..., description="Guideline name (GOLD 2024, GINA 2024, ESC 2023, BYT 2020)")
    disease_entity: str = Field(..., description="Disease entity (COPD, ASTHMA, HEART_FAILURE, PNEUMONIA)")
    section_title: str = Field(..., description="Guideline section header")
    clinical_category: str = Field(..., description="Category (DIAGNOSTIC_CRITERIA, DIFFERENTIAL_DIAGNOSIS, RED_FLAG)")
    evidence_level: str = Field(default="Level_A", description="Clinical evidence level (Level A, B, C)")
    text_content: str = Field(..., description="Authoritative clinical guidance text snippet")
    relevance_score: Optional[float] = Field(default=1.0, description="Relevance ranking score")


class AgentExplainRequest(BaseModel):
    """
    Request payload to trigger Multi-Agent Clinical Differential Consultation and Evidence Grounding.
    """
    patient_id: str = Field(default="PT-001", description="Patient identifier")
    clinical_notes: str = Field(..., min_length=5, description="Raw or de-identified clinical notes text")
    target_diagnosis: Optional[str] = Field(default=None, description="Optional primary hypothesis to audit (e.g. COPD, ASTHMA)")
    differential_diagnosis: Optional[str] = Field(default=None, description="Optional secondary hypothesis to compare against")
    calibrated_probabilities: Optional[Dict[str, float]] = Field(default=None, description="Optional map of calibrated probabilities")


class AgentExplainResponse(BaseModel):
    """
    Comprehensive output payload of the Agentic RAG Clinical Consultation.
    """
    patient_id: str = Field(..., description="Patient identifier")
    display_note: str = Field(..., description="De-identified note used for all evidence offsets")
    primary_diagnosis: str = Field(..., description="Primary suspected diagnosis (Hypothesis 1)")
    primary_diagnosis_name: str = Field(..., description="Vietnamese display name of primary diagnosis")
    differential_diagnosis: Optional[str] = Field(default=None, description="Secondary differential diagnosis (Hypothesis 2)")
    differential_diagnosis_name: Optional[str] = Field(default=None, description="Vietnamese display name of differential diagnosis")
    differential_reasoning: str = Field(..., description="Chain-of-thought clinical differential justification")
    grounded_spans: List[EvidenceSpan] = Field(
        default_factory=list,
        description="List of verified character offsets in patient note for frontend highlighting",
    )
    guideline_references: List[GuidelineReference] = Field(
        default_factory=list,
        description="Relevant clinical practice guideline chunks retrieved via Hybrid RAG",
    )
    red_flags: List[str] = Field(default_factory=list, description="Clinical red-flag alerts requiring emergency attention")
    recommended_investigations: List[str] = Field(
        default_factory=list,
        description="Recommended next diagnostic tests per guideline (e.g. Spirometry, NT-proBNP, CXR)",
    )
    hallucination_filtered_count: int = Field(default=0, description="Number of unsupported claims filtered out to ensure 0% hallucination")
    execution_time_ms: float = Field(default=0.0, description="Execution time in milliseconds")
