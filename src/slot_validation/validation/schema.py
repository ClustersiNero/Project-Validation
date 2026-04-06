from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationCheck:
	metric_name: str
	observed: float
	lower_bound: float
	upper_bound: float
	passed: bool
	note: str


@dataclass(frozen=True)
class ValidationReport:
	passed: bool
	checks: tuple[ValidationCheck, ...]
