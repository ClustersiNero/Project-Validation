from __future__ import annotations

from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig
from slot_validation.engine.rng import DeterministicRNG


@dataclass(frozen=True)
class PayoutBreakdown:
	regular_win: float
	scatter_win: float
	round_multiplier_sum: int
	total_win: float
	symbol_counts: dict[int, int]


def _count_symbols(board_rows: tuple[tuple[int, ...], ...]) -> dict[int, int]:
	counts: dict[int, int] = {}
	for row in board_rows:
		for symbol_id in row:
			counts[symbol_id] = counts.get(symbol_id, 0) + 1
	return counts


def _best_payout_for_count(payouts: dict[int, float], count: int) -> float:
	best = 0.0
	for threshold, amount in payouts.items():
		if count >= threshold and amount > best:
			best = amount
	return best


def evaluate_board_payout(
	board_rows: tuple[tuple[int, ...], ...],
	config: GameConfig,
	stake: float,
	multiplier_profile_id: int,
	rng: DeterministicRNG,
) -> PayoutBreakdown:
	counts = _count_symbols(board_rows)

	regular_win = 0.0
	scatter_win = 0.0

	for symbol_id, symbol in config.symbols.items():
		count = counts.get(symbol_id, 0)
		if count <= 0:
			continue

		base_amount = _best_payout_for_count(symbol.payouts, count)
		if base_amount <= 0:
			continue

		if symbol.symbol_type == "regular":
			regular_win += base_amount * stake
		elif symbol.symbol_type == "scatter":
			scatter_win += base_amount * stake

	multiplier_symbol_count = counts.get(config.multiplier_symbol_id, 0)
	round_multiplier_sum = 0
	if multiplier_symbol_count > 0:
		profile = config.multiplier_profiles[multiplier_profile_id]
		values = config.multiplier_values
		for _ in range(multiplier_symbol_count):
			chosen = rng.choice_from_population(values, profile.weights)
			round_multiplier_sum += chosen

	subtotal = regular_win + scatter_win
	if subtotal > 0 and round_multiplier_sum > 0:
		total = subtotal * float(round_multiplier_sum)
	else:
		total = subtotal

	return PayoutBreakdown(
		regular_win=regular_win,
		scatter_win=scatter_win,
		round_multiplier_sum=round_multiplier_sum,
		total_win=total,
		symbol_counts=counts,
	)
