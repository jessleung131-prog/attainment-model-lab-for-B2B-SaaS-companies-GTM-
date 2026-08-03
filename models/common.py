"""Shared types, feature contracts, and evaluation utilities."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np
import pandas as pd

NUMERIC_FEATURES = [
    "account_potential_m", "starting_pipeline_m", "account_count",
    "rep_tenure_months", "historical_conversion", "industry_concentration",
]
CATEGORICAL_FEATURES = ["region", "quarter_of_year"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


@dataclass(frozen=True)
class ValidationMetrics:
    model_name: str
    train_through: str
    validation_period: str
    mae_m: float
    rmse_m: float
    wmape: float
    bias_m: float
    interval_coverage: float

    def to_dict(self) -> dict:
        return asdict(self)


def regression_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
) -> dict[str, float]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    error = predicted - actual
    return {
        "mae_m": float(np.mean(np.abs(error))),
        "rmse_m": float(np.sqrt(np.mean(error ** 2))),
        "wmape": float(np.abs(error).sum() / max(np.abs(actual).sum(), 1e-9)),
        "bias_m": float(error.mean()),
        "interval_coverage": float(np.mean((actual >= lower) & (actual <= upper))),
    }


def assert_point_in_time_contract(frame: pd.DataFrame) -> None:
    """Fail fast on fields that would create historical leakage."""
    required = set(FEATURES + ["territory_id", "quarter", "bookings_m", "snapshot_date"])
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing modeling fields: {sorted(missing)}")
    if frame.duplicated(["territory_id", "quarter"]).any():
        raise ValueError("Expected one row per territory × quarter")
    snapshot = pd.to_datetime(frame["snapshot_date"])
    quarter_start = pd.PeriodIndex(frame["quarter"], freq="Q").start_time
    if (snapshot > quarter_start).any():
        raise ValueError("Snapshot date occurs after the planning-period start")
    forbidden = {"final_stage", "current_owner", "future_pipeline_m", "closed_won_flag"}
    leaked = forbidden.intersection(frame.columns)
    if leaked:
        raise ValueError(f"Potential leakage fields present: {sorted(leaked)}")

