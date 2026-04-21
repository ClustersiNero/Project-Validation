from validation.config.simulation_config import SimulationConfig
from validation.engine.rng import RNG
from validation.engine.round import run_basic_round, run_free_round
from validation.engine.types import BetExecution

MAX_FREE_ROUNDS_PER_BET = 1000


def run_bet(
    config: SimulationConfig,
    rng: RNG,
    bet_id: int,
) -> BetExecution:
    rounds = []
    carried_multiplier = 0.0
    next_round_id = 0
    remaining_award_rounds = 0

    basic_round = run_basic_round(
        config=config,
        rng=rng,
        round_id=next_round_id,
        carried_multiplier=carried_multiplier,
    )
    rounds.append(basic_round)
    next_round_id += 1
    remaining_award_rounds += basic_round.award_free_rounds

    while remaining_award_rounds > 0:
        if next_round_id > MAX_FREE_ROUNDS_PER_BET:
            raise RuntimeError("free round limit exceeded")
        free_round = run_free_round(
            config=config,
            rng=rng,
            round_id=next_round_id,
            carried_multiplier=carried_multiplier,
        )
        rounds.append(free_round)
        next_round_id += 1
        remaining_award_rounds -= 1
        remaining_award_rounds += free_round.award_free_rounds

        if free_round.base_symbol_win_amount > 0.0:
            carried_multiplier += free_round.round_multiplier_increment

    final_state = rounds[-1].final_state

    return BetExecution(bet_id=bet_id, rounds=rounds, final_state=final_state)
