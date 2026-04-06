from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationMeta:
	run_id: str
	config_id: str
	validation_version: str
	timestamp: str


@dataclass(frozen=True)
class CheckResult:
	metric: str
	observed: float
	expected: float | None
	range: tuple[float, float] | None
	ci: tuple[float, float] | None
	deviation: float | None
	verdict: str
	notes: str


@dataclass(frozen=True)
class ValidationSummary:
	total_checks: int
	pass_count: int
	fail_count: int
	warn_count: int
	overall_verdict: str


@dataclass(frozen=True)
class ValidationReport:
	meta: ValidationMeta
	checks: tuple[CheckResult, ...]
	summary: ValidationSummary
