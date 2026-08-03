"""Optional mixed-effects model for separating territory and rep variation."""
from __future__ import annotations
import pandas as pd


def fit_mixed_effects(history: pd.DataFrame):
    """Fit a rep-random-intercept model with region variance components.

    This is a diagnostic challenger, not a causal rep-performance score.
    Assignment of reps to territories is non-random, so effects require field
    interpretation and sensitivity analysis.
    """
    import statsmodels.formula.api as smf

    formula = (
        "bookings_m ~ account_potential_m + starting_pipeline_m + account_count "
        "+ rep_tenure_months + historical_conversion + industry_concentration "
        "+ C(quarter_of_year)"
    )
    model = smf.mixedlm(
        formula, history, groups=history["rep_id"],
        vc_formula={"territory": "0 + C(territory_id)", "region": "0 + C(region)"},
        re_formula="1",
    )
    return model.fit(method="lbfgs", maxiter=400, disp=False)

