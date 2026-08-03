"""Financial-plan-first predictive quota allocation."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def allocate_enterprise_quota(
    capacity: pd.DataFrame,
    financial_plan_m: float,
    coverage_factor: float = 1.15,
    prior_quota_col: str = "prior_quota_m",
    max_change: float = 0.25,
    target_attainment: float = 0.80,
) -> pd.DataFrame:
    """Minimize quota-difficulty dispersion under plan and change constraints."""
    required = {"territory_id", "expected_bookings_m", prior_quota_col}
    missing = required.difference(capacity.columns)
    if missing:
        raise ValueError(f"Quota input missing {sorted(missing)}")
    total_quota = financial_plan_m * coverage_factor
    expected = capacity["expected_bookings_m"].to_numpy(float)
    prior = capacity[prior_quota_col].to_numpy(float)
    lower = np.maximum(0.05, prior * (1 - max_change))
    upper = prior * (1 + max_change)

    # If strict change bands cannot reconcile to plan, relax them proportionally.
    if lower.sum() > total_quota or upper.sum() < total_quota:
        weights = np.maximum(expected, 0.01) / np.maximum(expected.sum(), 0.01)
        lower = np.minimum(lower, total_quota * weights * 0.85)
        upper = np.maximum(upper, total_quota * weights * 1.15)

    initial = total_quota * np.maximum(expected, 0.01) / np.maximum(expected.sum(), 0.01)
    initial = np.clip(initial, lower, upper)
    initial *= total_quota / initial.sum()

    def objective(quota: np.ndarray) -> float:
        attainment = expected / np.maximum(quota, 1e-6)
        fairness = np.mean((attainment - target_attainment) ** 2)
        change_penalty = np.mean(((quota - prior) / np.maximum(prior, 0.05)) ** 2)
        return float(fairness + 0.08 * change_penalty)

    solution = minimize(
        objective, initial, method="SLSQP", bounds=list(zip(lower, upper)),
        constraints=[{"type": "eq", "fun": lambda q: q.sum() - total_quota}],
        options={"maxiter": 1000, "ftol": 1e-10},
    )
    if not solution.success:
        raise RuntimeError(f"Quota optimization failed: {solution.message}")
    result = capacity.copy()
    result["recommended_quota_m"] = solution.x
    result["expected_attainment"] = expected / solution.x
    result["attainment_low"] = result["capacity_low_m"] / solution.x
    result["attainment_high"] = result["capacity_high_m"] / solution.x
    result["quota_change_pct"] = solution.x / prior - 1
    result["decision"] = np.select(
        [result["expected_attainment"] < 0.70, result["expected_attainment"] < 0.85],
        ["Rebalance", "Review"], default="Approve",
    )
    result["plan_control_m"] = total_quota - result["recommended_quota_m"].sum()
    return result.sort_values("expected_attainment")

