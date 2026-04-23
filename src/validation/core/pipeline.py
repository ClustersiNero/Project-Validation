from validation.core.simulation import run_simulation
from validation.core.metrics import compute_metrics
from validation.core.validation import validate_canonical, validate_metrics, validate_statistics
from validation.core.types import PipelineResult, ValidationRules


def run_pipeline(config, validation_rules: ValidationRules | None = None) -> PipelineResult:
    canonical_result = run_simulation(config)
    canonical_validation = validate_canonical(canonical_result)
    metrics_bundle = compute_metrics(canonical_result)
    metrics_validation = validate_metrics(metrics_bundle)
    statistical_validation = (
        validate_statistics(metrics_bundle, validation_rules)
        if validation_rules is not None
        else None
    )
    return PipelineResult(
        canonical_result=canonical_result,
        metrics_bundle=metrics_bundle,
        canonical_validation=canonical_validation,
        metrics_validation=metrics_validation,
        statistical_validation=statistical_validation,
    )
