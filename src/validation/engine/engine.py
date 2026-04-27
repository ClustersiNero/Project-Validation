from collections.abc import Callable

from validation.config.simulation_config import SimulationConfig
from validation.engine.bet import run_bet
from validation.engine.rng import RNG
from validation.engine.types import SimulationExecution


def run_engine(
    config: SimulationConfig,
    rng: RNG,
    progress_callback: Callable[[int, int], None] | None = None,
) -> SimulationExecution:
    bets = []
    for bet_id in range(config.bet_count):
        bets.append(run_bet(config=config, rng=rng, bet_id=bet_id))
        if progress_callback is not None:
            progress_callback(bet_id + 1, config.bet_count)
    return SimulationExecution(
        seed=config.seed,
        mode_id=config.mode_id,
        bet_count=config.bet_count,
        bets=bets,
    )
