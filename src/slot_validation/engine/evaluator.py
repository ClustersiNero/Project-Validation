from __future__ import annotations

from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig
from slot_validation.engine.board import generate_board
from slot_validation.engine.payout import evaluate_payout
from slot_validation.engine.rng import DeterministicRNG


@dataclass(frozen=True)
class EngineGameState:
	board: tuple[tuple[int, ...], ...]
	pending_round_multiplier: float | None
	feature_is_active: bool
	feature_remaining_rounds: int
	feature_awarded_rounds: int


@dataclass(frozen=True)
class EngineRollRecord:
	roll_id: int
	state_type: str
	pre_state: EngineGameState
	post_state: EngineGameState
	roll_win: float
	accumulated_round_win: float
	events: tuple[str, ...]
	reel_set_id: int | None
	multiplier_profile_id: int | None


@dataclass(frozen=True)
class EngineRoundRecord:
	round_id: int
	round_type: str
	round_win: float
	rolls: tuple[EngineRollRecord, ...]
	round_multiplier_total: float | None


@dataclass(frozen=True)
class EngineWagerRecord:
	wager_id: int
	bet: float
	total_win: float
	trigger_flags: tuple[str, ...]
	mode: str
	rounds: tuple[EngineRoundRecord, ...]
	final_state: EngineGameState


def _empty_state(rows: int, cols: int) -> EngineGameState:
	board = tuple(tuple(0 for _ in range(cols)) for _ in range(rows))
	return EngineGameState(
		board=board,
		pending_round_multiplier=None,
		feature_is_active=False,
		feature_remaining_rounds=0,
		feature_awarded_rounds=0,
	)


def evaluate_wager(
	*,
	wager_id: int,
	config: GameConfig,
	mode_id: int,
	state_name: str,
	stake: float,
	rng: DeterministicRNG,
) -> EngineWagerRecord:
	pre_state = _empty_state(config.definition.board_rows, config.definition.board_cols)
	board_out = generate_board(config=config, mode_id=mode_id, state_name=state_name, rng=rng)
	payout = evaluate_payout(
		board=board_out.board,
		config=config,
		stake=stake,
		multiplier_profile_id=board_out.multiplier_profile_id,
		rng=rng,
	)

	post_state = EngineGameState(
		board=board_out.board,
		pending_round_multiplier=payout.round_multiplier_total,
		feature_is_active=False,
		feature_remaining_rounds=0,
		feature_awarded_rounds=0,
	)

	rolls = (
		EngineRollRecord(
			roll_id=1,
			state_type="round_start",
			pre_state=pre_state,
			post_state=pre_state,
			roll_win=0.0,
			accumulated_round_win=0.0,
			events=(),
			reel_set_id=None,
			multiplier_profile_id=None,
		),
		EngineRollRecord(
			roll_id=2,
			state_type="initial_roll",
			pre_state=pre_state,
			post_state=post_state,
			roll_win=float(payout.total_win),
			accumulated_round_win=float(payout.total_win),
			events=payout.trigger_flags,
			reel_set_id=board_out.strip_set_id,
			multiplier_profile_id=board_out.multiplier_profile_id,
		),
		EngineRollRecord(
			roll_id=3,
			state_type="round_end",
			pre_state=post_state,
			post_state=post_state,
			roll_win=0.0,
			accumulated_round_win=float(payout.total_win),
			events=(),
			reel_set_id=None,
			multiplier_profile_id=None,
		),
	)

	round_record = EngineRoundRecord(
		round_id=1,
		round_type="base" if state_name == config.definition.base_state_name else "feature",
		round_win=float(payout.total_win),
		rolls=rolls,
		round_multiplier_total=payout.round_multiplier_total,
	)

	return EngineWagerRecord(
		wager_id=wager_id,
		bet=float(stake),
		total_win=float(payout.total_win),
		trigger_flags=payout.trigger_flags,
		mode=config.wager_modes[mode_id].mode_name,
		rounds=(round_record,),
		final_state=post_state,
	)
