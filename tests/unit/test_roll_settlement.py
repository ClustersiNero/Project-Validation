import pytest

from validation.api import run
import validation.engine.engine as engine_module
from validation.engine.engine import (
    CellExecution,
    apply_gravity,
    evaluate_regular_wins,
    refill_board,
)
from validation.engine.rng import RNG


def test_regular_win_evaluation_uses_highest_qualified_payout():
    board = [
        [CellExecution(1), CellExecution(1), CellExecution(1)],
        [CellExecution(1), CellExecution(1), CellExecution(1)],
        [CellExecution(1), CellExecution(1), CellExecution(2)],
    ]
    paytable = {
        1: {"symbol_name": "regular", "symbol_type": "regular", "payouts": {6: 1.5, 8: 4.0}},
        2: {"symbol_name": "other", "symbol_type": "regular", "payouts": {8: 1.0}},
    }

    evaluation = evaluate_regular_wins(board, paytable, bet_level=2.0)

    assert evaluation.win_amount == 8.0
    assert evaluation.winning_positions == {
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
    }


def test_gravity_moves_surviving_cells_to_bottom_of_each_column():
    bottom_cell = CellExecution(2)
    middle_cell = CellExecution(3)
    top_cell = CellExecution(4)
    board = [
        [None],
        [bottom_cell],
        [None],
        [middle_cell],
        [top_cell],
    ]

    settled = apply_gravity(board)

    assert settled == [
        [bottom_cell],
        [middle_cell],
        [top_cell],
        [None],
        [None],
    ]


def test_refill_uses_same_column_strip_from_next_index():
    board = [
        [CellExecution(2)],
        [CellExecution(3)],
        [None],
        [None],
        [None],
    ]
    paytable = {
        2: {"symbol_name": "two", "symbol_type": "regular", "payouts": {}},
        3: {"symbol_name": "three", "symbol_type": "regular", "payouts": {}},
        7: {"symbol_name": "seven", "symbol_type": "regular", "payouts": {}},
        8: {"symbol_name": "eight", "symbol_type": "regular", "payouts": {}},
        9: {"symbol_name": "nine", "symbol_type": "regular", "payouts": {}},
    }

    refill_result = refill_board(
        board=board,
        strip_set={4: [7, 8, 9]},
        column_strip_ids=[4],
        next_strip_indices=[1],
        paytable=paytable,
        multiplier_data={"value": [2], "weight": {1: [1]}},
        multiplier_profile_id=1,
        rng=RNG(seed=0),
    )

    assert [[cell.symbol_id for cell in row] for row in refill_result.board] == [
        [2],
        [3],
        [8],
        [9],
        [7],
    ]
    assert refill_result.next_strip_indices == [1]


def test_pipeline_clears_regular_wins_and_records_canonical_final_state():
    paytable = {
        1: {"symbol_name": "winning_regular", "symbol_type": "regular", "payouts": {8: 1.0}},
        2: {"symbol_name": "cascade_regular", "symbol_type": "regular", "payouts": {8: 2.0}},
        3: {"symbol_name": "non_winning_regular", "symbol_type": "regular", "payouts": {99: 1.0}},
    }
    strip_sets = {
        1: {
            strip_id: [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3]
            for strip_id in range(1, 7)
        },
    }
    implementation_config = {
        1: {
            "basic": {
                "round_strip_set_weights": [1],
                "round_multiplier_profile_weights": [1],
            },
            "free": {
                "round_strip_set_weights": [1],
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

    bet = result.canonical_result.bets[0]
    rnd = bet.rounds[0]
    roll = rnd.rolls[0]
    final_symbol_ids = {
        cell.symbol_id
        for row in roll.roll_final_state
        for cell in row
        if cell is not None
    }

    assert rnd.roll_count == 2
    assert [recorded_roll.roll_type for recorded_roll in rnd.rolls] == ["initial", "cascade"]
    assert [recorded_roll.roll_id for recorded_roll in rnd.rolls] == [0, 1]
    assert [recorded_roll.roll_win_amount for recorded_roll in rnd.rolls] == [3.0, 2.0]
    assert rnd.base_symbol_win_amount == 5.0
    assert rnd.round_win_amount == 5.0
    assert len(roll.roll_final_state) == 5
    assert all(len(row) == 6 for row in roll.roll_final_state)
    assert all(cell is not None for row in roll.roll_final_state for cell in row)
    assert 2 in final_symbol_ids
    assert rnd.rolls[1].roll_filled_state == roll.roll_final_state
    assert rnd.rolls[0].column_strip_ids == rnd.rolls[1].column_strip_ids
    assert rnd.rolls[0].refill_end_indices == rnd.rolls[1].refill_start_indices
    assert all(len(recorded_roll.column_strip_ids) == 6 for recorded_roll in rnd.rolls)
    assert all(len(recorded_roll.refill_start_indices) == 6 for recorded_roll in rnd.rolls)
    assert all(len(recorded_roll.refill_end_indices) == 6 for recorded_roll in rnd.rolls)
    assert rnd.round_final_state == rnd.rolls[-1].roll_final_state
    assert bet.bet_final_state == rnd.rolls[-1].roll_final_state


def test_round_special_summary_uses_final_board_for_multiplier_and_scatter():
    paytable = {
        1: {"symbol_name": "regular", "symbol_type": "regular", "payouts": {}},
        10: {"symbol_name": "scatter", "symbol_type": "scatter", "payouts": {4: 3.0, 5: 5.0}},
        11: {"symbol_name": "multiplier", "symbol_type": "multiplier"},
    }
    strip_sets = {
        1: {
            1: [10],
            2: [10],
            3: [10],
            4: [10],
            5: [11],
            6: [1],
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
            "multiplier_data": {"value": [5], "weight": {1: [1]}},
            "strip_sets": strip_sets,
            "implementation_config": implementation_config,
        }
    )

    rnd = result.canonical_result.bets[0].rounds[0]

    assert rnd.base_symbol_win_amount == 0.0
    assert rnd.round_multiplier_increment == 25.0
    assert rnd.round_total_multiplier == 25.0
    assert rnd.round_scatter_increment == 20
    assert rnd.award_free_rounds == 15
    assert rnd.scatter_win_amount == 5.0
    assert rnd.round_win_amount == 5.0


def test_basic_award_executes_free_rounds_and_updates_carried_multiplier():
    paytable = {
        1: {"symbol_name": "regular_win", "symbol_type": "regular", "payouts": {8: 1.0}},
        2: {"symbol_name": "regular_low", "symbol_type": "regular", "payouts": {99: 1.0}},
        10: {"symbol_name": "scatter", "symbol_type": "scatter", "payouts": {4: 3.0, 5: 5.0}},
        11: {"symbol_name": "multiplier", "symbol_type": "multiplier"},
    }
    strip_sets = {
        1: {
            1: [10],
            2: [10],
            3: [10],
            4: [10],
            5: [2],
            6: [2],
        },
        2: {
            1: [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
            2: [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
            3: [11],
            4: [2],
            5: [2],
            6: [2],
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
            "seed": 1,
            "mode_id": 1,
            "bet_count": 1,
            "simulation_mode": {1: {"mode_name": "normal", "bet_cost_multiplier": 1.0}},
            "paytable": paytable,
            "multiplier_data": {"value": [2], "weight": {1: [1]}},
            "strip_sets": strip_sets,
            "implementation_config": implementation_config,
        }
    )

    bet = result.canonical_result.bets[0]
    rounds = bet.rounds

    assert bet.round_count == 16
    assert [round_.round_type for round_ in rounds] == ["basic"] + ["free"] * 15
    assert rounds[0].award_free_rounds == 15
    assert all(round_.award_free_rounds == 0 for round_ in rounds[1:])
    assert rounds[1].carried_multiplier == 0.0
    assert rounds[1].base_symbol_win_amount == 1.0
    assert rounds[1].round_multiplier_increment == 10.0
    assert rounds[1].round_total_multiplier == 10.0
    assert rounds[2].carried_multiplier == 10.0
    assert rounds[2].base_symbol_win_amount == 0.0
    assert rounds[3].carried_multiplier == 10.0
    assert rounds[3].base_symbol_win_amount == 1.0
    assert rounds[3].round_total_multiplier == 20.0
    assert rounds[4].carried_multiplier == 20.0
    assert bet.basic_win_amount == rounds[0].round_win_amount
    assert bet.free_win_amount == sum(round_.round_win_amount for round_ in rounds[1:])


def test_cascade_roll_limit_prevents_infinite_refill_loop():
    paytable = {
        1: {"symbol_name": "always_winning", "symbol_type": "regular", "payouts": {1: 1.0}},
    }
    strip_sets = {
        1: {strip_id: [1] for strip_id in range(1, 7)},
    }
    implementation_config = {
        1: {
            "basic": {
                "round_strip_set_weights": [1],
                "round_multiplier_profile_weights": [1],
            },
            "free": {
                "round_strip_set_weights": [1],
                "round_multiplier_profile_weights": [1],
            },
        },
    }

    with pytest.raises(RuntimeError) as exc_info:
        run(
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

    assert str(exc_info.value) == "cascade roll limit exceeded"


def test_free_round_limit_prevents_infinite_award_queue(monkeypatch):
    paytable = {
        10: {"symbol_name": "scatter", "symbol_type": "scatter", "payouts": {}},
    }
    strip_sets = {
        1: {strip_id: [10] for strip_id in range(1, 7)},
    }
    implementation_config = {
        1: {
            "basic": {
                "round_strip_set_weights": [1],
                "round_multiplier_profile_weights": [1],
            },
            "free": {
                "round_strip_set_weights": [1],
                "round_multiplier_profile_weights": [1],
            },
        },
    }
    monkeypatch.setattr(engine_module, "MAX_FREE_ROUNDS_PER_BET", 2)

    with pytest.raises(RuntimeError) as exc_info:
        run(
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

    assert str(exc_info.value) == "free round limit exceeded"
