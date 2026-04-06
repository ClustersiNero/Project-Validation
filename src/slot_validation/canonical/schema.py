from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureState:
	feature_type: str
	remaining_rounds: int
	awarded_rounds: int
	is_active: bool


@dataclass(frozen=True)
class GameState:
	board: tuple[tuple[int, ...], ...]
	pending_round_multiplier: float | None
	feature_state: FeatureState | None


@dataclass(frozen=True)
class RollRecord:
	roll_id: int
	state_type: str
	pre_state: GameState
	post_state: GameState
	roll_win: float
	accumulated_round_win: float
	events: tuple[str, ...]
	reel_set_id: str | None
	multiplier_profile_id: str | None


@dataclass(frozen=True)
class RoundRecord:
	round_id: int
	round_type: str
	round_win: float
	roll_count: int
	rolls: tuple[RollRecord, ...]
	round_multiplier_total: float | None


@dataclass(frozen=True)
class WagerRecord:
	wager_id: int
	bet: float
	total_win: float
	is_hit: bool
	trigger_flags: tuple[str, ...]
	mode: str
	round_count: int
	rounds: tuple[RoundRecord, ...]
	final_state: GameState


@dataclass(frozen=True)
class RunMeta:
	run_id: str
	config_id: str
	config_version: str
	engine_version: str
	schema_version: str
	mode: str
	seed: int
	stake_amount: float
	total_wagers: int
	timestamp: str


@dataclass(frozen=True)
class RunSummary:
	total_bet: float
	total_win: float
	wager_count: int


@dataclass(frozen=True)
class CanonicalResult:
	run: RunMeta
	wagers: tuple[WagerRecord, ...]
	summary: RunSummary
