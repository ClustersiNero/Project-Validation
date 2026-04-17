from validation.core.types import CanonicalResult, MetricsBundle, ValidationReport
from validation.validation.minimal_validation import validate_canonical_impl, validate_metrics_impl


def validate_canonical(result: CanonicalResult) -> ValidationReport:
    return validate_canonical_impl(result)


def validate_metrics(metrics: MetricsBundle) -> ValidationReport:
    return validate_metrics_impl(metrics)

