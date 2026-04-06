from __future__ import annotations

from slot_validation.metrics.schema import MetricsBundle
from slot_validation.utils.time import utc_now_iso
from slot_validation.validation.checks import range_check
from slot_validation.validation.schema import CheckResult, ValidationMeta, ValidationReport, ValidationSummary


def build_validation_report(
	*,
	metrics: MetricsBundle,
	baseline_ranges: dict[str, tuple[float, float]],
) -> ValidationReport:
	checks: list[CheckResult] = []

	metric_map = {
		"core.empirical_rtp": metrics.core.empirical_rtp,
		"core.hit_frequency": metrics.core.hit_frequency,
		"core.avg_win": metrics.core.avg_win,
		"tail.top_1pct_win_share": metrics.tail.top_1pct_win_share,
	}

	for metric_name, expected_range in baseline_ranges.items():
		if metric_name not in metric_map:
			continue
		checks.append(range_check(metric_name, float(metric_map[metric_name]), expected_range))

	pass_count = sum(1 for c in checks if c.verdict == "pass")
	fail_count = sum(1 for c in checks if c.verdict == "fail")
	warn_count = 0
	overall = "fail" if fail_count > 0 else "pass"

	return ValidationReport(
		meta=ValidationMeta(
			run_id=metrics.meta.run_id,
			config_id=metrics.meta.config_id,
			validation_version="0.1.0",
			timestamp=utc_now_iso(),
		),
		checks=tuple(checks),
		summary=ValidationSummary(
			total_checks=len(checks),
			pass_count=pass_count,
			fail_count=fail_count,
			warn_count=warn_count,
			overall_verdict=overall,
		),
	)
