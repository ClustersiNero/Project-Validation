from validation.canonical.schema import (
    BetRecord,
    CanonicalResult,
    Cell,
    RollRecord,
    RoundRecord,
    SimulationMetadata,
)
from validation.config.simulation_config import SimulationConfig
from validation.engine.types import (
    BetExecution,
    CellExecution,
    RollExecution,
    RoundExecution,
    SimulationExecution,
)


def record_canonical_result(
    config: SimulationConfig,
    execution: SimulationExecution,
) -> CanonicalResult:
    metadata = SimulationMetadata(
        simulation_id=f"simulation-seed-{config.seed}",
        config_id="simulation_config",
        config_version="0.1.0",
        engine_version="engine.v1",
        schema_version="canonical.v1",
        mode=_mode_name(config),
        seed=config.seed,
        bet_amount=1.0,
        bet_level=1.0,
        total_bets=execution.bet_count,
        timestamp="1970-01-01T00:00:00Z",
    )
    return CanonicalResult(
        simulation_metadata=metadata,
        bets=[record_bet(bet_execution) for bet_execution in execution.bets],
    )


def record_bet(execution: BetExecution) -> BetRecord:
    rounds = [record_round(round_execution) for round_execution in execution.rounds]
    basic_win_amount = sum(rnd.round_win_amount for rnd in rounds if rnd.round_type == "basic")
    free_win_amount = sum(rnd.round_win_amount for rnd in rounds if rnd.round_type == "free")
    return BetRecord(
        bet_id=execution.bet_id,
        bet_win_amount=basic_win_amount + free_win_amount,
        basic_win_amount=basic_win_amount,
        free_win_amount=free_win_amount,
        round_count=len(rounds),
        bet_final_state=record_optional_board(execution.final_state),
        rounds=rounds,
    )


def record_round(execution: RoundExecution) -> RoundRecord:
    rolls = [record_roll(roll_execution) for roll_execution in execution.rolls]
    round_win_amount = (
        execution.base_symbol_win_amount * execution.round_total_multiplier
        + execution.scatter_win_amount
    )
    return RoundRecord(
        round_id=execution.round_id,
        round_type=execution.round_type,
        round_win_amount=round_win_amount,
        base_symbol_win_amount=execution.base_symbol_win_amount,
        carried_multiplier=execution.carried_multiplier,
        round_multiplier_increment=execution.round_multiplier_increment,
        round_total_multiplier=execution.round_total_multiplier,
        round_scatter_increment=execution.round_scatter_increment,
        award_free_rounds=execution.award_free_rounds,
        scatter_win_amount=execution.scatter_win_amount,
        roll_count=len(rolls),
        round_final_state=record_optional_board(execution.final_state),
        rolls=rolls,
    )


def record_roll(execution: RollExecution) -> RollRecord:
    return RollRecord(
        roll_id=execution.roll_id,
        roll_type=execution.roll_type,
        roll_win_amount=execution.roll_win_amount,
        strip_set_id=execution.strip_set_id,
        multiplier_profile_id=execution.multiplier_profile_id,
        column_strip_ids=list(execution.column_strip_ids),
        refill_start_indices=list(execution.refill_start_indices),
        refill_end_indices=list(execution.refill_end_indices),
        roll_filled_state=record_board(execution.filled_state),
        roll_final_state=record_optional_board(execution.final_state),
        roll_multi_symbols_num=execution.multi_symbols_num,
        roll_multi_symbols_carry=execution.multi_symbols_carry,
        roll_scatter_symbols_num=execution.scatter_symbols_num,
    )


def record_board(board: list[list[CellExecution]]) -> list[list[Cell]]:
    return [[record_cell(cell) for cell in row] for row in board]


def record_optional_board(
    board: list[list[CellExecution | None]],
) -> list[list[Cell | None]]:
    return [
        [None if cell is None else record_cell(cell) for cell in row]
        for row in board
    ]


def record_cell(cell: CellExecution) -> Cell:
    return Cell(symbol_id=cell.symbol_id, multiplier_value=cell.multiplier_value)


def _mode_name(config: SimulationConfig) -> str:
    if config.simulation_mode is None:
        return "normal"
    return config.simulation_mode[config.mode_id]["mode_name"]
