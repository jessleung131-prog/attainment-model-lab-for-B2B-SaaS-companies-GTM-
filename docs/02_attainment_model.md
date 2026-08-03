# 2. Underlying Attainment Model

## Business question

Given the territory composition and information available at the planning cutoff, what bookings can this territory reasonably produce next quarter?

The primary target is **bookings**, not `bookings / quota`. Predicting bookings keeps capacity independent of a proposed quota. Expected attainment is calculated downstream for each quota scenario.

## Grain and features

One row is `territory × rep × quarter`.

- Territory: account potential, account count, industry concentration, region
- Pipeline: starting pipeline and historical conversion
- Rep context: tenure/ramp; optional partially pooled rep effect
- Time: quarter-of-year; additional macro variables when supplied
- Target: realized bookings during the following quarter

## Models and libraries

| Tactic | Library | Role |
|---|---|---|
| Mean baseline | `sklearn.DummyRegressor` | Minimum performance bar |
| Ridge | `sklearn.linear_model.Ridge` | Stable, interpretable baseline under correlated features |
| Elastic Net | `sklearn.linear_model.ElasticNet` | Regularization plus conservative feature selection |
| Histogram gradient boosting | `sklearn.ensemble.HistGradientBoostingRegressor` | Nonlinear challenger and interaction test |
| Mixed effects | `statsmodels.MixedLM` | Diagnostic separation of rep, territory, region, and period variation |

## Training procedure

1. Validate grain, dates, keys, forbidden leakage fields, and snapshot timing.
2. Reserve the latest quarter as an untouched chronological holdout.
3. Fit preprocessing only on earlier quarters: scale numeric fields and one-hot encode categories.
4. Fit baseline, regularized models, and nonlinear challenger.
5. Estimate residual dispersion on training data and produce an illustrative 80% interval.
6. Compare WMAPE, MAE, RMSE, bias, and interval coverage.
7. Select the best non-naive model; retain the full leaderboard.
8. Score the planning-period territory frame and export expected bookings plus interval.

## Statistical reasoning

Regularization is the default because territory-quarter datasets are usually small and composition variables are correlated. The mixed-effects challenger applies partial pooling, which limits extreme rep or territory estimates when history is sparse. Rep effects are diagnostic, not causal: strong reps are not randomly assigned to territories.

## Validation

- Chronological holdout, never a random split
- Error and bias by region
- Interval coverage
- Rank stability for high/low-capacity territories
- Sensitivity to feature removal and reorganization periods
- Baseline comparison before accepting complexity

Implementation: `models/attainment.py`, `models/hierarchical.py`, and `models/validation.py`.

