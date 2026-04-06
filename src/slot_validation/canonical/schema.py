from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalSpinResult:
	spin_index: int
	state_name: str
	board_rows: tuple[tuple[int, ...], ...]
	strip_set_id: int
	multiplier_profile_id: int
	regular_win: float
	scatter_win: float
	round_multiplier_sum: int
	total_win: float
	symbol_counts: dict[int, int]


@dataclass(frozen=True)
class CanonicalResult:
	run_id: str
	game_id: str
	config_version: str
	timestamp_utc: str

	seed: int
	wager_mode_id: int
	state_name: str
	stake: float
	spins: int

	total_bet: float
	total_win: float
	spin_results: tuple[CanonicalSpinResult, ...]
