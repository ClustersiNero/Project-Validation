from validation.config.simulation_config import SimulationConfig
from validation.engine.board import collect_board_special_symbols
from validation.engine.rng import RNG
from validation.engine.roll import run_cascade_roll, run_initial_roll
from validation.engine.types import CellExecution, RoundExecution, RoundSpecialSummary

MAX_CASCADE_ROLLS = 100


def run_basic_round(
    config: SimulationConfig,
    rng: RNG,
    round_id: int,
    carried_multiplier: float,
) -> RoundExecution:
    return run_round(
        config=config,
        rng=rng,
        round_id=round_id,
        round_type="basic",
        carried_multiplier=carried_multiplier,
    )


def run_free_round(
    config: SimulationConfig,
    rng: RNG,
    round_id: int,
    carried_multiplier: float,
) -> RoundExecution:
    return run_round(
        config=config,
        rng=rng,
        round_id=round_id,
        round_type="free",
        carried_multiplier=carried_multiplier,
    )


def run_round(
    config: SimulationConfig,
    rng: RNG,
    round_id: int,
    round_type: str,
    carried_multiplier: float,
) -> RoundExecution:
    rolls = []
    roll = run_initial_roll(config=config, rng=rng, round_type=round_type)
    rolls.append(roll)
    next_fill_start_indices = roll.next_fill_start_indices

    while roll.roll_win_amount > 0.0:
        if len(rolls) > MAX_CASCADE_ROLLS:
            raise RuntimeError("cascade roll limit exceeded")
        roll = run_cascade_roll(
            config=config,
            rng=rng,
            roll_id=len(rolls),
            round_type=round_type,
            strip_set_id=roll.strip_set_id,
            multiplier_profile_id=roll.multiplier_profile_id,
            column_strip_ids=roll.column_strip_ids,
            pre_fill_state=roll.gravity_state,
            fill_start_indices=next_fill_start_indices,
        )
        rolls.append(roll)
        next_fill_start_indices = roll.next_fill_start_indices

    base_symbol_win_amount = sum(roll.roll_win_amount for roll in rolls)
    final_state = rolls[-1].gravity_state
    special_summary = summarize_round_specials(
        final_state=final_state,
        paytable=config.paytable,
        carried_multiplier=carried_multiplier,
        bet_level=1.0,
    )
    return RoundExecution(
        round_id=round_id,
        round_type=round_type,
        rolls=rolls,
        base_symbol_win_amount=base_symbol_win_amount,
        carried_multiplier=carried_multiplier,
        round_multiplier_increment=special_summary.round_multiplier_increment,
        round_total_multiplier=special_summary.round_total_multiplier,
        round_scatter_increment=special_summary.round_scatter_increment,
        award_free_rounds=determine_awarded_free_rounds(
            round_type=round_type,
            round_scatter_increment=special_summary.round_scatter_increment,
        ),
        scatter_win_amount=special_summary.scatter_win_amount,
        final_state=final_state,
    )


def summarize_round_specials(
    final_state: list[list[CellExecution | None]],
    paytable: dict,
    carried_multiplier: float,
    bet_level: float,
) -> RoundSpecialSummary:
    _, round_scatter_increment, multiplier_values = collect_board_special_symbols(
        final_state,
        paytable,
    )
    round_multiplier_increment = float(sum(multiplier_values))
    round_total_multiplier = (
        carried_multiplier + round_multiplier_increment
        if round_multiplier_increment > 0
        else 1.0
    )
    scatter_win_amount = evaluate_scatter_win(
        final_state,
        paytable,
        bet_level,
    )
    return RoundSpecialSummary(
        round_multiplier_increment=round_multiplier_increment,
        round_total_multiplier=round_total_multiplier,
        round_scatter_increment=round_scatter_increment,
        scatter_win_amount=scatter_win_amount,
    )


def evaluate_scatter_win(
    final_state: list[list[CellExecution | None]],
    paytable: dict,
    bet_level: float,
) -> float:
    scatter_counts: dict[int, int] = {}
    for row in final_state:
        for cell in row:
            if cell is None:
                continue
            symbol_config = paytable[cell.symbol_id]
            if symbol_config["symbol_type"] == "scatter":
                scatter_counts[cell.symbol_id] = scatter_counts.get(cell.symbol_id, 0) + 1

    scatter_win_amount = 0.0
    for symbol_id, scatter_count in scatter_counts.items():
        payouts = paytable[symbol_id].get("payouts", {})
        qualifying_counts = [
            required_count
            for required_count in payouts
            if required_count <= scatter_count
        ]
        if not qualifying_counts:
            continue

        matched_count = max(qualifying_counts)
        scatter_win_amount += payouts[matched_count] * bet_level

    return scatter_win_amount


def determine_awarded_free_rounds(
    round_type: str,
    round_scatter_increment: int,
) -> int:
    if round_type == "basic" and round_scatter_increment >= 4:
        return 15
    if round_type == "free" and round_scatter_increment >= 3:
        return 5
    return 0
