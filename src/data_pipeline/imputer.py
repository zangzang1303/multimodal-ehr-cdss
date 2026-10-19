"""
MOCK FILE - DO THÀNH VIÊN 3 TẠO MOCK ĐỂ PHỤC VỤ TEST / PHÁT TRIỂN
CẦN THAY THẾ (TODO: REPLACE WITH MEMBER 2'S ACTUAL IMPLEMENTATION IN SPRINT)
Mô tả: Module gán dữ liệu khuyết MICE (BayesianRidge IterativeImputer) + Binary Missingness Indicator
Tuân thủ: PROBAST Domain 2 (MAR assumption preservation)
"""

from typing import Dict, List
import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.linear_model import BayesianRidge


class ClinicalImputer:
    """
    Mock implementation of ClinicalImputer (MICE) for testing and development.
    - Imputes numerical features via IterativeImputer (Chained Equations with Bayesian Ridge).
    - Imputes categorical features using mode (SimpleImputer most_frequent).
    - Preserves clinical signal by adding binary indicators '{col}_is_missing' (0 or 1).
    """

    def __init__(self, max_iter: int = 10, random_state: int = 42):
        self.max_iter = max_iter
        self.random_state = random_state
        self.numeric_cols: List[str] = []
        self.cat_cols: List[str] = []
        self.missing_cols: List[str] = []

        self.mice_imputer = IterativeImputer(
            estimator=BayesianRidge(),
            max_iter=self.max_iter,
            random_state=self.random_state,
            initial_strategy="mean",
        )
        self.cat_imputer = SimpleImputer(strategy="most_frequent")
        self.is_fitted = False

    def fit(self, X: pd.DataFrame) -> "ClinicalImputer":
        """
        Fit imputers on the training set.
        """
        self.numeric_cols = list(X.select_dtypes(include=[np.number]).columns)
        self.cat_cols = [c for c in X.columns if c not in self.numeric_cols]
        # Identify columns that have missing values
        self.missing_cols = [col for col in X.columns if X[col].isna().any()]

        if self.numeric_cols:
            self.mice_imputer.fit(X[self.numeric_cols])

        if self.cat_cols:
            self.cat_imputer.fit(X[self.cat_cols])

        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform DataFrame by imputing missing values and appending binary indicators.
        """
        if not self.is_fitted:
            self.fit(X)

        df_out = X.copy()

        # 1. Add binary indicator columns for missingness
        # For any column that had missing values in X (or identified during fit)
        cols_to_indicate = set(self.missing_cols).union(
            [col for col in X.columns if X[col].isna().any()]
        )
        for col in cols_to_indicate:
            if col in X.columns:
                df_out[f"{col}_is_missing"] = X[col].isna().astype(int)

        # 2. Impute numeric columns via MICE
        if self.numeric_cols:
            imputed_num = self.mice_imputer.transform(X[self.numeric_cols])
            df_out[self.numeric_cols] = imputed_num

        # 3. Impute categorical columns via Most Frequent
        if self.cat_cols:
            imputed_cat = self.cat_imputer.transform(X[self.cat_cols])
            df_out[self.cat_cols] = imputed_cat

        return df_out

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Fit imputers and transform in a single call.
        """
        return self.fit(X).transform(X)

    def get_missingness_report(self, X: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate the percentage of missing values per column.
        """
        return {col: float(X[col].isna().mean() * 100) for col in X.columns}


# Alias for compatibility with PHASE_1_DETAILED_CODE_AND_DATA_SPEC.md
ClinicalMICEImputer = ClinicalImputer
