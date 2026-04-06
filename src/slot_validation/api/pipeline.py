from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from slot_validation.api.metrics import compute_metrics
from slot_validation.api.simulation import run_simulation
from slot_validation.api.validation import validate_metrics
from slot_validation.canonical.schema import CanonicalResult
from slot_validation.metrics.schema import MetricsBundle
from slot_validation.validation.schema import ValidationReport


@dataclass(frozen=True)
class PipelineResult:
	canonical_result: CanonicalResult
	metrics_bundle: MetricsBundle
	validation_report: ValidationReport


def run_validation_pipeline(
	*,
	seed: int,
	spins: int,
	baseline: dict[str, tuple[float, float]],
	wager_mode_id: int = 1,
	stake: float = 1.0,
	state_name: str = "basic",
	config_module: Any | None = None,
) -> PipelineResult:
	canonical = run_simulation(
		seed=seed,
		spins=spins,
		wager_mode_id=wager_mode_id,
		stake=stake,
		state_name=state_name,
		config_module=config_module,
	)
	metrics = compute_metrics(canonical)
	report = validate_metrics(metrics, baseline=baseline)

	return PipelineResult(
		canonical_result=canonical,
		metrics_bundle=metrics,
		validation_report=report,
	)
