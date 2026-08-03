# 4. Agentic Enterprise Territory Carving

## Business question

Which accounts should move between Enterprise territories to improve attainable-capacity balance without breaking field constraints?

This is primarily a **constrained assignment problem**, not a classification model.

## Account inputs

- Potential/TAM, pipeline, industry, region, and estimated workload
- Current territory and relationship owner
- Named-account and late-stage-pipeline locks
- Territory account-count and workload capacity

## Four-stage decision workflow

1. **Generate candidates:** identify overloaded source and underloaded destination territories.
2. **Apply hard rules:** remove named accounts, late-stage opportunities, cross-region moves, and destinations above capacity.
3. **Score valid moves:** quantify improvement in potential balance and subtract disruption/workload penalties.
4. **Recommend and escalate:** accept positive-score moves; attach reason, evidence, rule result, and human-review status.

Illustrative objective:

```text
minimize
    dispersion(expected attainment)
  + λ1 × workload dispersion
  + λ2 × account movement cost
  + λ3 × concentration risk
```

The reference implementation uses a transparent greedy search because it is easy to audit for a design-partner proof of approach. For a larger production problem, replace the search with mixed-integer programming or constraint programming while preserving the same rules and objective.

## Validation

- No hard-rule violations
- Maximum movement rate respected
- Before/after coefficient of variation for potential, workload, and pipeline
- Count and value of moved accounts
- Sensitivity to movement penalties and capacity limits
- Field review of technically balanced but operationally implausible assignments

Implementation: `models/enterprise_carving.py`.

