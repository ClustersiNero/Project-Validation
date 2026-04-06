from __future__ import annotations

from slot_validation.canonical.schema import CanonicalResult, CanonicalSpinResult
from slot_validation.config.game_config import GameConfig
from slot_validation.engine.runner import EngineRunResult
from slot_validation.utils.ids import build_run_id
from slot_validation.utils.time import utc_now_iso


def build_canonical_result(engine_result: EngineRunResult, config: GameConfig) -> CanonicalResult:
	spin_results = tuple(
		CanonicalSpinResult(
			spin_index=s.spin_index,
			state_name=s.state_name,
			board_rows=s.board_rows,
			strip_set_id=s.strip_set_id,
			multiplier_profile_id=s.multiplier_profile_id,
			regular_win=s.regular_win,
			scatter_win=s.scatter_win,
			round_multiplier_sum=s.round_multiplier_sum,
			total_win=s.total_win,
			symbol_counts=s.symbol_counts,
		)
		for s in engine_result.spin_results
	)

	return CanonicalResult(
		run_id=build_run_id(
			game_id=config.game_id,
			seed=engine_result.seed,
			mode_id=engine_result.wager_mode_id,
			spins=engine_result.spins,
		),
		game_id=config.game_id,
		config_version=config.config_version,
		timestamp_utc=utc_now_iso(),
		seed=engine_result.seed,
		wager_mode_id=engine_result.wager_mode_id,
		state_name=engine_result.state_name,
		stake=engine_result.stake,
		spins=engine_result.spins,
		total_bet=engine_result.total_bet,
		total_win=engine_result.total_win,
		spin_results=spin_results,
	)
