"""Generate reproducible point-in-time GTM datasets."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd


def generate(seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    territories = [f"ENT-{i:02d}" for i in range(1, 9)]
    regions = {t: ["East", "Central", "West"][(i - 1) % 3] for i, t in enumerate(territories, 1)}
    reps = {t: f"REP-{i:02d}" for i, t in enumerate(territories, 1)}
    quarters = pd.period_range("2023Q1", "2025Q4", freq="Q")
    history = []
    for ti, territory in enumerate(territories):
        territory_effect, rep_effect = rng.normal(0, .20), rng.normal(0, .13)
        for qi, quarter in enumerate(quarters):
            potential, pipeline = rng.uniform(5, 12), rng.uniform(1, 4)
            count, tenure = int(rng.integers(12, 26)), int(rng.integers(4, 72))
            conversion, concentration = rng.uniform(.16, .38), rng.uniform(.18, .62)
            seasonality = [0, .05, -.03, .12][qi % 4]
            bookings = (
                .15 * potential + .42 * pipeline + 1.8 * conversion
                + .006 * min(tenure, 36) - .45 * concentration
                + territory_effect + rep_effect + seasonality + rng.normal(0, .18)
            )
            history.append({
                "territory_id": territory, "rep_id": reps[territory], "region": regions[territory],
                "quarter": str(quarter), "quarter_of_year": f"Q{quarter.quarter}",
                "snapshot_date": quarter.start_time - pd.Timedelta(days=1),
                "account_potential_m": round(potential, 3), "starting_pipeline_m": round(pipeline, 3),
                "account_count": count, "rep_tenure_months": tenure,
                "historical_conversion": round(conversion, 4),
                "industry_concentration": round(concentration, 4),
                "bookings_m": round(max(.2, bookings), 3),
                "prior_quota_m": round(max(.4, bookings / rng.uniform(.68, 1.08)), 3),
            })

    industries = ["FinTech", "Cybersecurity", "Data", "Commerce", "HR"]
    accounts = []
    for i in range(120):
        territory = territories[i % 8]
        accounts.append({
            "account_id": f"ACC-{i+1:04d}", "account_name": f"Simulated {industries[i%5]} {i+1}",
            "territory_id": territory, "region": regions[territory], "industry": industries[i % 5],
            "potential_m": round(rng.uniform(.25, 2.1), 3), "pipeline_m": round(rng.uniform(0, .85), 3),
            "workload": int(rng.integers(1, 11)), "named_account": bool(rng.random() < .09),
            "late_stage_pipeline": bool(rng.random() < .12),
        })

    csms, cs_accounts = ["M. Diaz", "O. Grant", "Q. Wu", "R. Singh"], []
    for i in range(60):
        cs_accounts.append({
            "account_id": f"CS-{i+1:04d}", "account_name": f"Simulated Customer {i+1}",
            "csm": csms[i % 4], "arr_m": round(rng.uniform(.08, .95), 3),
            "renewal_risk": round(rng.uniform(.05, .55), 3), "expansion_m": round(rng.uniform(.02, 1.4), 3),
            "workload": int(rng.integers(1, 11)), "near_term_renewal": bool(rng.random() < .24),
            "specialist_required": bool(rng.random() < .10),
        })
    return pd.DataFrame(history), pd.DataFrame(accounts), pd.DataFrame(cs_accounts)


def write_all(output_dir: str | Path = "data") -> None:
    path = Path(output_dir); path.mkdir(parents=True, exist_ok=True)
    history, accounts, cs = generate()
    history.to_csv(path / "attainment_history.csv", index=False)
    accounts.to_csv(path / "enterprise_accounts.csv", index=False)
    cs.to_csv(path / "cs_accounts.csv", index=False)
    print(f"Wrote {len(history)} territory-quarter rows, {len(accounts)} Enterprise accounts, and {len(cs)} CS accounts")


if __name__ == "__main__":
    write_all()

