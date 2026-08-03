from models.cs_carving import carve_customer_success
from models.enterprise_carving import carve_enterprise
from models.validation import carving_balance_report
from synthetic_data.generate_all import generate


def test_enterprise_carving_respects_hard_locks():
    _, accounts, _ = generate()
    moves, audit = carve_enterprise(accounts)
    moved = set(moves.account_id) if not moves.empty else set()
    locked = set(accounts.loc[accounts.named_account | accounts.late_stage_pipeline, "account_id"])
    assert moved.isdisjoint(locked)
    assert carving_balance_report(audit, "potential_m")["after_cv"] <= carving_balance_report(audit, "potential_m")["before_cv"]


def test_cs_carving_protects_continuity():
    _, _, accounts = generate()
    moves, audit = carve_customer_success(accounts)
    moved = set(moves.account_id) if not moves.empty else set()
    locked = set(accounts.loc[accounts.near_term_renewal | accounts.specialist_required, "account_id"])
    assert moved.isdisjoint(locked)
    assert not audit.empty

