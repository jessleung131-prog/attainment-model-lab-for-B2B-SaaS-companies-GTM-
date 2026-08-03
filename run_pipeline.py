"""Run the complete synthetic proof-of-approach and export evidence."""
from pathlib import Path
import json
import yaml

from agentic.orchestrator import build_decision_queue
from models.attainment import fit_attainment_models, score_capacity
from models.cs_carving import carve_customer_success
from models.enterprise_carving import EnterpriseRules, carve_enterprise
from models.quota import allocate_enterprise_quota
from models.validation import carving_balance_report, quota_controls, segment_error_report
from synthetic_data.generate_all import generate


def main(output_dir: str = "outputs") -> None:
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    rules = yaml.safe_load(Path("config/business_rules.yaml").read_text())
    history, enterprise_accounts, cs_accounts = generate()
    result = fit_attainment_models(history)
    planning = history.loc[history.quarter == history.quarter.max()].copy()
    capacity = score_capacity(result, planning)
    quota_cfg = rules["quota"]
    quota = allocate_enterprise_quota(
        capacity, quota_cfg["financial_plan_m"], quota_cfg["coverage_factor"],
        max_change=quota_cfg["max_change"], target_attainment=quota_cfg["target_attainment"],
    )
    ent_cfg = rules["enterprise_carving"]
    ent_moves, ent_audit = carve_enterprise(enterprise_accounts, EnterpriseRules(
        max_move_rate=ent_cfg["max_move_rate"], max_accounts=ent_cfg["max_accounts_per_territory"],
        protect_named=ent_cfg["protect_named_accounts"],
        protect_late_stage=ent_cfg["protect_late_stage_pipeline"], preserve_region=ent_cfg["preserve_region"],
    ))
    cs_moves, cs_audit = carve_customer_success(cs_accounts, rules["customer_success_carving"]["max_moves"])
    queue = build_decision_queue(quota, ent_moves, cs_moves)

    tables = {
        "attainment_leaderboard": result.leaderboard,
        "attainment_validation": result.validation_predictions,
        "feature_effects": result.feature_effects,
        "territory_capacity": capacity,
        "enterprise_quota": quota,
        "enterprise_moves": ent_moves,
        "enterprise_balance": ent_audit,
        "cs_moves": cs_moves,
        "cs_balance": cs_audit,
        "segment_errors": segment_error_report(result.validation_predictions),
        "decision_queue": queue,
    }
    for name, frame in tables.items():
        frame.to_csv(out / f"{name}.csv", index=False)
    controls = {
        "quota": quota_controls(quota, quota_cfg["financial_plan_m"] * quota_cfg["coverage_factor"]),
        "enterprise_potential_balance": carving_balance_report(ent_audit, "potential_m"),
        "cs_workload_balance": carving_balance_report(cs_audit, "workload"),
    }
    (out / "controls.json").write_text(json.dumps(controls, indent=2))
    print(f"Selected attainment model: {result.selected_model}")
    print(f"Quota reconciled: {controls['quota']['reconciled']}")
    print(f"Decision queue rows: {len(queue)}")


if __name__ == "__main__":
    main()
