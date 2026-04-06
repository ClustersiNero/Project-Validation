from __future__ import annotations

from slot_validation.canonical.schema import CanonicalResult


def summarize_canonical(result: CanonicalResult) -> dict[str, float | int | str]:
	return {
		"run_id": result.run_id,
		"game_id": result.game_id,
		"seed": result.seed,
		"mode": result.wager_mode_id,
		"spins": result.spins,
		"total_bet": result.total_bet,
		"total_win": result.total_win,
	}
