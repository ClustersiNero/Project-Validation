from validation.config.minimal_config import MinimalConfigSource, load_minimal_config, validate_minimal_config
from validation.core.types import CanonicalResult
from validation.engine.minimal_engine import build_minimal_canonical_result


def run_simulation(config: MinimalConfigSource) -> CanonicalResult:
    normalized_config = load_minimal_config(config)
    validate_minimal_config(normalized_config)
    return build_minimal_canonical_result(normalized_config)
