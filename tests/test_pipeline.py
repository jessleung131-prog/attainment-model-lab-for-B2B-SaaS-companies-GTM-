from pathlib import Path
from run_pipeline import main


def test_end_to_end_pipeline(tmp_path: Path):
    main(str(tmp_path))
    expected = {
        "attainment_leaderboard.csv", "attainment_validation.csv", "territory_capacity.csv",
        "enterprise_quota.csv", "enterprise_moves.csv", "cs_moves.csv",
        "decision_queue.csv", "controls.json",
    }
    assert expected.issubset({p.name for p in tmp_path.iterdir()})
