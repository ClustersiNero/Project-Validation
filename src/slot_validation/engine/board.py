from __future__ import annotations

from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig, RoundFlowConfig
from slot_validation.engine.rng import DeterministicRNG


@dataclass(frozen=True)
class BoardResult:
	board: tuple[tuple[int, ...], ...]
	strip_set_id: int
	multiplier_profile_id: int


def _slice_cyclic(strip: tuple[int, ...], start_idx: int, size: int) -> tuple[int, ...]:
	n = len(strip)
	return tuple(strip[(start_idx + i) % n] for i in range(size))


def generate_board(
	*,
	config: GameConfig,
	mode_id: int,
	state_name: str,
	rng: DeterministicRNG,
) -> BoardResult:
	mode_flow = config.implementation[mode_id]
	flow: RoundFlowConfig = mode_flow.basic if state_name == config.definition.base_state_name else mode_flow.free

	strip_set_id = rng.weighted_index(flow.strip_set_weights) + 1
	profile_id = rng.weighted_index(flow.multiplier_profile_weights) + 1

	strip_set = config.strip_sets[strip_set_id]
	strip_ids = list(strip_set.keys())
	rng.shuffle(strip_ids)

	cols = config.definition.board_cols
	rows = config.definition.board_rows
	columns: list[tuple[int, ...]] = []
	for col in range(cols):
		strip = strip_set[strip_ids[col]]
		start_idx = rng.randint(0, len(strip) - 1)
		columns.append(_slice_cyclic(strip, start_idx, rows))

	board = tuple(tuple(columns[col][row] for col in range(cols)) for row in range(rows))
	return BoardResult(board=board, strip_set_id=strip_set_id, multiplier_profile_id=profile_id)
