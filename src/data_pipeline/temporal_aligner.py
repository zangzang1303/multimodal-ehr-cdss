from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Set
import pandas as pd

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )


class TemporalAligner:

    GOLD_STANDARD_BLACKLIST: Set[str] = {
        "fev1",
        "fvc",
        "fev1_fvc_ratio",
        "fev1_fvc",
        "tiffeneau_ratio",
        "tiffeneau",
        "lvef",
        "ef",
        "ejection_fraction",
        "bnp",
        "nt_pro_bnp",
        "bnp_pro_bnp",
        "pro_bnp",
        "sputum_culture_bacteria",
        "sputum_culture_pathogen",
        "sputum_culture",
        "antibiotic_sensitivity",
    }

    EXCLUDED_GOLD_STANDARDS = GOLD_STANDARD_BLACKLIST

    def __init__(self, custom_blacklist: Iterable[str] | None = None) -> None:
        """
        Initialize TemporalAligner.

        Args:
            custom_blacklist: Optional additional or overridden blacklist column/feature names.
        """
        self.blacklist: Set[str] = {item.lower() for item in self.GOLD_STANDARD_BLACKLIST}
        if custom_blacklist:
            self.blacklist.update(item.lower() for item in custom_blacklist)

    def filter_events_by_time(
        self,
        events_df: pd.DataFrame,
        event_time_col: str,
        diag_time_col: str,
    ) -> pd.DataFrame:
        """
        Strictly time-locks events by keeping only events where event_time < diag_time.
        Any event with event_time >= diag_time is purged as target leakage.

        Args:
            events_df: Input DataFrame containing event timelines.
            event_time_col: Name of event timestamp column.
            diag_time_col: Name of diagnostic confirmation timestamp column.

        Returns:
            pd.DataFrame: Filtered DataFrame containing only strictly pre-diagnostic records.
        """
        if events_df.empty:
            return events_df.copy()

        if event_time_col not in events_df.columns:
            raise KeyError(f"Event timestamp column '{event_time_col}' not found in DataFrame.")
        if diag_time_col not in events_df.columns:
            raise KeyError(f"Diagnostic timestamp column '{diag_time_col}' not found in DataFrame.")

        df = events_df.copy()

        # Convert to datetime if not already
        t_event = pd.to_datetime(df[event_time_col], errors="coerce")
        t_diag = pd.to_datetime(df[diag_time_col], errors="coerce")

        invalid_event_mask = t_event.isna()
        invalid_diag_mask = t_diag.isna()

        if invalid_event_mask.any():
            logger.warning(
                "Found %d rows with unparseable event timestamp in '%s'.",
                invalid_event_mask.sum(),
                event_time_col,
            )
        if invalid_diag_mask.any():
            logger.warning(
                "Found %d rows with unparseable diagnostic timestamp in '%s'.",
                invalid_diag_mask.sum(),
                diag_time_col,
            )

        valid_time_mask = (t_event < t_diag) & (~invalid_event_mask) & (~invalid_diag_mask)
        dropped_count = len(df) - valid_time_mask.sum()

        if dropped_count > 0:
            logger.warning(
                "TemporalAligner: Purged %d / %d records occurring at or after diagnosis timestamp "
                "(t_event >= t_diag) to prevent target leakage.",
                dropped_count,
                len(df),
            )

        return df[valid_time_mask].reset_index(drop=True)

    def is_blacklisted(self, column_name: str) -> bool:
        """Check if a given column name matches the Gold-Standard Blacklist."""
        col_normalized = str(column_name).strip().lower()
        return col_normalized in self.blacklist or any(
            col_normalized == bl
            or col_normalized.startswith(f"{bl}_")
            or col_normalized.endswith(f"_{bl}")
            for bl in self.blacklist
        )

    def detect_gold_standard_leakage(self, df: pd.DataFrame) -> List[str]:
        """Alias for check_gold_standard_leakage for contract compatibility."""
        return self.check_gold_standard_leakage(df)

    def check_gold_standard_leakage(self, df: pd.DataFrame) -> List[str]:

        detected: List[str] = []
        for col in df.columns:
            col_normalized = str(col).strip().lower()
            if col_normalized in self.blacklist or any(
                col_normalized == bl
                or col_normalized.startswith(f"{bl}_")
                or col_normalized.endswith(f"_{bl}")
                for bl in self.blacklist
            ):
                detected.append(col)
        return detected

    def remove_gold_standard_leakage(self, df: pd.DataFrame) -> pd.DataFrame:

        leaking_cols = self.check_gold_standard_leakage(df)
        if leaking_cols:
            logger.warning(
                "TemporalAligner: Detected and removed %d gold-standard leakage column(s): %s",
                len(leaking_cols),
                leaking_cols,
            )
            return df.drop(columns=leaking_cols).copy()
        return df.copy()

    @classmethod
    def filter_features(
        cls, events: List[Dict[str, Any]], confirmed_diag_time: str
    ) -> List[Dict[str, Any]]:

        diag_dt = pd.to_datetime(confirmed_diag_time)
        valid_events: List[Dict[str, Any]] = []

        for event in events:
            raw_ts = event.get("timestamp")
            if raw_ts is None:
                continue
            event_dt = pd.to_datetime(raw_ts)

            if event_dt < diag_dt:
                feature_name = str(event.get("feature_name", "")).strip().lower()
                if feature_name not in cls.GOLD_STANDARD_BLACKLIST:
                    valid_events.append(event)
                else:
                    logger.warning(
                        "filter_features: Dropped blacklisted gold-standard feature '%s'.",
                        feature_name,
                    )
            else:
                logger.warning(
                    "filter_features: Dropped post-diagnosis event at %s (diag: %s).",
                    event_dt,
                    diag_dt,
                )

        return valid_events
