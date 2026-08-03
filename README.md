# B2B SaaS GTM Attainment Model Lab

A Python-first, client-facing proof of approach for attainment modeling, predictive Enterprise quota, Enterprise territory carving, and Customer Success portfolio carving.

🔴 **[Live Demo →](https://jessleung131-prog.github.io/attainment-model-lab-for-B2B-SaaS-companies-GTM-/)**

> Every organization, person, account, value, model result, and recommendation is synthetic. The project demonstrates architecture and methodology, not real client predictions.

---

## What It Does

| Layer | Capability |
|---|---|
| **Data foundation** | Generates Salesforce-style account, territory, quota, rep, pipeline, and CS portfolio data with point-in-time snapshots |
| **Attainment model** | Compares naive, Ridge, Elastic Net, and gradient-boosting models with a chronological holdout |
| **Hierarchical diagnostic** | Provides a mixed-effects extension for partially pooled rep, territory, and region effects |
| **Predictive quota** | Allocates the approved financial plan while minimizing quota-difficulty dispersion and limiting quota change |
| **Enterprise carving** | Generates and scores account moves after named-account, pipeline, region, and capacity constraints |
| **CS carving** | Balances managed ARR, risk-adjusted ARR, expansion potential, and workload with continuity locks |
| **Agentic workflow** | Converts outputs into What / Why / Action decisions and routes exceptions for human approval |
| **Validation** | Tests time-based model accuracy, segment bias, quota reconciliation, hard rules, and before/after balance |

---

## One Methodology, Three Operating Models

```text
Static CRM · quota · pipeline · ownership · CS exports
                         │
                         ▼
          Point-in-time territory × rep × quarter mart
                         │
                         ▼
              ATTAINMENT CAPACITY MODEL
       expected bookings · interval · drivers · confidence
                         │
          ┌──────────────┼─────────────────┐
          ▼              ▼                 ▼
 Predictive quota   Enterprise carving   CS carving
 financial plan     account assignment   portfolio assignment
          │              │                 │
          └──────────────┼─────────────────┘
                         ▼
        rules → evidence → What / Why / Action queue
                         ▼
                    human approval
```

The attainment model predicts **bookings**, not attainment percentage. Quota is applied afterward so Finance can test multiple allocations without creating a circular target.

---

## Modeling Tactics

### 1. Underlying attainment methodology

| Item | Design |
|---|---|
| Grain | Territory × rep × quarter |
| Target | Next-quarter bookings |
| Features | Potential, starting pipeline, account count/mix, conversion, rep tenure, region, seasonality |
| Baselines | Mean, Ridge, Elastic Net |
| Challenger | Histogram gradient boosting |
| Hierarchical extension | Mixed-effects model with rep random intercept and territory/region variance components |
| Validation | Latest-quarter holdout; MAE, RMSE, WMAPE, bias, interval coverage, regional error |
| Key control | Feature snapshots must precede the planning-period start |

### 2. Predictive Enterprise quota

```text
required quota = financial plan × coverage factor
```

SLSQP constrained optimization minimizes expected-attainment dispersion plus a penalty for large changes from prior quota. The allocation must reconcile exactly to the financial plan and respect change bands when feasible.

### 3. Agentic Enterprise territory carving

Candidate account moves are generated, filtered through hard constraints, scored for balance improvement minus disruption, and placed into a human-review queue. The transparent greedy solver is appropriate for proof-of-approach work; the same contract can be upgraded to mixed-integer programming.

### 4. Agentic Customer Success carving

Customer health is an input—not the output. The output is an account-to-CSM portfolio assignment balancing ARR, renewal risk, expansion potential, and workload while protecting near-term renewals and specialist relationships.

Read the complete step-by-step methodology:

1. [Enterprise data architecture](docs/01_data_architecture.md)
2. [Attainment model](docs/02_attainment_model.md)
3. [Predictive Enterprise quota](docs/03_predictive_quota.md)
4. [Enterprise territory carving](docs/04_enterprise_carving.md)
5. [Customer Success carving](docs/05_cs_carving.md)
6. [Agentic workflow](docs/06_agentic_workflow.md)
7. [Validation and client handoff](docs/07_validation_handoff.md)

---

## Repository Structure

```text
agentic/
  orchestrator.py          # What / Why / Action decision queue
config/
  business_rules.yaml      # Client-editable rules and thresholds
docs/
  01_data_architecture.md
  02_attainment_model.md
  03_predictive_quota.md
  04_enterprise_carving.md
  05_cs_carving.md
  06_agentic_workflow.md
  07_validation_handoff.md
models/
  common.py                # Feature contract and shared metrics
  attainment.py            # Baselines, challenger, selection, capacity scoring
  hierarchical.py          # Mixed-effects diagnostic extension
  quota.py                 # Financial-plan constrained optimization
  enterprise_carving.py    # Enterprise rules and move scoring
  cs_carving.py            # CS portfolio balancing
  validation.py            # Segment, balance, and control reports
synthetic_data/
  generate_all.py          # Reproducible CRM/territory/CS simulation
tests/
  test_attainment.py
  test_quota.py
  test_carving.py
  test_pipeline.py
run_pipeline.py            # End-to-end proof-of-approach runner
index.html                 # Self-contained interactive dashboard
```

---

## Quick Start

```bash
git clone https://github.com/jessleung131-prog/attainment-model-lab-for-B2B-SaaS-companies-GTM-.git
cd attainment-model-lab-for-B2B-SaaS-companies-GTM-

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python run_pipeline.py
pytest -q
```

The pipeline writes auditable outputs to `outputs/`:

- Model leaderboard and validation predictions
- Feature effects and territory capacity intervals
- Financial-plan quota recommendations
- Enterprise and CS carving proposals
- Before/after balance tables
- Regional error report
- What / Why / Action decision queue
- JSON control checks

---

## Synthetic Data

The generator creates:

- **96 territory-quarter records** across eight Enterprise territories and twelve quarters
- **120 Enterprise accounts** with potential, pipeline, workload, industry, geography, and locks
- **60 Customer Success accounts** with ARR, renewal risk, expansion, workload, and continuity constraints

Signals are deliberately correlated and noisy so model selection and optimization are meaningful. The snapshot date precedes each outcome period to demonstrate leakage prevention.

---

## Tech Stack

| Area | Libraries |
|---|---|
| Data and simulation | Python, pandas, NumPy |
| Attainment prediction | scikit-learn: DummyRegressor, Ridge, ElasticNet, HistGradientBoosting |
| Hierarchical statistics | statsmodels MixedLM |
| Quota optimization | SciPy SLSQP |
| Rules and orchestration | PyYAML, Python dataclasses |
| Validation | scikit-learn metrics, pandas, NumPy |
| Tests | pytest |
| Demo | Standalone HTML/CSS/JavaScript, GitHub Pages |

---

## Client-Facing Decision Format

Every recommendation is written for an accountable stakeholder:

- **What:** the territory, quota, or portfolio issue
- **Why:** the model evidence, uncertainty, and constraint result
- **Action:** the next decision, owner, and human-review requirement

The model predicts. The optimizer proposes. Business rules constrain. Humans approve.

---

## Important Limitations

- Synthetic data proves workflow and code, not real-world lift.
- Rep and territory effects are associational because assignments are non-random.
- Residual prediction intervals are illustrative and should be calibrated on client history.
- Greedy carving is intentionally transparent; large production assignments may require MIP/CP-SAT.
- Any deployment must add access control, source-system integration, monitoring, and formal model governance.
