"""Rule-constrained Enterprise account-to-territory carving."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class EnterpriseRules:
    max_move_rate: float = 0.18
    max_accounts: int = 24
    protect_named: bool = True
    protect_late_stage: bool = True
    preserve_region: bool = True


def _summary(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.groupby("territory_id").agg(
        accounts=("account_id", "count"), potential_m=("potential_m", "sum"),
        pipeline_m=("pipeline_m", "sum"), workload=("workload", "sum"),
    )


def carve_enterprise(accounts: pd.DataFrame, rules: EnterpriseRules = EnterpriseRules()) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate, filter, score, and greedily accept auditable account moves."""
    working = accounts.copy()
    before = _summary(working)
    target = before["potential_m"].mean()
    max_moves = max(1, int(len(working) * rules.max_move_rate))
    decisions: list[dict] = []

    for _ in range(max_moves):
        loads = _summary(working)
        source = (loads["potential_m"] - target).idxmax()
        destination_candidates = loads.sort_values("potential_m").index.tolist()
        accepted = False
        for destination in destination_candidates:
            if destination == source or loads.loc[destination, "accounts"] >= rules.max_accounts:
                continue
            source_rows = working.loc[working["territory_id"] == source].copy()
            if rules.protect_named:
                source_rows = source_rows.loc[~source_rows["named_account"]]
            if rules.protect_late_stage:
                source_rows = source_rows.loc[~source_rows["late_stage_pipeline"]]
            if rules.preserve_region:
                region = working.loc[working["territory_id"] == destination, "region"].iloc[0]
                source_rows = source_rows.loc[source_rows["region"] == region]
            if source_rows.empty:
                continue

            def score(row: pd.Series) -> float:
                before_gap = abs(loads.loc[source, "potential_m"] - target) + abs(loads.loc[destination, "potential_m"] - target)
                after_gap = abs(loads.loc[source, "potential_m"] - row.potential_m - target)
                after_gap += abs(loads.loc[destination, "potential_m"] + row.potential_m - target)
                disruption = 0.10 + 0.15 * row.workload / 10 + 0.20 * row.pipeline_m
                return float(before_gap - after_gap - disruption)

            source_rows["score"] = source_rows.apply(score, axis=1)
            choice = source_rows.sort_values("score", ascending=False).iloc[0]
            if choice.score <= 0:
                continue
            working.loc[working["account_id"] == choice.account_id, "territory_id"] = destination
            decisions.append({
                "account_id": choice.account_id, "account_name": choice.account_name,
                "current_territory": source, "proposed_territory": destination,
                "potential_m": choice.potential_m, "pipeline_m": choice.pipeline_m,
                "score": round(float(choice.score), 4), "rule_status": "Eligible",
                "action": "Move", "reason": "Improves potential balance after disruption penalty",
            })
            accepted = True
            break
        if not accepted:
            break

    after = _summary(working)
    audit = before.add_prefix("before_").join(after.add_prefix("after_")).reset_index()
    return pd.DataFrame(decisions), audit

