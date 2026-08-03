# B2B SaaS GTM Attainment Model Lab

A client-facing proof of approach for four connected GTM decisions:

1. **Attainment methodology** — estimate attainable bookings from territory composition, pipeline, rep context, and period effects.
2. **Predictive Enterprise quota** — allocate a fixed financial plan against modeled territory capacity.
3. **Agentic Enterprise territory carving** — propose account assignments under named-account, pipeline, geography, and disruption constraints.
4. **Agentic Customer Success carving** — balance managed ARR, renewal risk, expansion potential, workload, and customer continuity.

🔴 **[Live Demo →](https://jessleung131-prog.github.io/attainment-model-lab-for-B2B-SaaS-companies-GTM-/)**

---

## What the dashboard demonstrates

- A shared territory–rep–period attainment foundation
- Interpretable capacity drivers and uncertainty
- Financial-plan-first quota allocation
- Rule-constrained Enterprise account movements
- Customer Success portfolio balancing
- Human review queues and explainable recommendations
- Google Sheets-ready methodology and handoff

## Modeling approach

The attainment layer estimates expected bookings while separating territory composition, rep context, and time effects. Its outputs feed quota and carving decisions.

| Component | Approach |
|---|---|
| Attainment | Interpretable regularized or hierarchical regression |
| Enterprise quota | Capacity-weighted allocation with financial and operational constraints |
| Enterprise carving | Constrained optimization with hard rules and movement penalties |
| CS carving | Portfolio optimization across ARR, renewal risk, expansion, and workload |
| Validation | Time-based backtesting, leakage controls, bias checks, calibration, and sensitivity analysis |
| Agentic layer | Propose, test, explain, and escalate—not silent auto-assignment |

## Client-facing decision structure

Every recommendation is presented as:

- **What:** the territory, quota, or portfolio issue
- **Why:** the supporting model evidence and business drivers
- **Action:** the accountable stakeholder, recommended decision, and review requirement

## Data disclaimer

All organizations, people, accounts, values, model results, and recommendations are **synthetic**. They illustrate architecture and methodology only and do not represent a real client or actual business predictions.

## Files

- `index.html` — self-contained interactive dashboard
- `modeling/attainment_lab.py` — Python reference implementation for all four modeling stages
- `README.md` — project overview and methodology
- `.github/workflows/pages.yml` — GitHub Pages deployment

## Run the Python model

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m modeling.attainment_lab
```

The script generates synthetic point-in-time data, validates the attainment model chronologically, allocates quota to the financial plan, and exports Enterprise and CS carving recommendations to `outputs/`.

## Use locally

Download `index.html` and open it in any modern browser. No installation, server, or external JavaScript library is required.
