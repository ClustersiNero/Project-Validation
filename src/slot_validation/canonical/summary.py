from __future__ import annotations

from slot_validation.canonical.schema import CanonicalResult


def summarize_canonical(result: CanonicalResult) -> dict[str, float | int | str]:
	return {
		"run_id": result.run.run_id,
		"config_id": result.run.config_id,
		"mode": result.run.mode,
		"seed": result.run.seed,
		"total_wagers": result.run.total_wagers,
		"total_bet": result.summary.total_bet,
		"total_win": result.summary.total_win,
	}
