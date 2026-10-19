

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Sequence, Union

import numpy as np
import pandas as pd

# Explicitly enable IterativeImputer from sklearn.experimental
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.linear_model import BayesianRidge

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class ClinicalImputer:
  

    def __init__(
        self,
        max_iter: int = 10,
        random_state: int = 42,
        numerical_cols: Optional[Sequence[str]] = None,
        categorical_cols: Optional[Sequence[str]] = None,
        create_indicators: bool = True,
        estimator: Any = None,
    ) -> None:
       
        self.max_iter = max_iter
        self.random_state = random_state
        self.user_numerical_cols = list(numerical_cols) if numerical_cols is not None else None
        self.user_categorical_cols = list(categorical_cols) if categorical_cols is not None else None
        self.create_indicators = create_indicators

        self.regressor = estimator if estimator is not None else BayesianRidge()

        self.num_imputer = IterativeImputer(
            estimator=self.regressor,
            max_iter=self.max_iter,
            random_state=self.random_state,
            sample_posterior=False,
            skip_complete=True,
            initial_strategy="median",
        )

        self.cat_imputer = SimpleImputer(strategy="most_frequent")

        self.fitted_numerical_cols: List[str] = []
        self.fitted_categorical_cols: List[str] = []
        self.is_fitted: bool = False
        self._initial_missing_stats: Dict[str, float] = {}

    def _infer_column_types(self, df: pd.DataFrame) -> tuple[List[str], List[str]]:
      
        excluded = {col for col in df.columns if col.endswith("_is_missing")}

        if self.user_numerical_cols is not None:
            num_cols = [c for c in self.user_numerical_cols if c in df.columns]
        else:
            num_cols = [
                c
                for c in df.select_dtypes(include=[np.number]).columns
                if c not in excluded
            ]

        if self.user_categorical_cols is not None:
            cat_cols = [c for c in self.user_categorical_cols if c in df.columns]
        else:
            cat_cols = [
                c
                for c in df.columns
                if c not in num_cols and c not in excluded
            ]

        return num_cols, cat_cols

    def fit(self, X: pd.DataFrame, y: Any = None) -> "ClinicalImputer":
      
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        self.fitted_numerical_cols, self.fitted_categorical_cols = self._infer_column_types(X)

     
        self._initial_missing_stats = {
            col: float(X[col].isna().mean()) for col in X.columns
        }

       
        if self.fitted_numerical_cols:
            num_df = X[self.fitted_numerical_cols]
            self.num_imputer.fit(num_df)

       
        if self.fitted_categorical_cols:
            cat_df = X[self.fitted_categorical_cols]
          
            self.cat_imputer.fit(cat_df)

        self.is_fitted = True
        logger.info(
            "ClinicalImputer fitted successfully on %d numerical and %d categorical features.",
            len(self.fitted_numerical_cols),
            len(self.fitted_categorical_cols),
        )
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
      
        if not self.is_fitted:
            raise RuntimeError("ClinicalImputer must be fitted before calling transform().")

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        out_df = X.copy()

        if self.create_indicators:
        
            indicator_targets = self.fitted_numerical_cols + self.fitted_categorical_cols
            for col in indicator_targets:
                if col in out_df.columns:
                    indicator_col = f"{col}_is_missing"
                  
                    out_df[indicator_col] = out_df[col].isna().astype(int)

      
        if self.fitted_numerical_cols:
            cols_to_impute = [c for c in self.fitted_numerical_cols if c in out_df.columns]
            if cols_to_impute:
                num_imputed = self.num_imputer.transform(out_df[cols_to_impute])
          
                if np.isnan(num_imputed).any():
                    num_imputed = np.nan_to_num(num_imputed, nan=0.0)
                out_df[cols_to_impute] = num_imputed

     
        if self.fitted_categorical_cols:
            cols_to_impute = [c for c in self.fitted_categorical_cols if c in out_df.columns]
            if cols_to_impute:
                cat_imputed = self.cat_imputer.transform(out_df[cols_to_impute])
                out_df[cols_to_impute] = cat_imputed

        
        remaining_nans = out_df.isna().sum().sum()
        if remaining_nans > 0:
            logger.warning("ClinicalImputer: %d residual NaNs detected; filling with forward/backward fill.", remaining_nans)
            out_df = out_df.ffill().bfill().fillna(0)

        return out_df

    def fit_transform(
        self,
        X: pd.DataFrame,
        y: Any = None,
        numerical_cols: Optional[Sequence[str]] = None,
    ) -> pd.DataFrame:
       
        if numerical_cols is not None:
            self.user_numerical_cols = list(numerical_cols)
        return self.fit(X, y).transform(X)

    def get_missingness_report(
        self,
        X_before: pd.DataFrame,
        X_after: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
      
        records = []
        total_rows = len(X_before)

        for col in X_before.columns:
            if col.endswith("_is_missing"):
                continue
            before_missing = int(X_before[col].isna().sum())
            before_pct = (before_missing / total_rows * 100.0) if total_rows > 0 else 0.0

            after_missing = 0
            after_pct = 0.0
            if X_after is not None and col in X_after.columns:
                after_missing = int(X_after[col].isna().sum())
                after_pct = (after_missing / len(X_after) * 100.0) if len(X_after) > 0 else 0.0

            records.append({
                "feature": col,
                "missing_before_count": before_missing,
                "missing_before_pct": round(before_pct, 2),
                "missing_after_count": after_missing,
                "missing_after_pct": round(after_pct, 2),
            })

        report_df = pd.DataFrame(records)
        return report_df.sort_values(by="missing_before_pct", ascending=False).reset_index(drop=True)



ClinicalMICEImputer = ClinicalImputer
TabularMICEImputer = ClinicalImputer
