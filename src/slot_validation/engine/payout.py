from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig
from slot_validation.engine.rng import DeterministicRNG


@dataclass(frozen=True)
class RegularWinResult:
	regular_win: float
	winning_positions: set[tuple[int, int]]
	winning_symbols_details: dict[int, dict[str, float | int]]


@dataclass(frozen=True)
class RoundFinalizationResult:
	scatter_win: float
	round_multiplier_total: float
	total_win: float
	applied_multiplier: float
	updated_global_multiplier: float
	bonus_rounds_awarded: int
	trigger_flags: tuple[str, ...]
	symbol_counts: dict[int, int]


def _count_symbols(board: tuple[tuple[int, ...], ...]) -> dict[int, int]:
	counts: dict[int, int] = {}
	for row in board:
		for symbol_id in row:
			counts[symbol_id] = counts.get(symbol_id, 0) + 1
	return counts


def _best_payout(payouts: dict[int, float], count: int) -> float:
	candidates = [amount for threshold, amount in payouts.items() if count >= threshold]
	return max(candidates) if candidates else 0.0


def evaluate_regular_wins(
	*,
	board: tuple[tuple[int, ...], ...],
	config: GameConfig,
	wager_amount: float,
) -> RegularWinResult:
	rows = config.definition.board_rows
	cols = config.definition.board_cols
	symbol_positions: dict[int, list[tuple[int, int]]] = defaultdict(list)
	for row in range(rows):
		for col in range(cols):
			symbol_id = board[row][col]
			symbol = config.symbols.get(symbol_id)
			if symbol is not None and symbol.symbol_type == "regular":
				symbol_positions[symbol_id].append((col, row))

	regular_win = 0.0
	winning_positions: set[tuple[int, int]] = set()
	winning_symbols_details: dict[int, dict[str, float | int]] = {}
	for symbol_id, positions in symbol_positions.items():
		symbol = config.symbols[symbol_id]
		count = len(positions)
		if count <= 0:
			continue
		base = _best_payout(symbol.payouts, count)
		if base <= 0:
			continue
		regular_win += base * wager_amount
		winning_positions.update(positions)
		winning_symbols_details[symbol_id] = {
			"count": count,
			"odds": base,
		}

	return RegularWinResult(
		regular_win=regular_win,
		winning_positions=winning_positions,
		winning_symbols_details=winning_symbols_details,
	)


def _evaluate_scatter(
	*,
	state_name: str,
	config: GameConfig,
	wager_amount: float,
	symbol_counts: dict[int, int],
) -> tuple[float, int, tuple[str, ...]]:
	scatter_count = symbol_counts.get(config.scatter_symbol_id, 0)
	scatter_symbol = config.symbols[config.scatter_symbol_id]
	scatter_win = _best_payout(scatter_symbol.payouts, scatter_count) * wager_amount

	trigger_flags: list[str] = []
	bonus_rounds_awarded = 0
	if state_name == config.definition.base_state_name:
		if scatter_count >= config.definition.base_free_trigger_count:
			trigger_flags.append("free_trigger")
			bonus_rounds_awarded = config.definition.base_awarded_free_spins
	else:
		if scatter_count >= config.definition.retrigger_count:
			trigger_flags.append("free_retrigger")
			bonus_rounds_awarded = config.definition.retrigger_awarded_free_spins

	return scatter_win, bonus_rounds_awarded, tuple(trigger_flags)


def _evaluate_round_multiplier(
	*,
	symbol_counts: dict[int, int],
	config: GameConfig,
	multiplier_profile_id: int,
	rng: DeterministicRNG,
) -> tuple[float, bool]:
	multiplier_count = symbol_counts.get(config.multiplier_symbol_id, 0)
	if multiplier_count <= 0:
		return 0.0, False

	profile = config.multiplier_profiles[multiplier_profile_id]
	multiplier_total = 0.0
	for _ in range(multiplier_count):
		multiplier_total += float(rng.choice_weighted(config.multiplier_values, profile.weights))
	return multiplier_total, True


def finalize_round_payout(
	*,
	board: tuple[tuple[int, ...], ...],
	config: GameConfig,
	state_name: str,
	wager_amount: float,
	regular_chain_win: float,
	stored_global_multiplier: float,
	multiplier_profile_id: int,
	rng: DeterministicRNG,
) -> RoundFinalizationResult:
	symbol_counts = _count_symbols(board)
	scatter_win, bonus_rounds_awarded, trigger_flags = _evaluate_scatter(
		state_name=state_name,
		config=config,
		wager_amount=wager_amount,
		symbol_counts=symbol_counts,
	)
	round_multiplier_total, has_round_multiplier_symbol = _evaluate_round_multiplier(
		symbol_counts=symbol_counts,
		config=config,
		multiplier_profile_id=multiplier_profile_id,
		rng=rng,
	)

	round_subtotal = regular_chain_win + scatter_win
	applied_multiplier = 1.0
	updated_global_multiplier = stored_global_multiplier
	definition = config.definition

	if state_name == definition.free_state_name and definition.free_game_has_global_multiplier:
		current_round_multiplier_required = (
			definition.free_game_global_multiplier_applies_only_if_current_round_has_multiplier_symbol
		)
		can_apply_global = round_subtotal > 0 and (
			has_round_multiplier_symbol or not current_round_multiplier_required
		)
		if can_apply_global:
			if definition.free_game_applied_multiplier_combines_current_and_global_by_addition:
				applied_multiplier = round_multiplier_total + stored_global_multiplier
			else:
				applied_multiplier = round_multiplier_total
		if definition.free_game_collects_round_multiplier_into_global and round_multiplier_total > 0 and round_subtotal > 0:
			if definition.free_game_global_multiplier_accumulates_by_addition:
				updated_global_multiplier = stored_global_multiplier + round_multiplier_total
			else:
				updated_global_multiplier = round_multiplier_total
	else:
		if round_multiplier_total > 0 and round_subtotal > 0 and definition.multiplier_applies_to_entire_round_win:
			applied_multiplier = round_multiplier_total

	total_win = round_subtotal * applied_multiplier if round_subtotal > 0 else 0.0

	return RoundFinalizationResult(
		scatter_win=scatter_win,
		round_multiplier_total=round_multiplier_total,
		total_win=total_win,
		applied_multiplier=applied_multiplier,
		updated_global_multiplier=updated_global_multiplier,
		bonus_rounds_awarded=bonus_rounds_awarded,
		trigger_flags=trigger_flags,
		symbol_counts=symbol_counts,
	)
