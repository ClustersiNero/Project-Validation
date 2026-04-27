from collections.abc import Callable

from validation.config.simulation_config import (
    ConfigSource,
    SimulationConfig,
    load_simulation_config,
    validate_simulation_config,
)
from validation.engine.engine import run_engine
from validation.engine.rng import RNG
from validation.engine.types import SimulationExecution


def run_simulation(
    config: ConfigSource,
    progress_callback: Callable[[int, int], None] | None = None,
) -> tuple[SimulationConfig, SimulationExecution]:
    normalized_config = load_simulation_config(config)
    validate_simulation_config(normalized_config)
    rng = RNG(seed=normalized_config.seed)
    execution = run_engine(normalized_config, rng, progress_callback=progress_callback)
    return normalized_config, execution
