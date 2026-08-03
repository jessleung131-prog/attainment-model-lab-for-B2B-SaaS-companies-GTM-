# 3. Predictive Enterprise Quota

## Business question

How should a fixed financial plan be distributed across territories so quota difficulty is defensible and operational change remains controlled?

## Financial control

```text
required total quota = financial plan × coverage factor
```

The optimizer cannot invent a different company target. The recommended territory quotas must reconcile exactly to the required total.

## Inputs

- Expected bookings and capacity interval from the attainment model
- Prior quota
- Rep ramp or special planning adjustment
- Financial plan and coverage factor
- Minimum/maximum allowed quota change
- Target planning attainment

## Optimization

`scipy.optimize.minimize` uses Sequential Least Squares Programming (SLSQP).

Objective:

```text
minimize
    mean((expected_bookings / quota - target_attainment)²)
  + λ × mean(((quota - prior_quota) / prior_quota)²)
```

Constraints:

- Sum of territory quota equals the approved total
- Quota stays inside allowed change bands when feasible
- Quota remains positive
- Optional regional subtotals, ramp adjustments, and management locks can be added

## Procedure

1. Load the approved plan and coverage factor.
2. Generate a capacity-weighted starting allocation.
3. Apply quota-change bounds.
4. Optimize for comparable expected difficulty with a change penalty.
5. Recalculate expected attainment and uncertainty range.
6. Flag territories below review and rebalance thresholds.
7. Reconcile the allocation to the plan and export a control difference.

## Validation

- Exact plan reconciliation
- Constraint satisfaction
- Expected-attainment dispersion before versus after
- Percentage of territories below the feasibility threshold
- Sensitivity to capacity low/base/high scenarios
- Backtest: would the method have produced less biased quota difficulty in prior periods?

Implementation: `models/quota.py`.

