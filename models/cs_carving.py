"""Customer Success portfolio carving with continuity guardrails."""
from __future__ import annotations
import pandas as pd


def _portfolio(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.assign(risk_arr_m=frame["arr_m"] * frame["renewal_risk"])
    return enriched.groupby("csm").agg(
        accounts=("account_id", "count"), managed_arr_m=("arr_m", "sum"),
        risk_arr_m=("risk_arr_m", "sum"), expansion_m=("expansion_m", "sum"),
        workload=("workload", "sum"),
    )


def carve_customer_success(accounts: pd.DataFrame, max_moves: int = 8) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Balance value and service load while locking sensitive relationships."""
    working = accounts.copy()
    before = _portfolio(working)
    decisions: list[dict] = []
    for _ in range(max_moves):
        load = _portfolio(working)
        target_arr, target_work = load.managed_arr_m.mean(), load.workload.mean()
        pressure = load.managed_arr_m / target_arr + load.workload / target_work + 0.4 * load.risk_arr_m / max(load.risk_arr_m.mean(), .01)
        source, destination = pressure.idxmax(), pressure.idxmin()
        candidates = working.loc[
            (working.csm == source) & ~working.near_term_renewal & ~working.specialist_required
        ].copy()
        if candidates.empty:
            break
        candidates["score"] = (
            candidates.workload / target_work + candidates.arr_m / target_arr
            + 0.25 * candidates.expansion_m - 0.30 * candidates.renewal_risk
        )
        choice = candidates.sort_values("score", ascending=False).iloc[0]
        working.loc[working.account_id == choice.account_id, "csm"] = destination
        decisions.append({
            "account_id": choice.account_id, "account_name": choice.account_name,
            "current_csm": source, "proposed_csm": destination,
            "arr_m": choice.arr_m, "renewal_risk": choice.renewal_risk,
            "workload": int(choice.workload), "rule_status": "Continuity passed",
            "action": "Move", "reason": "Reduces combined ARR, risk, and workload pressure",
        })
    after = _portfolio(working)
    audit = before.add_prefix("before_").join(after.add_prefix("after_")).reset_index()
    return pd.DataFrame(decisions), audit

