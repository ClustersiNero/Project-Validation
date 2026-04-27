import pytest
from configs.game import olympus_mini
from validation.api.run_pipeline import run

_SIMULATION_MODE = {1: {"mode_name": "normal", "bet_cost_multiplier": 1.0}}
_MULTIPLIER_DATA = {"value": [2], "weight": {1: [1]}}


def _strip_set(symbol_id: int = 1) -> dict[int, list[int]]:
    return {strip_id: [symbol_id] for strip_id in range(1, 7)}


def _valid_round_config(strip_set_count: int = 1, multiplier_profile_count: int = 1) -> dict:
    return {
        "round_strip_set_weights": [1] + [0] * (strip_set_count - 1),
        "round_multiplier_profile_weights": [1] + [0] * (multiplier_profile_count - 1),
    }


def _implementation_config(
    *,
    basic: dict | None = None,
    free: dict | None = None,
    strip_set_count: int = 1,
    multiplier_profile_count: int = 1,
) -> dict:
    return {
        1: {
            "basic": basic if basic is not None else _valid_round_config(strip_set_count, multiplier_profile_count),
            "free": free if free is not None else _valid_round_config(strip_set_count, multiplier_profile_count),
        },
    }


def test_non_positive_bet_count_raises():
    with pytest.raises(ValueError) as exc_info:
        run({"bet_count": 0})
    assert str(exc_info.value) == "config.bet_count must be positive"


def test_negative_bet_count_raises():
    with pytest.raises(ValueError) as exc_info:
        run({"bet_count": -1})
    assert str(exc_info.value) == "config.bet_count must be positive"


def test_non_positive_mode_id_raises():
    with pytest.raises(ValueError) as exc_info:
        run({"mode_id": 0})
    assert str(exc_info.value) == "config.mode_id must be positive"


def test_bet_count_controls_generated_bets():
    result = run(
        {
            "seed": 1,
            "mode_id": 1,
            "bet_count": 3,
            "simulation_mode": olympus_mini.SIMULATION_MODE,
            "paytable": olympus_mini.PAYTABLE,
            "multiplier_data": olympus_mini.MULTIPLIER_DATA,
            "strip_sets": olympus_mini.STRIP_SETS,
            "implementation_config": olympus_mini.IMPLEMENTATION_CONFIG,
        }
    )
    assert len(result.canonical_result.bets) == 3
    assert result.canonical_result.simulation_metadata.total_bets == 3


def test_missing_round_strip_set_weights_raises():
    implementation_config = _implementation_config(basic={})

    with pytest.raises(ValueError) as exc_info:
        run(
            {
                "simulation_mode": _SIMULATION_MODE,
                "paytable": olympus_mini.PAYTABLE,
                "multiplier_data": _MULTIPLIER_DATA,
                "strip_sets": {1: _strip_set()},
                "implementation_config": implementation_config,
            }
        )

    assert (
        str(exc_info.value)
        == "implementation_config[mode_id][round_type] must define round_strip_set_weights"
    )


def test_missing_free_round_config_raises():
    implementation_config = {
        1: {
            "basic": _valid_round_config(),
        },
    }

    with pytest.raises(ValueError) as exc_info:
        run(
            {
                "simulation_mode": _SIMULATION_MODE,
                "paytable": olympus_mini.PAYTABLE,
                "multiplier_data": _MULTIPLIER_DATA,
                "strip_sets": {1: _strip_set()},
                "implementation_config": implementation_config,
            }
        )

    assert str(exc_info.value) == "implementation_config[mode_id] must define config for round_type 'free'"


def test_missing_config_block_raises():
    with pytest.raises(ValueError) as exc_info:
        run(
            {
                "simulation_mode": olympus_mini.SIMULATION_MODE,
                "paytable": olympus_mini.PAYTABLE,
                "multiplier_data": olympus_mini.MULTIPLIER_DATA,
                "implementation_config": olympus_mini.IMPLEMENTATION_CONFIG,
            }
        )

    assert str(exc_info.value) == "config.strip_sets must be provided"


def test_round_strip_set_weights_must_be_valid_weights():
    implementation_config = _implementation_config(
        basic={
            "round_strip_set_weights": [0, 0, 0],
            "round_multiplier_profile_weights": [1],
        },
        strip_set_count=3,
    )

    with pytest.raises(ValueError) as exc_info:
        run(
            {
                "simulation_mode": _SIMULATION_MODE,
                "paytable": olympus_mini.PAYTABLE,
                "multiplier_data": _MULTIPLIER_DATA,
                "strip_sets": {1: _strip_set(), 2: _strip_set(), 3: _strip_set()},
                "implementation_config": implementation_config,
            }
        )

    assert str(exc_info.value) == "sum(round_strip_set_weights) must be positive"


def test_reachable_strip_set_ids_must_exist():
    implementation_config = _implementation_config(
        basic={
            "round_strip_set_weights": [1, 1, 1],
            "round_multiplier_profile_weights": [1],
        },
        strip_set_count=3,
    )

    with pytest.raises(ValueError) as exc_info:
        run(
            {
                "simulation_mode": _SIMULATION_MODE,
                "paytable": olympus_mini.PAYTABLE,
                "multiplier_data": _MULTIPLIER_DATA,
                "strip_sets": {1: _strip_set(), 2: _strip_set(), 4: _strip_set()},
                "implementation_config": implementation_config,
            }
        )

    assert str(exc_info.value) == "reachable strip_set_id values must exist in strip_sets"


def test_reachable_strip_sets_must_define_six_non_empty_strips():
    implementation_config = _implementation_config()

    with pytest.raises(ValueError) as exc_info:
        run(
            {
                "simulation_mode": _SIMULATION_MODE,
                "paytable": olympus_mini.PAYTABLE,
                "multiplier_data": _MULTIPLIER_DATA,
                "strip_sets": {1: {1: [1]}},
                "implementation_config": implementation_config,
            }
        )

    assert str(exc_info.value) == "strip sets must define exactly 6 strips"


def test_missing_round_multiplier_profile_weights_raises():
    implementation_config = _implementation_config(
        basic={
            "round_strip_set_weights": [1, 0, 0],
        },
        strip_set_count=3,
    )

    with pytest.raises(ValueError) as exc_info:
        run(
            {
                "simulation_mode": _SIMULATION_MODE,
                "paytable": olympus_mini.PAYTABLE,
                "multiplier_data": _MULTIPLIER_DATA,
                "strip_sets": {1: _strip_set(), 2: _strip_set(), 3: _strip_set()},
                "implementation_config": implementation_config,
            }
        )

    assert (
        str(exc_info.value)
        == "implementation_config[mode_id][round_type] must define round_multiplier_profile_weights"
    )


def test_reachable_multiplier_profiles_must_exist():
    implementation_config = _implementation_config(
        basic={
            "round_strip_set_weights": [1, 0, 0, 0],
            "round_multiplier_profile_weights": [0, 0, 1],
        },
        strip_set_count=4,
        multiplier_profile_count=3,
    )
    multiplier_data = {
        "value": [2],
        "weight": {
            1: [1],
        },
    }

    with pytest.raises(ValueError) as exc_info:
        run(
            {
                "simulation_mode": _SIMULATION_MODE,
                "paytable": olympus_mini.PAYTABLE,
                "multiplier_data": multiplier_data,
                "strip_sets": olympus_mini.STRIP_SETS,
                "implementation_config": implementation_config,
            }
        )

    assert str(exc_info.value) == "reachable multiplier_profile_id values must exist in multiplier_data.weight"
