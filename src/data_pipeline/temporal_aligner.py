"""
MOCK FILE - DO THÀNH VIÊN 3 TẠO MOCK ĐỂ PHỤC VỤ TEST / PHÁT TRIỂN
CẦN THAY THẾ (TODO: REPLACE WITH MEMBER 2'S ACTUAL IMPLEMENTATION IN SPRINT)
Mô tả: Module khóa chuỗi thời gian & chống rò rỉ nhãn (Gold-Standard Blacklist)
Tuân thủ: PROBAST Domain 2 & Domain 3
"""

from typing import List, Optional
import pandas as pd


class TemporalAligner:
    """
    Mock implementation of TemporalAligner for testing and system development.
    - Locks clinical events strictly before diagnostic confirmation (t_event < t_diag).
    - Removes or flags Gold-Standard Target Leakage variables (e.g. FEV1, LVEF, Sputum culture).
    """

    GOLD_STANDARD_BLACKLIST: List[str] = [
        "fev1",
        "fvc",
        "fev1_fvc_ratio",
        "tiffeneau_ratio",       # Gold standard for Asthma/COPD (GOLD guidelines)
        "lvef",
        "ef",
        "ejection_fraction",     # Gold standard for Heart Failure (ESC guidelines)
        "sputum_culture_bacteria",
        "antibiotic_sensitivity",  # Gold standard for Pneumonia
    ]

    def __init__(self, custom_blacklist: Optional[List[str]] = None):
        self.blacklist = [item.lower() for item in self.GOLD_STANDARD_BLACKLIST]
        if custom_blacklist:
            self.blacklist.extend([item.lower() for item in custom_blacklist])

    def filter_events_by_time(
        self,
        events_df: pd.DataFrame,
        event_time_col: str = "event_time",
        diag_time_col: str = "diag_time",
    ) -> pd.DataFrame:
        """
        Filter out any clinical record/event where t_event >= t_diag.
        Preserves only events occurring strictly before diagnosis confirmation: t_event < t_diag.
        """
        if events_df.empty:
            return events_df.copy()

        df = events_df.copy()
        t_event = pd.to_datetime(df[event_time_col])
        t_diag = pd.to_datetime(df[diag_time_col])

        # Strictly exclude events at or after diagnosis time
        valid_mask = t_event < t_diag
        return df.loc[valid_mask].reset_index(drop=True)

    def is_blacklisted(self, column_name: str) -> bool:
        """
        Check if a given column name matches the Gold-Standard Blacklist.
        """
        col_lower = column_name.lower().strip()
        return any(b == col_lower or b in col_lower for b in self.blacklist)

    def detect_gold_standard_leakage(self, df: pd.DataFrame) -> List[str]:
        """
        Detect any columns in the DataFrame that belong to the Gold-Standard Blacklist.
        """
        return [col for col in df.columns if self.is_blacklisted(col)]

    def remove_gold_standard_leakage(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove any blacklisted columns from the input DataFrame to prevent target leakage.
        """
        leaking_cols = self.detect_gold_standard_leakage(df)
        if leaking_cols:
            return df.drop(columns=leaking_cols)
        return df.copy()
