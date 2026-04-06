from __future__ import annotations

import importlib
from typing import Any

from slot_validation.canonical.builders import build_canonical_result
from slot_validation.canonical.schema import CanonicalResult
from slot_validation.config.game_config import build_game_config
from slot_validation.engine.runner import run_engine
from slot_validation.games.olympus_mini.definition import OLYMPUS_MINI_DEFINITION


def _load_default_module() -> Any:
	return importlib.import_module("configs.game.olympus_mini")


def run_simulation(
	*,
	seed: int,
	total_wagers: int,
	mode_id: int = 1,
	stake_amount: float = 1.0,
	state_name: str = "basic",
	config_id: str = "configs.game.olympus_mini",
	config_module: Any | None = None,
) -> CanonicalResult:
	module = config_module if config_module is not None else _load_default_module()
	game_config = build_game_config(module=module, definition=OLYMPUS_MINI_DEFINITION)

	engine_result = run_engine(
		config=game_config,
		config_id=config_id,
		seed=seed,
		mode_id=mode_id,
		total_wagers=total_wagers,
		stake_amount=stake_amount,
		state_name=state_name,
	)
	return build_canonical_result(engine_result, game_config)
