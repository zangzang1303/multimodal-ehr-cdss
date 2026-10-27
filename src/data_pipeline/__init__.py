"""Data-pipeline public API.

Heavy training dependencies are imported lazily so the lightweight inference API
can start without loading pandas, scikit-learn, or PyTorch.
"""

from importlib import import_module
from typing import Any

from src.data_pipeline.deidentifier import ClinicalDeidentifier

__all__ = [
    "ClinicalDeidentifier",
    "TemporalAligner",
    "ClinicalImputer",
    "ClinicalMICEImputer",
    "TabularMICEImputer",
    "MultimodalEHRDataset",
    "create_patient_level_splits",
    "get_data_loaders",
    "process_and_save_patient_splits",
]


_LAZY_IMPORTS = {
    "TemporalAligner": ("src.data_pipeline.temporal_aligner", "TemporalAligner"),
    "ClinicalImputer": ("src.data_pipeline.imputer", "ClinicalImputer"),
    "ClinicalMICEImputer": ("src.data_pipeline.imputer", "ClinicalMICEImputer"),
    "TabularMICEImputer": ("src.data_pipeline.imputer", "TabularMICEImputer"),
    "MultimodalEHRDataset": ("src.data_pipeline.dataset_loader", "MultimodalEHRDataset"),
    "create_patient_level_splits": (
        "src.data_pipeline.dataset_loader",
        "create_patient_level_splits",
    ),
    "get_data_loaders": ("src.data_pipeline.dataset_loader", "get_data_loaders"),
    "process_and_save_patient_splits": (
        "src.data_pipeline.dataset_loader",
        "process_and_save_patient_splits",
    ),
}


def __getattr__(name: str) -> Any:
    """Load optional data/ML components only when callers request them."""
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attribute_name = _LAZY_IMPORTS[name]
    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value
