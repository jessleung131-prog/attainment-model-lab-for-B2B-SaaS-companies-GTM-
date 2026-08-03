"""Transparent reference implementation for the Attainment Model Lab.

The module demonstrates the separation of concerns used in the dashboard:

1. Predict attainable territory bookings from point-in-time features.
2. Allocate a fixed financial plan against predicted capacity.
3. Recommend Enterprise account moves subject to hard constraints.
4. Recommend Customer Success assignments using ARR and workload capacity.

All generated records are synthetic. The implementation favors readable,
auditable logic over production-scale optimization.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RNG_SEED = 42
NUMERIC_FEATURES = [
    "account_potential_m",
    "starting_pipeline_m",
    "account_count",
    "rep_tenure_months",
    "historical_conversion",
    "industry_concentration",
]
CATEGORICAL_FEATURES = ["region", "quarter"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


@dataclass(frozen=True)
class ModelMetrics:
    """Out-of-time model quality and simple decision diagnostics."""

    train_through: str
    validation_period: str
    mae_m: float
    wmape: float
    bias_m: float


@dataclass(frozen=True)
class CarvingRules:
    """Business constraints applied after predictive scoring."""

    max_account_movement_rate: float = 0.18
    max_accounts_per_territory: int = 24
    named_accounts_locked: bool = True
    late_stage_pipeline_locked: bool = True


def simulate_data(seed: int = RNG_SEED) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create synthetic history, Enterprise accounts, and CS accounts."""

    rng = np.random.default_rng(seed)
    territories = [f"ENT-{i:02d}" for i in range(1, 9)]
    regions = {t: ["East", "Central", "West"][(i - 1) % 3] for i, t in enumerate(territories, 1)}
    quarters = pd.period_range("2024Q1", "2025Q4", freq="Q")

    history_rows: list[dict] = []
    for territory_index, territory in enumerate(territories):
        territory_quality = rng.normal(0, 0.22)
        rep_effect = rng.normal(0, 0.15)
        for period_index, quarter in enumerate(quarters):
            potential = rng.uniform(5.0, 12.0)
            pipeline = rng.uniform(1.0, 4.0)
            account_count = int(rng.integers(12, 26))
            tenure = int(rng.integers(4, 72))
            conversion = rng.uniform(0.16, 0.38)
            concentration = rng.uniform(0.18, 0.62)
            seasonal = [0.00, 0.05, -0.03, 0.12][period_index % 4]
            bookings = (
                0.15 * potential
                + 0.42 * pipeline
                + 1.8 * conversion
                + 0.006 * min(tenure, 36)
                - 0.45 * concentration
                + territory_quality
                + rep_effect
                + seasonal
                + rng.normal(0, 0.18)
            )
            history_rows.append(
                {
                    "territory_id": territory,
                    "region": regions[territory],
                    "quarter": str(quarter),
                    "account_potential_m": round(potential, 3),
                    "starting_pipeline_m": round(pipeline, 3),
                    "account_count": account_count,
                    "rep_tenure_months": tenure,
                    "historical_conversion": round(conversion, 4),
                    "industry_concentration": round(concentration, 4),
                    "bookings_m": round(max(0.2, bookings), 3),
                }
            )

    industries = ["FinTech", "Cybersecurity", "Data", "Commerce", "HR"]
    account_rows: list[dict] = []
    for account_index in range(120):
        territory = territories[account_index % len(territories)]
        account_rows.append(
            {
                "account_id": f"ACC-{account_index + 1:04d}",
                "account_name": f"Simulated {industries[account_index % len(industries)]} {account_index + 1}",
                "territory_id": territory,
                "region": regions[territory],
                "industry": industries[account_index % len(industries)],
                "potential_m": round(rng.uniform(0.25, 2.1), 3),
                "pipeline_m": round(rng.uniform(0, 0.85), 3),
                "workload": int(rng.integers(1, 11)),
                "named_account": bool(rng.random() < 0.09),
                "late_stage_pipeline": bool(rng.random() < 0.12),
            }
        )

    csms = ["M. Diaz", "O. Grant", "Q. Wu", "R. Singh"]
    cs_rows: list[dict] = []
    for account_index in range(60):
        cs_rows.append(
            {
                "account_id": f"CS-{account_index + 1:04d}",
                "account_name": f"Simulated Customer {account_index + 1}",
                "csm": csms[account_index % len(csms)],
                "arr_m": round(rng.uniform(0.08, 0.95), 3),
                "renewal_risk": round(rng.uniform(0.05, 0.55), 3),
                "expansion_m": round(rng.uniform(0.02, 1.4), 3),
                "workload": int(rng.integers(1, 11)),
                "near_term_renewal": bool(rng.random() < 0.24),
                "specialist_required": bool(rng.random() < 0.10),
            }
        )

    return pd.DataFrame(history_rows), pd.DataFrame(account_rows), pd.DataFrame(cs_rows)


class AttainmentModel:
    """Elastic-net baseline with a strict chronological holdout."""

    def __init__(self, alpha: float = 0.08, l1_ratio: float = 0.15) -> None:
        preprocess = ColumnTransformer(
            transformers=[
                ("numeric", StandardScaler(), NUMERIC_FEATURES),
                ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ]
        )
        self.pipeline = Pipeline(
            steps=[
                ("preprocess", preprocess),
                ("regression", ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=20_000)),
            ]
        )
        self.metrics_: ModelMetrics | None = None
        self.residual_std_: float | None = None

    def fit_validate(self, history: pd.DataFrame, validation_quarter: str = "2025Q4") -> ModelMetrics:
        """Fit only on periods before the validation quarter and score forward."""

        required = set(FEATURES + ["territory_id", "bookings_m"])
        missing = required.difference(history.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        train = history.loc[history["quarter"] < validation_quarter].copy()
        validation = history.loc[history["quarter"] == validation_quarter].copy()
        if train.empty or validation.empty:
            raise ValueError("Chronological train and validation periods must both contain rows")

        self.pipeline.fit(train[FEATURES], train["bookings_m"])
        train_prediction = self.pipeline.predict(train[FEATURES])
        validation_prediction = np.maximum(0, self.pipeline.predict(validation[FEATURES]))
        residuals = train["bookings_m"].to_numpy() - train_prediction
        self.residual_std_ = float(np.std(residuals, ddof=1))

        actual = validation["bookings_m"].to_numpy()
        error = validation_prediction - actual
        metrics = ModelMetrics(
            train_through=str(train["quarter"].max()),
            validation_period=validation_quarter,
            mae_m=float(mean_absolute_error(actual, validation_prediction)),
            wmape=float(np.abs(error).sum() / np.abs(actual).sum()),
            bias_m=float(error.mean()),
        )
        self.metrics_ = metrics
        return metrics

    def predict_capacity(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Return expected bookings and an illustrative 80% prediction interval."""

        if self.residual_std_ is None:
            raise RuntimeError("Call fit_validate before predict_capacity")
        result = frame.copy()
        expected = np.maximum(0, self.pipeline.predict(result[FEATURES]))
        interval_width = 1.282 * self.residual_std_
        result["expected_bookings_m"] = expected
        result["capacity_low_m"] = np.maximum(0, expected - interval_width)
        result["capacity_high_m"] = expected + interval_width
        return result


def allocate_quota(
    capacity: pd.DataFrame,
    financial_plan_m: float,
    coverage_factor: float = 1.15,
    min_attainment: float = 0.70,
) -> pd.DataFrame:
    """Allocate a fixed plan by capacity and expose feasibility risk.

    The total recommended quota is reconciled exactly to plan × coverage.
    Quota is allocated with a small floor so low-capacity territories do not
    disappear from the operating plan.
    """

    if financial_plan_m <= 0 or coverage_factor <= 0:
        raise ValueError("Financial plan and coverage factor must be positive")
    required = {"territory_id", "expected_bookings_m"}
    if not required.issubset(capacity.columns):
        raise ValueError(f"Capacity data requires {sorted(required)}")

    result = capacity[["territory_id", "expected_bookings_m"]].copy()
    target_quota = financial_plan_m * coverage_factor
    floor_weight = max(result["expected_bookings_m"].median() * 0.20, 0.01)
    weights = result["expected_bookings_m"].clip(lower=floor_weight)
    result["recommended_quota_m"] = target_quota * weights / weights.sum()
    result["expected_attainment"] = (
        result["expected_bookings_m"] / result["recommended_quota_m"]
    )
    result["decision"] = np.select(
        [result["expected_attainment"] < min_attainment, result["expected_attainment"] < 0.85],
        ["Rebalance", "Review"],
        default="Approve",
    )

    reconciliation_difference = target_quota - result["recommended_quota_m"].sum()
    result.loc[result.index[-1], "recommended_quota_m"] += reconciliation_difference
    result["recommended_quota_m"] = result["recommended_quota_m"].round(4)
    return result.sort_values(["decision", "expected_attainment"])


def _enterprise_load(accounts: pd.DataFrame) -> pd.DataFrame:
    return (
        accounts.groupby("territory_id", as_index=False)
        .agg(
            accounts=("account_id", "count"),
            potential_m=("potential_m", "sum"),
            pipeline_m=("pipeline_m", "sum"),
            workload=("workload", "sum"),
        )
    )


def carve_enterprise(accounts: pd.DataFrame, rules: CarvingRules = CarvingRules()) -> pd.DataFrame:
    """Recommend greedy moves from overloaded to underloaded territories.

    The score rewards potential balance and penalizes workload and disruption.
    Named accounts and late-stage pipeline are hard locks by default.
    """

    working = accounts.copy()
    loads = _enterprise_load(working)
    target_potential = loads["potential_m"].mean()
    target_workload = loads["workload"].mean()
    max_moves = max(1, int(len(working) * rules.max_account_movement_rate))
    proposals: list[dict] = []

    for _ in range(max_moves):
        loads = _enterprise_load(working).set_index("territory_id")
        source = (loads["potential_m"] - target_potential).idxmax()
        destination = (loads["potential_m"] - target_potential).idxmin()
        if loads.loc[source, "potential_m"] <= target_potential:
            break
        if loads.loc[destination, "accounts"] >= rules.max_accounts_per_territory:
            break

        candidates = working.loc[working["territory_id"] == source].copy()
        if rules.named_accounts_locked:
            candidates = candidates.loc[~candidates["named_account"]]
        if rules.late_stage_pipeline_locked:
            candidates = candidates.loc[~candidates["late_stage_pipeline"]]
        if candidates.empty:
            break

        before_gap = abs(loads.loc[source, "potential_m"] - target_potential) + abs(
            loads.loc[destination, "potential_m"] - target_potential
        )

        def score(row: pd.Series) -> float:
            after_gap = abs(loads.loc[source, "potential_m"] - row.potential_m - target_potential)
            after_gap += abs(loads.loc[destination, "potential_m"] + row.potential_m - target_potential)
            balance_gain = before_gap - after_gap
            workload_penalty = max(
                0.0,
                loads.loc[destination, "workload"] + row.workload - target_workload,
            ) / max(target_workload, 1)
            return float(balance_gain - 0.25 * workload_penalty)

        candidates["move_score"] = candidates.apply(score, axis=1)
        choice = candidates.sort_values("move_score", ascending=False).iloc[0]
        if choice.move_score <= 0:
            break
        working.loc[working["account_id"] == choice.account_id, "territory_id"] = destination
        proposals.append(
            {
                "account_id": choice.account_id,
                "account_name": choice.account_name,
                "current_territory": source,
                "proposed_territory": destination,
                "potential_m": choice.potential_m,
                "move_score": round(float(choice.move_score), 4),
                "action": "Move",
                "reason": "Improves potential balance without violating hard locks",
            }
        )

    return pd.DataFrame(proposals)


def _cs_load(accounts: pd.DataFrame) -> pd.DataFrame:
    weighted_risk = accounts["arr_m"] * accounts["renewal_risk"]
    frame = accounts.assign(weighted_risk_m=weighted_risk)
    return (
        frame.groupby("csm", as_index=False)
        .agg(
            accounts=("account_id", "count"),
            managed_arr_m=("arr_m", "sum"),
            risk_arr_m=("weighted_risk_m", "sum"),
            expansion_m=("expansion_m", "sum"),
            workload=("workload", "sum"),
        )
    )


def carve_customer_success(accounts: pd.DataFrame, max_moves: int = 8) -> pd.DataFrame:
    """Balance CS workload while protecting continuity-sensitive customers."""

    working = accounts.copy()
    proposals: list[dict] = []
    for _ in range(max_moves):
        loads = _cs_load(working).set_index("csm")
        workload_target = loads["workload"].mean()
        arr_target = loads["managed_arr_m"].mean()
        source = (loads["workload"] / workload_target + loads["managed_arr_m"] / arr_target).idxmax()
        destination = (loads["workload"] / workload_target + loads["managed_arr_m"] / arr_target).idxmin()
        candidates = working.loc[
            (working["csm"] == source)
            & (~working["near_term_renewal"])
            & (~working["specialist_required"])
        ].copy()
        if candidates.empty:
            break

        candidates["balance_score"] = (
            candidates["workload"] / max(workload_target, 1)
            + candidates["arr_m"] / max(arr_target, 0.01)
            + 0.25 * candidates["expansion_m"]
            - 0.35 * candidates["renewal_risk"]
        )
        choice = candidates.sort_values("balance_score", ascending=False).iloc[0]
        working.loc[working["account_id"] == choice.account_id, "csm"] = destination
        proposals.append(
            {
                "account_id": choice.account_id,
                "account_name": choice.account_name,
                "current_csm": source,
                "proposed_csm": destination,
                "arr_m": choice.arr_m,
                "workload": int(choice.workload),
                "action": "Move",
                "reason": "Balances managed ARR and service workload; continuity checks passed",
            }
        )
    return pd.DataFrame(proposals)


def run_demo(output_dir: str | Path = "outputs") -> None:
    """Run all four stages and export auditable CSV outputs."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    history, enterprise_accounts, cs_accounts = simulate_data()

    model = AttainmentModel()
    metrics = model.fit_validate(history)
    latest = history.loc[history["quarter"] == history["quarter"].max()].copy()
    capacity = model.predict_capacity(latest)
    quota = allocate_quota(capacity, financial_plan_m=24.0, coverage_factor=1.15)
    enterprise_moves = carve_enterprise(enterprise_accounts)
    cs_moves = carve_customer_success(cs_accounts)

    history.to_csv(output_path / "attainment_history.csv", index=False)
    capacity.to_csv(output_path / "territory_capacity.csv", index=False)
    quota.to_csv(output_path / "enterprise_quota.csv", index=False)
    enterprise_moves.to_csv(output_path / "enterprise_carving.csv", index=False)
    cs_moves.to_csv(output_path / "cs_carving.csv", index=False)
    pd.DataFrame([metrics.__dict__]).to_csv(output_path / "model_validation.csv", index=False)

    print(f"Validation MAE: ${metrics.mae_m:.3f}M")
    print(f"Validation WMAPE: {metrics.wmape:.1%}")
    print(f"Quota allocated: ${quota['recommended_quota_m'].sum():.2f}M")
    print(f"Enterprise moves proposed: {len(enterprise_moves)}")
    print(f"CS moves proposed: {len(cs_moves)}")


if __name__ == "__main__":
    run_demo()

