"""Convert model outputs into reviewable actions and exceptions."""
from __future__ import annotations
import pandas as pd


def build_decision_queue(quota: pd.DataFrame, enterprise_moves: pd.DataFrame, cs_moves: pd.DataFrame) -> pd.DataFrame:
    decisions = []
    for row in quota.itertuples():
        if row.decision != "Approve":
            decisions.append({
                "priority": "P1" if row.decision == "Rebalance" else "P2",
                "model": "Enterprise quota", "entity": row.territory_id,
                "what": f"Expected attainment is {row.expected_attainment:.0%}",
                "why": "Quota is high relative to predicted territory capacity",
                "action": "Test eligible account moves, then review quota with Sales Ops and Finance",
                "human_review": "Required",
            })
    for model, frame in [("Enterprise carving", enterprise_moves), ("CS carving", cs_moves)]:
        for row in frame.itertuples():
            decisions.append({
                "priority": "P2", "model": model, "entity": row.account_id,
                "what": f"Proposed reassignment from {row[3]} to {row[4]}",
                "why": row.reason, "action": "Approve, reject, or record an override reason",
                "human_review": "Required",
            })
    return pd.DataFrame(decisions).sort_values(["priority", "model"])

