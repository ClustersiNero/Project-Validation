from __future__ import annotations

from slot_validation.validation.schema import ValidationCheck


def validate_metric_range(
	*,
	metric_name: str,
	observed: float,
	lower_bound: float,
	upper_bound: float,
	note: str = "",
) -> ValidationCheck:
	passed = lower_bound <= observed <= upper_bound
	return ValidationCheck(
		metric_name=metric_name,
		observed=observed,
		lower_bound=lower_bound,
		upper_bound=upper_bound,
		passed=passed,
		note=note,
	)
