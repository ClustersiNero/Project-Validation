from dataclasses import dataclass

from validation.canonical.schema import CanonicalResult
from validation.metrics.metrics import MetricsBundle
from validation.validation.validation import ValidationReport


@dataclass
class PipelineResult:
    canonical_result: CanonicalResult
    metrics_bundle: MetricsBundle
    canonical_validation: ValidationReport
    metrics_validation: ValidationReport
