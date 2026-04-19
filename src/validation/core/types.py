from dataclasses import dataclass

from validation.canonical.minimal_canonical import CanonicalResult
from validation.metrics.minimal_metrics import MetricsBundle
from validation.validation.minimal_validation import ValidationReport


@dataclass
class PipelineResult:
    canonical_result: CanonicalResult
    metrics_bundle: MetricsBundle
    canonical_validation: ValidationReport
    metrics_validation: ValidationReport
