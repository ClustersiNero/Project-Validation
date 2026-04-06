from __future__ import annotations

from dataclasses import dataclass

from slot_validation.config.game_config import GameConfig
from slot_validation.engine.evaluator import EvaluatedSpin, evaluate_single_spin
from slot_validation.engine.rng import DeterministicRNG


@dataclass(frozen=True)
class EngineRunResult:
	seed: int
	wager_mode_id: int
	state_name: str
	stake: float
	spins: int
	total_bet: float
	total_win: float
	spin_results: tuple[EvaluatedSpin, ...]


def run_engine(
	*,
	config: GameConfig,
	seed: int,
	wager_mode_id: int,
	spins: int,
	stake: float = 1.0,
	state_name: str = "basic",
) -> EngineRunResult:
	if spins <= 0:
		raise ValueError("spins must be > 0")
	if stake <= 0:
		raise ValueError("stake must be > 0")
	if wager_mode_id not in config.wager_modes:
		raise ValueError(f"Unknown wager_mode_id: {wager_mode_id}")

	rng = DeterministicRNG(seed=seed)
	spin_results: list[EvaluatedSpin] = []

	for spin_index in range(1, spins + 1):
		spin = evaluate_single_spin(
			spin_index=spin_index,
			mode_id=wager_mode_id,
			state_name=state_name,
			stake=stake,
			config=config,
			rng=rng,
		)
		spin_results.append(spin)

	total_bet = float(spins) * float(stake)
	total_win = float(sum(s.total_win for s in spin_results))

	return EngineRunResult(
		seed=seed,
		wager_mode_id=wager_mode_id,
		state_name=state_name,
		stake=stake,
		spins=spins,
		total_bet=total_bet,
		total_win=total_win,
		spin_results=tuple(spin_results),
	)
