from validation.canonical.schema import CanonicalResult
from validation.metrics.types import MetricsBundle
from validation.validation.validation import ValidationReport
from validation.validation.validation import validate_canonical_impl, validate_metrics_impl


def validate_canonical(result: CanonicalResult) -> ValidationReport:
    return validate_canonical_impl(result)


def validate_metrics(metrics: MetricsBundle) -> ValidationReport:
    return validate_metrics_impl(metrics)

