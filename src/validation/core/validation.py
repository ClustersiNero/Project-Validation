from validation.canonical.schema import CanonicalResult
from validation.metrics.types import MetricsBundle
from validation.validation.canonical_validation import validate_canonical_impl
from validation.validation.metrics_validation import validate_metrics_impl
from validation.validation.statistical_validation import validate_statistics_impl
from validation.validation.types import StatisticalValidationReport, ValidationReport, ValidationRules


def validate_canonical(result: CanonicalResult) -> ValidationReport:
    return validate_canonical_impl(result)


def validate_metrics(metrics: MetricsBundle) -> ValidationReport:
    return validate_metrics_impl(metrics)


def validate_statistics(
    metrics: MetricsBundle,
    validation_rules: ValidationRules,
) -> StatisticalValidationReport:
    return validate_statistics_impl(metrics, validation_rules)

