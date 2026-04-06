from __future__ import annotations

from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig
from slot_validation.engine.evaluator import EngineWagerRecord, evaluate_wager
from slot_validation.engine.rng import DeterministicRNG


ENGINE_VERSION = "0.2.0"


@dataclass(frozen=True)
class EngineRunResult:
	seed: int
	config_id: str
	mode_id: int
	mode_name: str
	# Raw stake input before applying mode wager_cost_multiplier.
	stake_amount: float
	total_wagers: int
	wagers: tuple[EngineWagerRecord, ...]
	total_bet: float
	total_win: float
	engine_version: str = ENGINE_VERSION


def run_engine(
	*,
	config: GameConfig,
	config_id: str,
	seed: int,
	mode_id: int,
	total_wagers: int,
	stake_amount: float,
	state_name: str,
) -> EngineRunResult:
	if total_wagers <= 0:
		raise ValueError("total_wagers must be > 0")
	if stake_amount <= 0:
		raise ValueError("stake_amount must be > 0")
	if mode_id not in config.wager_modes:
		raise ValueError(f"Unknown mode_id: {mode_id}")

	mode = config.wager_modes[mode_id]
	wager_amount = stake_amount * mode.wager_cost_multiplier
	if wager_amount <= 0:
		raise ValueError("wager_amount must be > 0")

	rng = DeterministicRNG(seed=seed)
	wagers: list[EngineWagerRecord] = []
	for wager_id in range(1, total_wagers + 1):
		wagers.append(
			evaluate_wager(
				wager_id=wager_id,
				config=config,
				mode_id=mode_id,
				state_name=state_name,
				wager_amount=wager_amount,
				rng=rng,
			)
		)

	total_bet = float(total_wagers * wager_amount)
	total_win = float(sum(w.total_win for w in wagers))
	return EngineRunResult(
		seed=seed,
		config_id=config_id,
		mode_id=mode_id,
		mode_name=mode.mode_name,
		stake_amount=float(stake_amount),
		total_wagers=total_wagers,
		wagers=tuple(wagers),
		total_bet=total_bet,
		total_win=total_win,
	)
