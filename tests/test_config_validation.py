import pytest
from validation.api.run_pipeline import run


def test_empty_rounds_raises():
    with pytest.raises(ValueError) as exc_info:
        run({"rounds": []})
    assert str(exc_info.value) == "config.rounds must be non-empty"


def test_empty_roll_wins_raises():
    with pytest.raises(ValueError) as exc_info:
        run({"rounds": [{"round_id": 0, "round_type": "basic", "roll_wins": []}]})
    assert str(exc_info.value) == "config.rounds[0].roll_wins must be non-empty"


def test_negative_roll_win_raises():
    with pytest.raises(ValueError) as exc_info:
        run({"rounds": [{"round_id": 0, "round_type": "basic", "roll_wins": [0.0, -1.0]}]})
    assert str(exc_info.value) == "config.rounds[0].roll_wins[1] must be non-negative"


def test_invalid_round_type_raises():
    with pytest.raises(ValueError) as exc_info:
        run({"rounds": [{"round_id": 0, "round_type": "invalid", "roll_wins": [0.0]}]})
    assert str(exc_info.value) == "config.rounds[0].round_type must be 'basic' or 'free'"


def test_free_round_type_is_allowed():
    result = run({"rounds": [{"round_id": 0, "round_type": "free", "roll_wins": [0.0]}]})
    assert result.canonical_result.bets[0].rounds[0].round_type == "free"


def test_round_id_mismatch_raises():
    with pytest.raises(ValueError) as exc_info:
        run({"rounds": [{"round_id": 1, "round_type": "basic", "roll_wins": [0.0]}]})
    assert str(exc_info.value) == "config.rounds[0].round_id must equal its position"
