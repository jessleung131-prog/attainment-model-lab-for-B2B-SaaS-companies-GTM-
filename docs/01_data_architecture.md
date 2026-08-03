# 1. Enterprise Data Architecture

## Decision-first design

The architecture supports four decisions: attainable bookings, Enterprise quota, Enterprise account-to-territory assignments, and Customer Success account-to-CSM assignments. Static exports are treated as source systems, not analysis-ready tables.

```text
Salesforce / planning / CS exports
        ↓ immutable dated snapshots
schema, key, type, duplicate, and control-total validation
        ↓
canonical account · opportunity · rep · territory · quota · CSM entities
        ↓ effective-dated ownership and territory history
point-in-time territory × rep × quarter feature mart
        ↓
attainment model → quota optimization → Enterprise/CS carving
        ↓
decision queue · evidence · override reason · export reconciliation
```

## Core grains

| Dataset | Grain | Stable keys | Timing rule |
|---|---|---|---|
| Account | Account | `account_id` | Attributes effective at planning cutoff |
| Opportunity snapshot | Opportunity × snapshot date | `opportunity_id`, `snapshot_date` | Only pipeline known at cutoff |
| Ownership | Account × effective-date interval | `account_id`, `owner_id` | No use of current owner historically |
| Attainment history | Territory × rep × quarter | `territory_id`, `rep_id`, `quarter` | Features frozen before quarter starts |
| Quota | Territory × planning period | `territory_id`, `quarter` | Financial-plan version retained |
| CS portfolio | Account × CSM × effective-date interval | `account_id`, `csm_id` | Renewal/continuity status at cutoff |

## Leakage controls

- Reconstruct historical ownership and territory membership with effective dates.
- Freeze pipeline at the planning cutoff; never use final stage or closed-won outcome as a feature.
- Fit encoders, scalers, and models only on earlier quarters.
- Separate the target window from every feature window.
- Keep quota outside the bookings target to avoid circularity.
- Retain source file, row identifier, snapshot date, model version, and rule version in outputs.

## Data quality controls

- Unique IDs and relationship integrity
- Duplicate and orphan detection
- Currency and date normalization
- Missing-field rates by source and period
- Reconciliation of account count, pipeline, bookings, ARR, and quota to source exports
- Explicit exception table: corrected, excluded, mapped, or unresolved

The code enforces the point-in-time contract in `models/common.py`.

