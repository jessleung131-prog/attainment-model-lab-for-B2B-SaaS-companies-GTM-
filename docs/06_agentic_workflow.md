# 6. Agentic Decision Workflow

## Definition

The agentic layer does not replace the statistical model or optimizer. It coordinates a controlled workflow:

```text
observe → diagnose → propose → test rules → score → explain → escalate → log
```

## Separation of responsibilities

| Layer | Responsibility |
|---|---|
| Statistical model | Estimate attainable bookings and uncertainty |
| Optimizer | Search quota or assignment scenarios |
| Rules engine | Define what is permitted |
| Agentic orchestrator | Assemble evidence, actions, and exception queue |
| Human approver | Accept, reject, or override with a recorded reason |

## What / Why / Action output

Every row in the decision queue includes:

- **What:** the territory, quota, or assignment issue
- **Why:** predictive evidence, constraint result, and confidence
- **Action:** recommended next step, accountable owner, and review requirement

## Guardrails

- Deterministic outputs from a frozen snapshot and versioned configuration
- No silent account reassignment
- Low-confidence or locked cases always escalate
- Model estimates never override financial controls or field policy
- Every override records approver, timestamp, and reason
- Generated narrative may summarize governed metrics but may not invent numbers

Implementation: `agentic/orchestrator.py` and `config/business_rules.yaml`.

