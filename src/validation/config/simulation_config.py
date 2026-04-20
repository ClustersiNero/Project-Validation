from dataclasses import dataclass
from typing import Protocol, Union


@dataclass
class SimulationConfig:
    seed: int = 0
    mode_id: int = 1
    bet_count: int = 1

    simulation_mode: dict | None = None
    paytable: dict | None = None
    multiplier_data: dict | None = None
    strip_sets: dict | None = None
    implementation_config: dict | None = None



class GameConfigModule(Protocol):
    SIMULATION_MODE: dict
    PAYTABLE: dict
    MULTIPLIER_DATA: dict
    STRIP_SETS: dict
    IMPLEMENTATION_CONFIG: dict


ConfigSource = Union[SimulationConfig, dict, GameConfigModule]

_CONFIG_BLOCK_NAMES = (
    "simulation_mode",
    "paytable",
    "multiplier_data",
    "strip_sets",
    "implementation_config",
)
_VALID_ROUND_TYPES = {"basic", "free"}
_VALID_SYMBOL_TYPES = {"regular", "scatter", "multiplier"}


def normalize_simulation_config(
    raw_config: dict,
    *,
    simulation_mode: dict | None = None,
    paytable: dict | None = None,
    multiplier_data: dict | None = None,
    strip_sets: dict | None = None,
    implementation_config: dict | None = None,
) -> SimulationConfig:
    return SimulationConfig(
        seed=raw_config.get("seed", 0),
        mode_id=raw_config.get("mode_id", 1),
        bet_count=raw_config.get("bet_count", 1),
        simulation_mode=raw_config.get("simulation_mode", simulation_mode),
        paytable=raw_config.get("paytable", paytable),
        multiplier_data=raw_config.get("multiplier_data", multiplier_data),
        strip_sets=raw_config.get("strip_sets", strip_sets),
        implementation_config=raw_config.get("implementation_config", implementation_config),
    )


def load_simulation_config(config_input: ConfigSource) -> SimulationConfig:
    if isinstance(config_input, SimulationConfig):
        return config_input
    elif isinstance(config_input, dict):
        return normalize_simulation_config(config_input)
    else:
        return SimulationConfig(
            simulation_mode=config_input.SIMULATION_MODE,
            paytable=config_input.PAYTABLE,
            multiplier_data=config_input.MULTIPLIER_DATA,
            strip_sets=config_input.STRIP_SETS,
            implementation_config=config_input.IMPLEMENTATION_CONFIG,
        )


def validate_simulation_config(config: SimulationConfig) -> None:
    _validate_run_input(config)
    _validate_config_blocks(config)
    _validate_simulation_modes(config.simulation_mode)
    _validate_paytable(config.paytable)
    _validate_multiplier_data(config.multiplier_data)
    _validate_strip_sets(config.strip_sets, config.paytable)
    _validate_implementation_config(
        implementation_config=config.implementation_config,
        simulation_mode=config.simulation_mode,
        strip_sets=config.strip_sets,
        multiplier_data=config.multiplier_data,
    )

    if config.mode_id not in config.simulation_mode:
        raise ValueError("config.mode_id must exist in simulation_mode")
    if config.mode_id not in config.implementation_config:
        raise ValueError("config.mode_id must exist in implementation_config")


def _validate_run_input(config: SimulationConfig) -> None:
    if type(config.seed) is not int:
        raise ValueError("config.seed must be an int")
    if type(config.mode_id) is not int:
        raise ValueError("config.mode_id must be an int")
    if config.mode_id <= 0:
        raise ValueError("config.mode_id must be positive")
    if type(config.bet_count) is not int:
        raise ValueError("config.bet_count must be an int")
    if config.bet_count <= 0:
        raise ValueError("config.bet_count must be positive")


def _validate_config_blocks(config: SimulationConfig) -> None:
    for block_name in _CONFIG_BLOCK_NAMES:
        block = getattr(config, block_name)
        if block is None:
            raise ValueError(f"config.{block_name} must be provided")
        if not isinstance(block, dict):
            raise ValueError(f"config.{block_name} must be a dict")
        if not block:
            raise ValueError(f"config.{block_name} must be non-empty")


def _validate_simulation_modes(simulation_mode: dict) -> None:
    for mode_id, mode_config in simulation_mode.items():
        if type(mode_id) is not int or mode_id <= 0:
            raise ValueError("simulation_mode keys must be positive ints")
        if not isinstance(mode_config, dict):
            raise ValueError("simulation_mode[mode_id] must be a dict")
        if not isinstance(mode_config.get("mode_name"), str) or not mode_config["mode_name"]:
            raise ValueError("simulation_mode[mode_id].mode_name must be a non-empty string")
        bet_cost_multiplier = mode_config.get("bet_cost_multiplier")
        if type(bet_cost_multiplier) not in (int, float) or bet_cost_multiplier <= 0:
            raise ValueError("simulation_mode[mode_id].bet_cost_multiplier must be positive")


def _validate_paytable(paytable: dict) -> None:
    symbol_names = set()
    for symbol_id, symbol_config in paytable.items():
        if type(symbol_id) is not int or symbol_id <= 0:
            raise ValueError("paytable keys must be positive ints")
        if not isinstance(symbol_config, dict):
            raise ValueError("paytable[symbol_id] must be a dict")
        symbol_name = symbol_config.get("symbol_name")
        if not isinstance(symbol_name, str) or not symbol_name:
            raise ValueError("paytable[symbol_id].symbol_name must be a non-empty string")
        if symbol_name in symbol_names:
            raise ValueError("paytable symbol_name values must be unique")
        symbol_names.add(symbol_name)
        symbol_type = symbol_config.get("symbol_type")
        if symbol_type not in _VALID_SYMBOL_TYPES:
            raise ValueError("paytable[symbol_id].symbol_type must be valid")
        if symbol_type in {"regular", "scatter"}:
            if "payouts" not in symbol_config or not isinstance(symbol_config["payouts"], dict):
                raise ValueError("regular and scatter symbols must define payouts")
        elif "payouts" in symbol_config:
            raise ValueError("multiplier symbols must not define payouts")


def _validate_multiplier_data(multiplier_data: dict) -> None:
    multiplier_values = multiplier_data.get("value")
    multiplier_weights_by_profile = multiplier_data.get("weight")
    if not isinstance(multiplier_values, list) or not multiplier_values:
        raise ValueError("multiplier_data.value must be a non-empty list")
    if any(type(value) is not int or value <= 0 for value in multiplier_values):
        raise ValueError("multiplier_data.value values must be positive ints")
    if not isinstance(multiplier_weights_by_profile, dict) or not multiplier_weights_by_profile:
        raise ValueError("multiplier_data.weight must be a non-empty dict")
    for profile_id, profile_weights in multiplier_weights_by_profile.items():
        if type(profile_id) is not int or profile_id <= 0:
            raise ValueError("multiplier_data.weight keys must be positive ints")
        _validate_weight_list(profile_weights, "multiplier profile weights")
        if len(profile_weights) != len(multiplier_values):
            raise ValueError("multiplier profile weights length must match multiplier_data.value")


def _validate_strip_sets(strip_sets: dict, paytable: dict) -> None:
    for strip_set_id, strip_set in strip_sets.items():
        if type(strip_set_id) is not int or strip_set_id <= 0:
            raise ValueError("strip_sets keys must be positive ints")
        if not isinstance(strip_set, dict):
            raise ValueError("strip sets must be dicts")
        if len(strip_set) != 6:
            raise ValueError("strip sets must define exactly 6 strips")
        for strip_id, strip in strip_set.items():
            if type(strip_id) is not int or strip_id <= 0:
                raise ValueError("strip ids must be positive ints")
            if not isinstance(strip, list):
                raise ValueError("strips must be lists")
            if not strip:
                raise ValueError("strips must be non-empty")
            for symbol_id in strip:
                if symbol_id not in paytable:
                    raise ValueError("strip symbol ids must exist in paytable")


def _validate_implementation_config(
    implementation_config: dict,
    simulation_mode: dict,
    strip_sets: dict,
    multiplier_data: dict,
) -> None:
    if set(implementation_config) != set(simulation_mode):
        raise ValueError("implementation_config mode ids must match simulation_mode")
    for mode_id, mode_implementation_config in implementation_config.items():
        if not isinstance(mode_implementation_config, dict):
            raise ValueError("implementation_config[mode_id] must be a dict")
        if "basic" not in mode_implementation_config:
            raise ValueError("implementation_config[mode_id] must define config for round_type 'basic'")
        if "free" not in mode_implementation_config:
            raise ValueError("implementation_config[mode_id] must define config for round_type 'free'")
        invalid_round_types = set(mode_implementation_config) - _VALID_ROUND_TYPES
        if invalid_round_types:
            raise ValueError("implementation_config round_type keys must be valid")
        for round_type, round_config in mode_implementation_config.items():
            _validate_round_implementation_config(
                round_config=round_config,
                strip_sets=strip_sets,
                multiplier_data=multiplier_data,
            )


def _validate_round_implementation_config(
    round_config: dict,
    strip_sets: dict,
    multiplier_data: dict,
) -> None:
    if not isinstance(round_config, dict):
        raise ValueError("implementation_config[mode_id][round_type] must be a dict")
    if "round_strip_set_weights" not in round_config:
        raise ValueError("implementation_config[mode_id][round_type] must define round_strip_set_weights")
    if "round_multiplier_profile_weights" not in round_config:
        raise ValueError(
            "implementation_config[mode_id][round_type] must define round_multiplier_profile_weights"
        )

    round_strip_set_weights = round_config["round_strip_set_weights"]
    _validate_weight_list(round_strip_set_weights, "round_strip_set_weights")
    if len(round_strip_set_weights) != len(strip_sets):
        raise ValueError("round_strip_set_weights length must match strip_sets")
    reachable_strip_set_ids = _reachable_ids(round_strip_set_weights)
    if any(strip_set_id not in strip_sets for strip_set_id in reachable_strip_set_ids):
        raise ValueError("reachable strip_set_id values must exist in strip_sets")

    round_multiplier_profile_weights = round_config["round_multiplier_profile_weights"]
    _validate_weight_list(round_multiplier_profile_weights, "round_multiplier_profile_weights")
    multiplier_weights_by_profile = multiplier_data["weight"]
    reachable_profile_ids = _reachable_ids(round_multiplier_profile_weights)
    missing_profile_ids = [
        profile_id
        for profile_id in reachable_profile_ids
        if profile_id not in multiplier_weights_by_profile
    ]
    if missing_profile_ids:
        raise ValueError("reachable multiplier_profile_id values must exist in multiplier_data.weight")
    if len(round_multiplier_profile_weights) != len(multiplier_weights_by_profile):
        raise ValueError("round_multiplier_profile_weights length must match multiplier_data.weight")


def _reachable_ids(weights: list[int]) -> list[int]:
    return [index + 1 for index, weight in enumerate(weights) if weight > 0]


def _validate_weight_list(weights: object, name: str) -> None:
    if not isinstance(weights, list):
        raise ValueError(f"{name} must be a list")
    if not weights:
        raise ValueError(f"{name} must be non-empty")
    if any(type(weight) is not int for weight in weights):
        raise ValueError(f"{name} values must be ints")
    if any(weight < 0 for weight in weights):
        raise ValueError(f"{name} values must be non-negative")
    if sum(weights) <= 0:
        raise ValueError(f"sum({name}) must be positive")
