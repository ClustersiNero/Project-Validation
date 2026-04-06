from __future__ import annotations

from slot_validation.metrics.schema import MetricsBundle
from slot_validation.validation.checks import validate_metric_range
from slot_validation.validation.schema import ValidationCheck, ValidationReport


def build_validation_report(
	metrics: MetricsBundle,
	baseline_ranges: dict[str, tuple[float, float]],
) -> ValidationReport:
	checks: list[ValidationCheck] = []

	metric_map = {
		"empirical_rtp": metrics.empirical_rtp,
		"hit_frequency": metrics.hit_frequency,
		"avg_win_per_spin": metrics.avg_win_per_spin,
		"top_1pct_payout_share": metrics.top_1pct_payout_share,
	}

	for metric_name, observed in metric_map.items():
		if metric_name not in baseline_ranges:
			continue
		low, high = baseline_ranges[metric_name]
		checks.append(
			validate_metric_range(
				metric_name=metric_name,
				observed=float(observed),
				lower_bound=float(low),
				upper_bound=float(high),
				note="baseline_range_check",
			)
		)

	passed = all(c.passed for c in checks) if checks else True
	return ValidationReport(passed=passed, checks=tuple(checks))
