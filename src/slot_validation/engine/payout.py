from __future__ import annotations

from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig
from slot_validation.engine.rng import DeterministicRNG


@dataclass(frozen=True)
class PayoutResult:
	regular_win: float
	scatter_win: float
	round_multiplier_total: float | None
	total_win: float
	symbol_counts: dict[int, int]
	trigger_flags: tuple[str, ...]


def _count_symbols(board: tuple[tuple[int, ...], ...]) -> dict[int, int]:
	counts: dict[int, int] = {}
	for row in board:
		for symbol_id in row:
			counts[symbol_id] = counts.get(symbol_id, 0) + 1
	return counts


def _best_payout(payouts: dict[int, float], count: int) -> float:
	candidates = [amount for threshold, amount in payouts.items() if count >= threshold]
	return max(candidates) if candidates else 0.0


def evaluate_payout(
	*,
	board: tuple[tuple[int, ...], ...],
	config: GameConfig,
	stake: float,
	multiplier_profile_id: int,
	rng: DeterministicRNG,
) -> PayoutResult:
	counts = _count_symbols(board)
	regular_win = 0.0
	scatter_win = 0.0

	for symbol_id, symbol in config.symbols.items():
		count = counts.get(symbol_id, 0)
		if count <= 0:
			continue
		base = _best_payout(symbol.payouts, count)
		if base <= 0:
			continue
		if symbol.symbol_type == "regular":
			regular_win += base * stake
		elif symbol.symbol_type == "scatter":
			scatter_win += base * stake

	multiplier_count = counts.get(config.multiplier_symbol_id, 0)
	multiplier_total = 0.0
	if multiplier_count > 0:
		profile = config.multiplier_profiles[multiplier_profile_id]
		for _ in range(multiplier_count):
			multiplier_total += float(rng.choice_weighted(config.multiplier_values, profile.weights))

	subtotal = regular_win + scatter_win
	total_win = subtotal * multiplier_total if subtotal > 0 and multiplier_total > 0 else subtotal

	flags: list[str] = []
	if counts.get(config.scatter_symbol_id, 0) >= config.definition.base_free_trigger_count:
		flags.append("free_trigger")

	return PayoutResult(
		regular_win=regular_win,
		scatter_win=scatter_win,
		round_multiplier_total=multiplier_total if multiplier_total > 0 else None,
		total_win=total_win,
		symbol_counts=counts,
		trigger_flags=tuple(flags),
	)
