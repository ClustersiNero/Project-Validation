from validation.config.simulation_config import SimulationConfig
from validation.engine.board import (
    apply_gravity,
    clear_winning_positions,
    collect_board_special_symbols,
    generate_initial_board,
    refill_board,
)
from validation.engine.rng import RNG
from validation.engine.selection import (
    choose_round_multiplier_profile_id,
    choose_round_strip_set_id,
)
from validation.engine.types import (
    CellExecution,
    RegularWinEvaluation,
    RollExecution,
    RollSettlement,
)


def run_initial_roll(
    config: SimulationConfig,
    rng: RNG,
    round_type: str,
) -> RollExecution:
    strip_set_id = choose_round_strip_set_id(
        config.implementation_config,
        config.mode_id,
        round_type,
        rng,
    )
    multiplier_profile_id = choose_round_multiplier_profile_id(
        config.implementation_config,
        config.mode_id,
        round_type,
        rng,
    )
    board_generation = generate_initial_board(
        strip_set=config.strip_sets[strip_set_id],
        paytable=config.paytable,
        multiplier_data=config.multiplier_data,
        multiplier_profile_id=multiplier_profile_id,
        rng=rng,
    )
    filled_state = board_generation.board
    multi_symbols_num, scatter_symbols_num, multi_symbols_carry = collect_board_special_symbols(
        filled_state,
        config.paytable,
    )
    settlement = settle_regular_wins(
        board=filled_state,
        paytable=config.paytable,
        strip_set=config.strip_sets[strip_set_id],
        column_strip_ids=board_generation.column_strip_ids,
        next_strip_indices=board_generation.next_strip_indices,
        multiplier_data=config.multiplier_data,
        multiplier_profile_id=multiplier_profile_id,
        rng=rng,
        bet_level=1.0,
    )

    return RollExecution(
        roll_id=0,
        roll_type="initial",
        roll_win_amount=settlement.win_amount,
        strip_set_id=strip_set_id,
        multiplier_profile_id=multiplier_profile_id,
        column_strip_ids=board_generation.column_strip_ids,
        refill_start_indices=settlement.refill_start_indices,
        refill_end_indices=settlement.refill_end_indices,
        filled_state=filled_state,
        final_state=settlement.final_state,
        multi_symbols_num=multi_symbols_num,
        multi_symbols_carry=multi_symbols_carry,
        scatter_symbols_num=scatter_symbols_num,
    )


def run_cascade_roll(
    config: SimulationConfig,
    rng: RNG,
    roll_id: int,
    round_type: str,
    strip_set_id: int,
    multiplier_profile_id: int,
    column_strip_ids: list[int],
    next_strip_indices: list[int],
    filled_state: list[list[CellExecution]],
) -> RollExecution:
    multi_symbols_num, scatter_symbols_num, multi_symbols_carry = collect_board_special_symbols(
        filled_state,
        config.paytable,
    )
    settlement = settle_regular_wins(
        board=filled_state,
        paytable=config.paytable,
        strip_set=config.strip_sets[strip_set_id],
        column_strip_ids=column_strip_ids,
        next_strip_indices=next_strip_indices,
        multiplier_data=config.multiplier_data,
        multiplier_profile_id=multiplier_profile_id,
        rng=rng,
        bet_level=1.0,
    )

    return RollExecution(
        roll_id=roll_id,
        roll_type="cascade",
        roll_win_amount=settlement.win_amount,
        strip_set_id=strip_set_id,
        multiplier_profile_id=multiplier_profile_id,
        column_strip_ids=column_strip_ids,
        refill_start_indices=settlement.refill_start_indices,
        refill_end_indices=settlement.refill_end_indices,
        filled_state=filled_state,
        final_state=settlement.final_state,
        multi_symbols_num=multi_symbols_num,
        multi_symbols_carry=multi_symbols_carry,
        scatter_symbols_num=scatter_symbols_num,
    )


def settle_regular_wins(
    board: list[list[CellExecution]],
    paytable: dict,
    strip_set: dict[int, list[int]],
    column_strip_ids: list[int],
    next_strip_indices: list[int],
    multiplier_data: dict,
    multiplier_profile_id: int,
    rng: RNG,
    bet_level: float,
) -> RollSettlement:
    evaluation = evaluate_regular_wins(board, paytable, bet_level)
    cleared_board = clear_winning_positions(board, evaluation.winning_positions)
    settled_board = apply_gravity(cleared_board)
    refill_start_indices = list(next_strip_indices)
    refill_result = refill_board(
        board=settled_board,
        strip_set=strip_set,
        column_strip_ids=column_strip_ids,
        next_strip_indices=refill_start_indices,
        paytable=paytable,
        multiplier_data=multiplier_data,
        multiplier_profile_id=multiplier_profile_id,
        rng=rng,
    )
    return RollSettlement(
        win_amount=evaluation.win_amount,
        final_state=refill_result.board,
        refill_start_indices=refill_start_indices,
        refill_end_indices=refill_result.next_strip_indices,
    )


def evaluate_regular_wins(
    board: list[list[CellExecution]],
    paytable: dict,
    bet_level: float,
) -> RegularWinEvaluation:
    symbol_counts: dict[int, int] = {}
    symbol_positions: dict[int, set[tuple[int, int]]] = {}

    for row_index, row in enumerate(board):
        for col_index, cell in enumerate(row):
            symbol_config = paytable[cell.symbol_id]
            if symbol_config["symbol_type"] != "regular":
                continue
            symbol_counts[cell.symbol_id] = symbol_counts.get(cell.symbol_id, 0) + 1
            symbol_positions.setdefault(cell.symbol_id, set()).add((row_index, col_index))

    win_amount = 0.0
    winning_positions: set[tuple[int, int]] = set()
    for symbol_id, count in symbol_counts.items():
        payouts = paytable[symbol_id].get("payouts", {})
        qualifying_counts = [required_count for required_count in payouts if required_count <= count]
        if not qualifying_counts:
            continue

        matched_count = max(qualifying_counts)
        win_amount += payouts[matched_count] * bet_level
        winning_positions.update(symbol_positions[symbol_id])

    return RegularWinEvaluation(
        win_amount=win_amount,
        winning_positions=winning_positions,
    )


def has_regular_win(board: list[list[CellExecution]], paytable: dict) -> bool:
    return bool(evaluate_regular_wins(board, paytable, bet_level=1.0).winning_positions)
