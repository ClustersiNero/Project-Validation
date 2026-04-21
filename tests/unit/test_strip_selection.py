import pytest

from configs.game import olympus_mini
from validation.api import run
from validation.engine.selection import choose_round_strip_set_id, choose_weighted_id
from validation.engine.rng import RNG


def test_same_seed_produces_same_strip_set_id():
    rng_a = RNG(seed=42)
    rng_b = RNG(seed=42)

    selected_a = choose_round_strip_set_id(olympus_mini.IMPLEMENTATION_CONFIG, 1, "basic", rng_a)
    selected_b = choose_round_strip_set_id(olympus_mini.IMPLEMENTATION_CONFIG, 1, "basic", rng_b)

    assert selected_a == selected_b


def test_zero_weight_id_is_unreachable_when_other_weights_are_positive():
    selected_ids = {
        choose_round_strip_set_id(olympus_mini.IMPLEMENTATION_CONFIG, 1, "basic", RNG(seed=seed))
        for seed in range(100)
    }

    assert 3 not in selected_ids
    assert selected_ids <= {1, 2}


def test_index_to_id_mapping_returns_one_based_id():
    rng = RNG(seed=0)

    assert choose_weighted_id([0, 0, 1], rng) == 3


def test_pipeline_records_config_selected_strip_set_id():
    implementation_config = {
        1: {
            "basic": {
                "round_strip_set_weights": [0, 0, 1],
                "round_multiplier_profile_weights": [1],
            },
            "free": {
                "round_strip_set_weights": [1, 0, 0],
                "round_multiplier_profile_weights": [1],
            },
        },
    }

    result = run(
        {
            "seed": 0,
            "mode_id": 1,
            "bet_count": 1,
            "simulation_mode": {1: {"mode_name": "normal", "bet_cost_multiplier": 1.0}},
            "paytable": olympus_mini.PAYTABLE,
            "multiplier_data": {"value": [2], "weight": {1: [1]}},
            "strip_sets": olympus_mini.STRIP_SETS,
            "implementation_config": implementation_config,
        }
    )

    roll = result.canonical_result.bets[0].rounds[0].rolls[0]
    assert roll.strip_set_id == 3


def test_pipeline_records_board_from_selected_strip_set():
    paytable = {
        symbol_id: {"symbol_name": f"symbol_{symbol_id}", "symbol_type": "regular", "payouts": {}}
        for symbol_id in range(1, 9)
    }
    strip_sets = {
        1: {strip_id: [7] for strip_id in range(1, 7)},
        2: {strip_id: [8] for strip_id in range(1, 7)},
        3: {strip_id: [strip_id] for strip_id in range(1, 7)},
    }
    implementation_config = {
        1: {
            "basic": {
                "round_strip_set_weights": [0, 0, 1],
                "round_multiplier_profile_weights": [1],
            },
            "free": {
                "round_strip_set_weights": [1, 0, 0],
                "round_multiplier_profile_weights": [1],
            },
        },
    }

    result = run(
        {
            "seed": 0,
            "mode_id": 1,
            "bet_count": 1,
            "simulation_mode": {1: {"mode_name": "normal", "bet_cost_multiplier": 1.0}},
            "paytable": paytable,
            "multiplier_data": {"value": [2], "weight": {1: [1]}},
            "strip_sets": strip_sets,
            "implementation_config": implementation_config,
        }
    )

    board = result.canonical_result.bets[0].rounds[0].rolls[0].roll_filled_state
    symbol_ids = {cell.symbol_id for row in board for cell in row}

    assert len(board) == 5
    assert all(len(row) == 6 for row in board)
    assert symbol_ids == {1, 2, 3, 4, 5, 6}


def test_pipeline_records_special_symbol_counts_from_initial_board():
    paytable = {
        1: {"symbol_name": "regular", "symbol_type": "regular", "payouts": {}},
        10: {"symbol_name": "scatter", "symbol_type": "scatter", "payouts": {}},
        11: {"symbol_name": "multiplier", "symbol_type": "multiplier"},
    }
    strip_sets = {
        1: {
            1: [11],
            2: [10],
            3: [1],
            4: [1],
            5: [10],
            6: [11],
        },
        2: {
            1: [1],
            2: [1],
            3: [1],
            4: [1],
            5: [1],
            6: [1],
        },
    }
    implementation_config = {
        1: {
            "basic": {
                "round_strip_set_weights": [1, 0],
                "round_multiplier_profile_weights": [1],
            },
            "free": {
                "round_strip_set_weights": [0, 1],
                "round_multiplier_profile_weights": [1],
            },
        },
    }

    result = run(
        {
            "seed": 0,
            "mode_id": 1,
            "bet_count": 1,
            "simulation_mode": {1: {"mode_name": "normal", "bet_cost_multiplier": 1.0}},
            "paytable": paytable,
            "multiplier_data": {"value": [2], "weight": {1: [1]}},
            "strip_sets": strip_sets,
            "implementation_config": implementation_config,
        }
    )

    roll = result.canonical_result.bets[0].rounds[0].rolls[0]
    assert roll.roll_multi_symbols_num == 10
    assert roll.roll_scatter_symbols_num == 10


def test_pipeline_records_multiplier_profile_and_sampled_multiplier_values():
    paytable = {
        1: {"symbol_name": "regular", "symbol_type": "regular", "payouts": {}},
        11: {"symbol_name": "multiplier", "symbol_type": "multiplier"},
    }
    strip_sets = {
        1: {
            1: [11],
            2: [1],
            3: [1],
            4: [1],
            5: [1],
            6: [1],
        },
    }
    implementation_config = {
        1: {
            "basic": {
                "round_strip_set_weights": [1],
                "round_multiplier_profile_weights": [0, 1],
            },
            "free": {
                "round_strip_set_weights": [1],
                "round_multiplier_profile_weights": [1, 0],
            },
        },
    }
    multiplier_data = {
        "value": [2, 5],
        "weight": {
            1: [1, 0],
            2: [0, 1],
        },
    }

    result = run(
        {
            "seed": 0,
            "mode_id": 1,
            "bet_count": 1,
            "simulation_mode": {1: {"mode_name": "normal", "bet_cost_multiplier": 1.0}},
            "paytable": paytable,
            "multiplier_data": multiplier_data,
            "strip_sets": strip_sets,
            "implementation_config": implementation_config,
        }
    )

    roll = result.canonical_result.bets[0].rounds[0].rolls[0]
    multiplier_values = [
        cell.multiplier_value
        for row in roll.roll_filled_state
        for cell in row
        if cell.symbol_id == 11
    ]

    assert roll.multiplier_profile_id == 2
    assert multiplier_values == [5, 5, 5, 5, 5]
    assert roll.roll_multi_symbols_carry == [5, 5, 5, 5, 5]
    assert result.canonical_result.bets[0].rounds[0].round_multiplier_increment == 25


def test_all_zero_weights_raise():
    with pytest.raises(ValueError) as exc_info:
        choose_weighted_id([0, 0, 0], RNG(seed=0))

    assert str(exc_info.value) == "sum(weights) must be positive"
