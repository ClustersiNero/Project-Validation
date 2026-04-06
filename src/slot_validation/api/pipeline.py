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
class PipelineArtifact:
	canonical_result: CanonicalResult
	metrics_bundle: MetricsBundle
	validation_report: ValidationReport
	run_metadata: dict[str, Any]
	optional_export_refs: tuple[str, ...] = ()


def run_pipeline(
	*,
	seed: int,
	total_wagers: int,
	baseline: dict[str, tuple[float, float]],
	mode_id: int = 1,
	stake_amount: float = 1.0,
	state_name: str = "basic",
	config_id: str = "configs.game.olympus_mini",
	config_module: Any | None = None,
) -> PipelineArtifact:
	canonical_result = run_simulation(
		seed=seed,
		total_wagers=total_wagers,
		mode_id=mode_id,
		stake_amount=stake_amount,
		state_name=state_name,
		config_id=config_id,
		config_module=config_module,
	)
	metrics_bundle = compute_metrics(canonical_result)
	validation_report = validate_metrics(metrics_bundle, baseline=baseline)

	run_metadata = {
		"run_id": canonical_result.run.run_id,
		"config_id": canonical_result.run.config_id,
		"engine_version": canonical_result.run.engine_version,
		"schema_version": canonical_result.run.schema_version,
		"seed": canonical_result.run.seed,
		"mode": canonical_result.run.mode,
		"stake_amount": canonical_result.run.stake_amount,
		"total_wagers": canonical_result.run.total_wagers,
		"timestamp": canonical_result.run.timestamp,
	}

	return PipelineArtifact(
		canonical_result=canonical_result,
		metrics_bundle=metrics_bundle,
		validation_report=validation_report,
		run_metadata=run_metadata,
		optional_export_refs=(),
	)
