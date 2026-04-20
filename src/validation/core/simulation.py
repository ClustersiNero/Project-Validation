from validation.config.simulation_config import ConfigSource, load_simulation_config, validate_simulation_config
from validation.canonical.schema import CanonicalResult
from validation.canonical.recording import record_canonical_result
from validation.engine.engine import run_engine
from validation.engine.rng import RNG


def run_simulation(config: ConfigSource) -> CanonicalResult:
    normalized_config = load_simulation_config(config)
    validate_simulation_config(normalized_config)
    rng = RNG(seed=normalized_config.seed)
    execution = run_engine(normalized_config, rng)
    return record_canonical_result(normalized_config, execution)
