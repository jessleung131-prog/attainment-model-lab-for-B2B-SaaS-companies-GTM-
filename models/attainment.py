"""Attainment capacity models with chronological model selection.

The primary target is bookings, not attainment percentage. Quota is kept out of
the target so the downstream quota model can test alternative allocations
without circularity.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .common import (
    CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES,
    ValidationMetrics, assert_point_in_time_contract, regression_metrics,
)


@dataclass
class AttainmentResult:
    selected_model: str
    leaderboard: pd.DataFrame
    validation_predictions: pd.DataFrame
    feature_effects: pd.DataFrame
    model: Pipeline
    residual_std_m: float


def _preprocessor() -> ColumnTransformer:
    return ColumnTransformer([
        ("numeric", StandardScaler(), NUMERIC_FEATURES),
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
    ])


def _candidates(seed: int) -> dict[str, object]:
    return {
        "Mean baseline": DummyRegressor(strategy="mean"),
        "Ridge": Ridge(alpha=2.0),
        "ElasticNet": ElasticNet(alpha=0.06, l1_ratio=0.15, max_iter=20_000),
        "HistGradientBoosting": HistGradientBoostingRegressor(
            learning_rate=0.06, max_depth=3, max_iter=180,
            l2_regularization=1.0, random_state=seed,
        ),
    }


def fit_attainment_models(
    history: pd.DataFrame,
    validation_quarter: str | None = None,
    seed: int = 42,
) -> AttainmentResult:
    """Compare interpretable baselines and a nonlinear challenger out of time."""
    assert_point_in_time_contract(history)
    ordered_quarters = sorted(history["quarter"].unique())
    validation_quarter = validation_quarter or ordered_quarters[-1]
    train = history.loc[history["quarter"] < validation_quarter].copy()
    validation = history.loc[history["quarter"] == validation_quarter].copy()
    if len(train) < 20 or validation.empty:
        raise ValueError("Insufficient chronological history for train/validation")

    rows, fitted = [], {}
    for name, estimator in _candidates(seed).items():
        pipeline = Pipeline([("preprocess", _preprocessor()), ("model", estimator)])
        pipeline.fit(train[FEATURES], train["bookings_m"])
        train_pred = pipeline.predict(train[FEATURES])
        residual_std = float(np.std(train["bookings_m"].to_numpy() - train_pred, ddof=1))
        pred = np.maximum(0, pipeline.predict(validation[FEATURES]))
        width = 1.282 * residual_std
        metrics = regression_metrics(
            validation["bookings_m"].to_numpy(), pred,
            np.maximum(0, pred - width), pred + width,
        )
        rows.append(ValidationMetrics(
            model_name=name,
            train_through=str(train["quarter"].max()),
            validation_period=validation_quarter,
            **metrics,
        ).to_dict())
        fitted[name] = (pipeline, residual_std, pred)

    leaderboard = pd.DataFrame(rows).sort_values(["wmape", "mae_m"]).reset_index(drop=True)
    eligible = leaderboard.loc[leaderboard["model_name"].isin(["Ridge", "ElasticNet", "HistGradientBoosting"])]
    best_name = str(eligible.iloc[0]["model_name"])
    best_model, residual_std, best_pred = fitted[best_name]
    width = 1.282 * residual_std
    validation_output = validation[["territory_id", "region", "quarter", "bookings_m"]].copy()
    validation_output["predicted_bookings_m"] = best_pred
    validation_output["lower_80_m"] = np.maximum(0, best_pred - width)
    validation_output["upper_80_m"] = best_pred + width
    validation_output["error_m"] = best_pred - validation_output["bookings_m"]

    effects = _feature_effects(best_model, best_name)
    return AttainmentResult(best_name, leaderboard, validation_output, effects, best_model, residual_std)


def _feature_effects(model: Pipeline, model_name: str) -> pd.DataFrame:
    if model_name not in {"Ridge", "ElasticNet"}:
        return pd.DataFrame({"feature": FEATURES, "effect": np.nan, "note": "Nonlinear challenger"})
    prep = model.named_steps["preprocess"]
    names = list(NUMERIC_FEATURES) + list(
        prep.named_transformers_["categorical"].get_feature_names_out(CATEGORICAL_FEATURES)
    )
    coefficients = model.named_steps["model"].coef_
    return pd.DataFrame({"feature": names, "effect": coefficients}).sort_values(
        "effect", key=lambda s: s.abs(), ascending=False
    )


def score_capacity(result: AttainmentResult, planning_frame: pd.DataFrame) -> pd.DataFrame:
    expected = np.maximum(0, result.model.predict(planning_frame[FEATURES]))
    width = 1.282 * result.residual_std_m
    output = planning_frame.copy()
    output["expected_bookings_m"] = expected
    output["capacity_low_m"] = np.maximum(0, expected - width)
    output["capacity_high_m"] = expected + width
    output["model_name"] = result.selected_model
    return output

