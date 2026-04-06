from __future__ import annotations

from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig
from slot_validation.engine.board import clear_gravity_refill, generate_board
from slot_validation.engine.payout import evaluate_regular_wins, finalize_round_payout
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
	wager_amount: float,
	rng: DeterministicRNG,
) -> EngineWagerRecord:
	definition = config.definition
	is_free_active = state_name == definition.free_state_name
	remaining_free_rounds = 1 if is_free_active else 0
	global_multiplier = 0.0
	if is_free_active and not definition.free_game_global_multiplier_starts_at_zero:
		global_multiplier = 1.0

	rounds: list[EngineRoundRecord] = []
	wager_trigger_flags: set[str] = set()
	wager_total_win = 0.0
	round_id = 1

	def evaluate_single_round(current_state_name: str, free_remaining_before: int) -> tuple[EngineRoundRecord, int, float, tuple[str, ...]]:
		nonlocal global_multiplier
		board_out = generate_board(
			config=config,
			mode_id=mode_id,
			state_name=current_state_name,
			rng=rng,
		)
		board = board_out.board
		rolls: list[EngineRollRecord] = []
		roll_id = 1
		accumulated_round_win = 0.0

		start_state = EngineGameState(
			board=board,
			pending_round_multiplier=None,
			feature_is_active=current_state_name == definition.free_state_name,
			feature_remaining_rounds=free_remaining_before,
			feature_awarded_rounds=0,
		)
		rolls.append(
			EngineRollRecord(
				roll_id=roll_id,
				state_type="round_start",
				pre_state=start_state,
				post_state=start_state,
				roll_win=0.0,
				accumulated_round_win=0.0,
				events=(),
				reel_set_id=None,
				multiplier_profile_id=None,
			)
		)
		roll_id += 1

		is_first_roll = True
		regular_chain_win = 0.0
		while True:
			pre_state = EngineGameState(
				board=board,
				pending_round_multiplier=None,
				feature_is_active=current_state_name == definition.free_state_name,
				feature_remaining_rounds=free_remaining_before,
				feature_awarded_rounds=0,
			)
			regular_eval = evaluate_regular_wins(
				board=board,
				config=config,
				wager_amount=wager_amount,
			)
			regular_chain_win += regular_eval.regular_win
			accumulated_round_win = regular_chain_win

			if regular_eval.winning_positions:
				next_board = clear_gravity_refill(
					board=board,
					winning_positions=regular_eval.winning_positions,
					config=config,
					strip_set_id=board_out.strip_set_id,
					column_strip_ids=board_out.column_strip_ids,
					rng=rng,
				)
				state_type = "initial_roll" if is_first_roll else "cascade_roll"
				post_state = EngineGameState(
					board=next_board,
					pending_round_multiplier=None,
					feature_is_active=current_state_name == definition.free_state_name,
					feature_remaining_rounds=free_remaining_before,
					feature_awarded_rounds=0,
				)
				rolls.append(
					EngineRollRecord(
						roll_id=roll_id,
						state_type=state_type,
						pre_state=pre_state,
						post_state=post_state,
						roll_win=regular_eval.regular_win,
						accumulated_round_win=accumulated_round_win,
						events=("regular_win",),
						reel_set_id=board_out.strip_set_id,
						multiplier_profile_id=board_out.multiplier_profile_id,
					)
				)
				roll_id += 1
				board = next_board
				is_first_roll = False
				continue

			# No more regular wins, finalize round using final board.
			finalized = finalize_round_payout(
				board=board,
				config=config,
				state_name=current_state_name,
				wager_amount=wager_amount,
				regular_chain_win=regular_chain_win,
				stored_global_multiplier=global_multiplier,
				multiplier_profile_id=board_out.multiplier_profile_id,
				rng=rng,
			)
			global_multiplier = finalized.updated_global_multiplier
			if current_state_name == definition.free_state_name:
				post_feature_remaining_rounds = max(0, free_remaining_before - 1 + finalized.bonus_rounds_awarded)
			else:
				post_feature_remaining_rounds = max(0, finalized.bonus_rounds_awarded)
			rolls.append(
				EngineRollRecord(
					roll_id=roll_id,
					state_type="round_end",
					pre_state=pre_state,
					post_state=EngineGameState(
						board=board,
						pending_round_multiplier=finalized.round_multiplier_total if finalized.round_multiplier_total > 0 else None,
						feature_is_active=current_state_name == definition.free_state_name,
						feature_remaining_rounds=post_feature_remaining_rounds,
						feature_awarded_rounds=finalized.bonus_rounds_awarded,
					),
					roll_win=max(0.0, finalized.total_win - accumulated_round_win),
					accumulated_round_win=finalized.total_win,
					events=finalized.trigger_flags,
					reel_set_id=board_out.strip_set_id,
					multiplier_profile_id=board_out.multiplier_profile_id,
				)
			)
			return (
				EngineRoundRecord(
					round_id=round_id,
					round_type="base" if current_state_name == definition.base_state_name else "feature",
					round_win=finalized.total_win,
					rolls=tuple(rolls),
					round_multiplier_total=finalized.round_multiplier_total if finalized.round_multiplier_total > 0 else None,
				),
				finalized.bonus_rounds_awarded,
				finalized.total_win,
				finalized.trigger_flags,
			)

	# Base round (always one when starting from basic mode).
	if not is_free_active:
		round_record, awarded_rounds, round_win, round_flags = evaluate_single_round(
			definition.base_state_name,
			free_remaining_before=0,
		)
		rounds.append(round_record)
		round_id += 1
		wager_total_win += round_win
		wager_trigger_flags.update(round_flags)
		remaining_free_rounds += awarded_rounds

	# Free-game rounds sequence, including retriggers.
	while remaining_free_rounds > 0:
		round_record, awarded_rounds, round_win, round_flags = evaluate_single_round(
			definition.free_state_name,
			free_remaining_before=remaining_free_rounds,
		)
		rounds.append(round_record)
		round_id += 1
		wager_total_win += round_win
		wager_trigger_flags.update(round_flags)
		remaining_free_rounds -= 1
		remaining_free_rounds += awarded_rounds

	if is_free_active and not rounds:
		# Starting directly in free mode should still execute one free round.
		round_record, awarded_rounds, round_win, round_flags = evaluate_single_round(
			definition.free_state_name,
			free_remaining_before=1,
		)
		rounds.append(round_record)
		wager_total_win += round_win
		wager_trigger_flags.update(round_flags)

	last_board = rounds[-1].rolls[-1].post_state.board if rounds else _empty_state(config.definition.board_rows, config.definition.board_cols).board
	final_state = EngineGameState(
		board=last_board,
		pending_round_multiplier=rounds[-1].round_multiplier_total if rounds else None,
		feature_is_active=False,
		feature_remaining_rounds=0,
		feature_awarded_rounds=0,
	)

	return EngineWagerRecord(
		wager_id=wager_id,
		bet=float(wager_amount),
		total_win=float(wager_total_win),
		trigger_flags=tuple(sorted(wager_trigger_flags)),
		mode=config.wager_modes[mode_id].mode_name,
		rounds=tuple(rounds),
		final_state=final_state,
	)
