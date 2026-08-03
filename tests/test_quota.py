from models.attainment import fit_attainment_models, score_capacity
from models.quota import allocate_enterprise_quota
from synthetic_data.generate_all import generate


def test_quota_reconciles_to_financial_plan():
    history, _, _ = generate()
    model = fit_attainment_models(history)
    capacity = score_capacity(model, history.loc[history.quarter == history.quarter.max()])
    quota = allocate_enterprise_quota(capacity, financial_plan_m=24, coverage_factor=1.15)
    assert abs(quota.recommended_quota_m.sum() - 27.6) < 1e-6
    assert quota.expected_attainment.notna().all()


def test_quota_change_limits_hold_when_feasible():
    history, _, _ = generate()
    model = fit_attainment_models(history)
    capacity = score_capacity(model, history.loc[history.quarter == history.quarter.max()])
    quota = allocate_enterprise_quota(capacity, 24, 1.15, max_change=.25)
    assert quota.quota_change_pct.abs().max() <= .250001

