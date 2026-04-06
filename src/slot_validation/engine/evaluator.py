from __future__ import annotations

from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig
from slot_validation.engine.board import generate_round_board
from slot_validation.engine.payout import evaluate_board_payout
from slot_validation.engine.rng import DeterministicRNG


@dataclass(frozen=True)
class EvaluatedSpin:
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


def evaluate_single_spin(
	*,
	spin_index: int,
	mode_id: int,
	state_name: str,
	stake: float,
	config: GameConfig,
	rng: DeterministicRNG,
) -> EvaluatedSpin:
	board_rows, meta = generate_round_board(
		config=config,
		mode_id=mode_id,
		state_name=state_name,
		rng=rng,
	)

	payout = evaluate_board_payout(
		board_rows=board_rows,
		config=config,
		stake=stake,
		multiplier_profile_id=meta.multiplier_profile_id,
		rng=rng,
	)

	return EvaluatedSpin(
		spin_index=spin_index,
		state_name=state_name,
		board_rows=board_rows,
		strip_set_id=meta.strip_set_id,
		multiplier_profile_id=meta.multiplier_profile_id,
		regular_win=payout.regular_win,
		scatter_win=payout.scatter_win,
		round_multiplier_sum=payout.round_multiplier_sum,
		total_win=payout.total_win,
		symbol_counts=payout.symbol_counts,
	)
