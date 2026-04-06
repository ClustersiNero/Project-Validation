from __future__ import annotations

from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig, RoundFlowConfig
from slot_validation.engine.rng import DeterministicRNG


@dataclass(frozen=True)
class BoardBuildMeta:
	strip_set_id: int
	multiplier_profile_id: int


def _pick_weighted_id(weights: tuple[int, ...], rng: DeterministicRNG) -> int:
	return rng.weighted_index(weights) + 1


def _slice_cyclic_strip(strip: tuple[int, ...], start_idx: int, take: int) -> tuple[int, ...]:
	length = len(strip)
	return tuple(strip[(start_idx + i) % length] for i in range(take))


def generate_round_board(
	config: GameConfig,
	mode_id: int,
	state_name: str,
	rng: DeterministicRNG,
) -> tuple[tuple[int, ...], BoardBuildMeta]:
	mode_impl = config.implementation[mode_id]
	flow: RoundFlowConfig = mode_impl.basic if state_name == config.definition.base_state_name else mode_impl.free

	strip_set_id = _pick_weighted_id(flow.strip_set_weights, rng)
	multiplier_profile_id = _pick_weighted_id(flow.multiplier_profile_weights, rng)

	strip_set = config.strip_sets[strip_set_id]
	available_strip_ids = list(strip_set.keys())
	rng.shuffle(available_strip_ids)

	cols = config.definition.board_cols
	rows = config.definition.board_rows
	column_symbols: list[tuple[int, ...]] = []

	for col in range(cols):
		strip_id = available_strip_ids[col]
		strip = strip_set[strip_id]
		start = rng.randint(0, len(strip) - 1)
		column_symbols.append(_slice_cyclic_strip(strip, start, rows))

	# Convert [col][row] into immutable [row][col]
	board_rows = tuple(tuple(column_symbols[col][row] for col in range(cols)) for row in range(rows))

	return board_rows, BoardBuildMeta(
		strip_set_id=strip_set_id,
		multiplier_profile_id=multiplier_profile_id,
	)
