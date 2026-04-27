from collections.abc import Callable

from validation.canonical.recording import record_canonical_result
from validation.core.simulation import run_simulation
from validation.core.metrics import compute_metrics
from validation.core.validation import validate_canonical, validate_metrics, validate_statistics
from validation.core.types import PipelineResult, ValidationRules


def run_pipeline(
    config,
    validation_rules: ValidationRules | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    post_progress_callback: Callable[[int, int, str], None] | None = None,
) -> PipelineResult:
    normalized_config, execution = run_simulation(config, progress_callback=progress_callback)
    total_post_steps = 5 if validation_rules is not None else 4

    _report_post_progress(post_progress_callback, 0, total_post_steps, "recording canonical")
    canonical_result = record_canonical_result(normalized_config, execution)
    _report_post_progress(post_progress_callback, 1, total_post_steps, "validating canonical")
    canonical_validation = validate_canonical(canonical_result)
    _report_post_progress(post_progress_callback, 2, total_post_steps, "computing metrics")
    metrics_bundle = compute_metrics(canonical_result)
    _report_post_progress(post_progress_callback, 3, total_post_steps, "validating metrics")
    metrics_validation = validate_metrics(metrics_bundle)
    statistical_validation = (
        _run_statistical_validation(
            metrics_bundle,
            validation_rules,
            post_progress_callback,
            total_post_steps,
        )
        if validation_rules is not None
        else None
    )
    _report_post_progress(post_progress_callback, total_post_steps, total_post_steps, "complete")
    return PipelineResult(
        canonical_result=canonical_result,
        metrics_bundle=metrics_bundle,
        canonical_validation=canonical_validation,
        metrics_validation=metrics_validation,
        statistical_validation=statistical_validation,
    )


def _run_statistical_validation(
    metrics_bundle,
    validation_rules: ValidationRules,
    post_progress_callback: Callable[[int, int, str], None] | None,
    total_post_steps: int,
):
    _report_post_progress(
        post_progress_callback,
        total_post_steps - 1,
        total_post_steps,
        "statistical validation",
    )
    return validate_statistics(metrics_bundle, validation_rules)


def _report_post_progress(
    callback: Callable[[int, int, str], None] | None,
    completed: int,
    total: int,
    detail: str,
) -> None:
    if callback is not None:
        callback(completed, total, detail)
