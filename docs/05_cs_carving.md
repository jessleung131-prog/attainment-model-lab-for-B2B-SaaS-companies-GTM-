# 5. Agentic Customer Success Carving

## Business question

How should customer accounts be allocated across CSMs so commercial value and service demand are balanced while continuity-sensitive relationships remain protected?

Customer health is an input. The model output is the **account-to-CSM portfolio assignment**.

## Portfolio inputs

- Managed ARR and risk-adjusted ARR
- Renewal risk and renewal timing
- Expansion potential
- Product/support complexity and workload
- Specialist requirement and customer continuity

## Decision logic

1. Calculate portfolio pressure from ARR, risk-adjusted ARR, and workload.
2. Identify the most overloaded and most underloaded CSM portfolios.
3. Exclude near-term renewals and specialist-dependent relationships.
4. Rank eligible accounts by balance improvement.
5. Propose a limited number of moves.
6. Export the reason and require CS leadership approval.

## Why equal account count is wrong

Ten low-complexity customers are not equivalent to ten high-ARR customers renewing next month. The objective therefore balances value, risk, and service demand rather than count alone.

## Validation

- Zero movement of continuity-locked accounts
- Before/after workload and managed-ARR dispersion
- High-risk-renewal concentration by CSM
- Number of disrupted relationships
- Sensitivity to risk and workload weights
- Review by CS Operations and regional leaders

Implementation: `models/cs_carving.py`.

