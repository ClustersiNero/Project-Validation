from dataclasses import dataclass

from validation.canonical.schema import CanonicalResult
from validation.metrics.types import MetricsBundle
from validation.validation.types import (
    MetricRule,
    StatisticalCheckResult,
    StatisticalValidationReport,
    ValidationReport,
    ValidationRules,
)


@dataclass
class PipelineResult:
    canonical_result: CanonicalResult
    metrics_bundle: MetricsBundle
    canonical_validation: ValidationReport
    metrics_validation: ValidationReport
    statistical_validation: StatisticalValidationReport | None = None


__all__ = [
    "MetricRule",
    "PipelineResult",
    "StatisticalCheckResult",
    "StatisticalValidationReport",
    "ValidationReport",
    "ValidationRules",
]
