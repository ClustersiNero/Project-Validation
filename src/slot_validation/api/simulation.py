from __future__ import annotations

import importlib
from typing import Any

from slot_validation.canonical.builders import build_canonical_result
from slot_validation.canonical.schema import CanonicalResult
from slot_validation.config.game_config import build_game_config
from slot_validation.engine.runner import run_engine
from slot_validation.games.olympus_mini.definition import OLYMPUS_MINI_DEFINITION


def _load_default_config_module() -> Any:
	return importlib.import_module("configs.game.olympus_mini")


def run_simulation(
	*,
	seed: int,
	spins: int,
	wager_mode_id: int = 1,
	stake: float = 1.0,
	state_name: str = "basic",
	config_module: Any | None = None,
) -> CanonicalResult:
	module = config_module if config_module is not None else _load_default_config_module()
	config = build_game_config(module=module, definition=OLYMPUS_MINI_DEFINITION)

	engine_result = run_engine(
		config=config,
		seed=seed,
		wager_mode_id=wager_mode_id,
		spins=spins,
		stake=stake,
		state_name=state_name,
	)
	return build_canonical_result(engine_result=engine_result, config=config)
