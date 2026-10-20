"""
Core Pydantic v2 Schemas for Multimodal EHR CDSS
Defines Data Contracts for Tabular Features, Clinical Notes, and Baseline Predictions.
Aligned with configs/data_schema.yaml
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Literal, Optional
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
