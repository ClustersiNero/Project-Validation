from __future__ import annotations

from slot_validation.canonical.schema import (
	CanonicalResult,
	FeatureState,
	GameState,
	RollRecord,
	RoundRecord,
	RunMeta,
	RunSummary,
	WagerRecord,
)
from slot_validation.config.game_config import GameConfig
from slot_validation.engine.runner import EngineRunResult
from slot_validation.utils.ids import build_run_id
from slot_validation.utils.time import utc_now_iso


CANONICAL_SCHEMA_VERSION = "1.0.0"


def _to_game_state(raw_state) -> GameState:
	feature_state = FeatureState(
		feature_type="free",
		remaining_rounds=raw_state.feature_remaining_rounds,
		awarded_rounds=raw_state.feature_awarded_rounds,
		is_active=raw_state.feature_is_active,
	) if raw_state.feature_is_active or raw_state.feature_awarded_rounds > 0 else None

	return GameState(
		board=raw_state.board,
		pending_round_multiplier=raw_state.pending_round_multiplier,
		feature_state=feature_state,
	)


def build_canonical_result(engine_result: EngineRunResult, config: GameConfig) -> CanonicalResult:
	wagers: list[WagerRecord] = []

	for wager in engine_result.wagers:
		rounds: list[RoundRecord] = []
		for round_rec in wager.rounds:
			rolls = tuple(
				RollRecord(
					roll_id=roll.roll_id,
					state_type=roll.state_type,
					pre_state=_to_game_state(roll.pre_state),
					post_state=_to_game_state(roll.post_state),
					roll_win=roll.roll_win,
					accumulated_round_win=roll.accumulated_round_win,
					events=roll.events,
					reel_set_id=str(roll.reel_set_id) if roll.reel_set_id is not None else None,
					multiplier_profile_id=str(roll.multiplier_profile_id) if roll.multiplier_profile_id is not None else None,
				)
				for roll in round_rec.rolls
			)

			rounds.append(
				RoundRecord(
					round_id=round_rec.round_id,
					round_type=round_rec.round_type,
					round_win=round_rec.round_win,
					roll_count=len(rolls),
					rolls=rolls,
					round_multiplier_total=round_rec.round_multiplier_total,
				)
			)

		wagers.append(
			WagerRecord(
				wager_id=wager.wager_id,
				bet=wager.bet,
				total_win=wager.total_win,
				is_hit=wager.total_win > 0,
				trigger_flags=wager.trigger_flags,
				mode=wager.mode,
				round_count=len(rounds),
				rounds=tuple(rounds),
				final_state=_to_game_state(wager.final_state),
			)
		)

	run_meta = RunMeta(
		run_id=build_run_id(engine_result.config_id, engine_result.seed, engine_result.total_wagers),
		config_id=engine_result.config_id,
		config_version=config.config_version,
		engine_version=engine_result.engine_version,
		schema_version=CANONICAL_SCHEMA_VERSION,
		mode=engine_result.mode_name,
		seed=engine_result.seed,
		stake_amount=engine_result.stake_amount,
		total_wagers=engine_result.total_wagers,
		timestamp=utc_now_iso(),
	)

	result = CanonicalResult(
		run=run_meta,
		wagers=tuple(wagers),
		summary=RunSummary(
			total_bet=engine_result.total_bet,
			total_win=engine_result.total_win,
			wager_count=len(wagers),
		),
	)
	_validate_canonical_invariants(result)
	return result


def _validate_canonical_invariants(result: CanonicalResult) -> None:
	if result.run.total_wagers != len(result.wagers):
		raise ValueError("run.total_wagers must equal len(wagers)")

	recomputed_total_win = 0.0
	for wager in result.wagers:
		round_win_sum = sum(r.round_win for r in wager.rounds)
		if abs(round_win_sum - wager.total_win) > 1e-9:
			raise ValueError("wager.total_win must equal sum(round.round_win)")
		recomputed_total_win += wager.total_win

		for round_rec in wager.rounds:
			if round_rec.roll_count != len(round_rec.rolls):
				raise ValueError("round.roll_count must equal len(round.rolls)")
			expected_roll_id = 1
			last_acc = -1.0
			for roll in round_rec.rolls:
				if roll.roll_id != expected_roll_id:
					raise ValueError("roll_id must be continuous and ordered")
				if roll.accumulated_round_win < last_acc:
					raise ValueError("accumulated_round_win must be monotonic")
				expected_roll_id += 1
				last_acc = roll.accumulated_round_win

	if abs(recomputed_total_win - result.summary.total_win) > 1e-9:
		raise ValueError("summary.total_win must be recomputable from wagers")
