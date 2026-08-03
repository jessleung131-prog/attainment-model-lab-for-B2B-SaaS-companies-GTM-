"""Decision-focused validation and guardrail checks."""
from __future__ import annotations
import numpy as np
import pandas as pd


def segment_error_report(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dimension in ["region"]:
        for value, group in predictions.groupby(dimension):
            error = group.predicted_bookings_m - group.bookings_m
            rows.append({
                "dimension": dimension, "segment": value, "rows": len(group),
                "mae_m": float(error.abs().mean()), "bias_m": float(error.mean()),
                "wmape": float(error.abs().sum() / max(group.bookings_m.abs().sum(), 1e-9)),
            })
    return pd.DataFrame(rows)


def carving_balance_report(audit: pd.DataFrame, prefix: str) -> dict[str, float]:
    before = audit[f"before_{prefix}"].to_numpy(float)
    after = audit[f"after_{prefix}"].to_numpy(float)
    before_cv = float(np.std(before) / max(np.mean(before), 1e-9))
    after_cv = float(np.std(after) / max(np.mean(after), 1e-9))
    return {
        "before_cv": before_cv, "after_cv": after_cv,
        "improvement_pct": float((before_cv - after_cv) / max(before_cv, 1e-9)),
    }


def quota_controls(quota: pd.DataFrame, required_total_m: float) -> dict[str, float | bool]:
    allocated = float(quota.recommended_quota_m.sum())
    return {
        "required_total_m": required_total_m,
        "allocated_total_m": allocated,
        "difference_m": required_total_m - allocated,
        "reconciled": abs(required_total_m - allocated) < 1e-6,
        "pct_below_70_attainment": float((quota.expected_attainment < .70).mean()),
    }
