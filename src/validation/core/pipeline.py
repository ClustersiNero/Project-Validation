from validation.core.simulation import run_simulation
from validation.core.metrics import compute_metrics
from validation.core.validation import validate_canonical, validate_metrics
from validation.core.types import PipelineResult


def run_pipeline(config) -> PipelineResult:
    canonical_result = run_simulation(config)
    canonical_validation = validate_canonical(canonical_result)
    metrics_bundle = compute_metrics(canonical_result)
    metrics_validation = validate_metrics(metrics_bundle)
    return PipelineResult(
        canonical_result=canonical_result,
        metrics_bundle=metrics_bundle,
        canonical_validation=canonical_validation,
        metrics_validation=metrics_validation,
    )
