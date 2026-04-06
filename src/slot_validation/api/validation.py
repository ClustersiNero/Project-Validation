from __future__ import annotations

from slot_validation.metrics.schema import MetricsBundle
from slot_validation.validation.report import build_validation_report
from slot_validation.validation.schema import ValidationReport


def validate_metrics(
	metrics: MetricsBundle,
	baseline: dict[str, tuple[float, float]],
) -> ValidationReport:
	return build_validation_report(metrics=metrics, baseline_ranges=baseline)
