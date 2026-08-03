# 7. Validation, Monitoring, and Client Handoff

## Model validation

- Latest-quarter chronological holdout
- MAE, RMSE, WMAPE, bias, and interval coverage
- Segment-level errors by region and rep-tenure cohort
- Baseline versus regularized versus nonlinear challenger
- Leakage audit and feature-availability dictionary

## Decision validation

- Quota reconciles exactly to the financial plan
- All hard carving constraints pass
- Before/after balance metrics are reported
- Sensitivity scenarios use capacity low/base/high estimates
- Exception volume is operationally manageable

## Monitoring if productionized

| Monitor | Example trigger |
|---|---|
| Data freshness | Snapshot is late or missing |
| Schema drift | Required column removed/type changed |
| Feature drift | PSI or standardized mean shift exceeds threshold |
| Error drift | WMAPE or bias deteriorates over consecutive periods |
| Decision drift | Override rate or exception volume increases materially |
| Constraint health | Any prohibited move appears in an output |

## Static GSheets handoff

The proof of approach is designed for static exports. The client handoff should include:

1. Frozen source tabs and control totals
2. Data dictionary and effective-date assumptions
3. Point-in-time modeling table
4. Model leaderboard and validation predictions
5. Capacity, quota, and carving outputs
6. Business-rules tab with editable thresholds
7. Decision queue with human-review status
8. Methodology, limitations, and rerun instructions

The `run_pipeline.py` output directory mirrors these handoff artifacts as CSV and JSON files.
