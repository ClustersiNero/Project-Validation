from validation.config.minimal_config import MinimalConfigSource, load_minimal_config, validate_minimal_config
from validation.core.types import CanonicalResult
from validation.engine.minimal_engine import build_minimal_canonical_result
from validation.engine.rng import RNG


def run_simulation(config: MinimalConfigSource) -> CanonicalResult:
    normalized_config = load_minimal_config(config)
    validate_minimal_config(normalized_config)
    rng = RNG(seed=normalized_config.seed)
    return build_minimal_canonical_result(normalized_config, rng)
