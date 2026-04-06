from __future__ import annotations

from slot_validation.validation.schema import CheckResult


def range_check(metric: str, observed: float, expected_range: tuple[float, float]) -> CheckResult:
	low, high = expected_range
	verdict = "pass" if low <= observed <= high else "fail"
	return CheckResult(
		metric=metric,
		observed=observed,
		expected=None,
		range=expected_range,
		ci=None,
		deviation=None,
		verdict=verdict,
		notes="range_check",
	)
