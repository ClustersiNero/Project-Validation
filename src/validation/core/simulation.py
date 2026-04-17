from validation.core.types import CanonicalResult
from validation.engine.minimal_engine import build_minimal_canonical_result


def run_simulation(config) -> CanonicalResult:
    return build_minimal_canonical_result(config)
