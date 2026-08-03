import numpy as np
from models.attainment import fit_attainment_models, score_capacity
from models.common import assert_point_in_time_contract
from synthetic_data.generate_all import generate


def test_point_in_time_contract_and_chronological_validation():
    history, _, _ = generate()
    assert_point_in_time_contract(history)
    result = fit_attainment_models(history)
    assert result.leaderboard.iloc[0].wmape < 0.20
    assert set(result.validation_predictions.quarter) == {history.quarter.max()}


def test_capacity_has_ordered_intervals():
    history, _, _ = generate()
    result = fit_attainment_models(history)
    capacity = score_capacity(result, history.loc[history.quarter == history.quarter.max()])
    assert np.all(capacity.capacity_low_m <= capacity.expected_bookings_m)
    assert np.all(capacity.expected_bookings_m <= capacity.capacity_high_m)

