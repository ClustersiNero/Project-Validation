from dataclasses import dataclass
from typing import Protocol, Union


@dataclass
class MinimalRoundConfig:
    round_id: int
    round_type: str
    roll_wins: list[float]


@dataclass
class MinimalSimulationConfig:
    rounds: list[MinimalRoundConfig]
    seed: int = 0
    simulation_id: str = "minimal-seed-0"
    config_id: str = "minimal_config"
    config_version: str = "0.1.0"
    engine_version: str = "minimal_engine.v1"
    schema_version: str = "canonical.v1"
    mode: str = "normal"
    bet_amount: float = 1.0
    bet_level: float = 1.0
    timestamp: str = "1970-01-01T00:00:00Z"


class MinimalConfigModule(Protocol):
    SIMULATION_CONFIG: dict


MinimalConfigSource = Union[MinimalSimulationConfig, dict, MinimalConfigModule]


def normalize_minimal_config(raw_config: dict) -> MinimalSimulationConfig:
    seed = raw_config.get("seed", 0)
    rounds = [
        MinimalRoundConfig(
            round_id=round_data["round_id"],
            round_type=round_data["round_type"],
            roll_wins=round_data["roll_wins"],
        )
        for round_data in raw_config["rounds"]
    ]
    return MinimalSimulationConfig(
        rounds=rounds,
        seed=seed,
        simulation_id=raw_config.get("simulation_id", f"minimal-seed-{seed}"),
        config_id=raw_config.get("config_id", "minimal_config"),
        config_version=raw_config.get("config_version", "0.1.0"),
        engine_version=raw_config.get("engine_version", "minimal_engine.v1"),
        schema_version=raw_config.get("schema_version", "canonical.v1"),
        mode=raw_config.get("mode", "normal"),
        bet_amount=raw_config.get("bet_amount", 1.0),
        bet_level=raw_config.get("bet_level", 1.0),
        timestamp=raw_config.get("timestamp", "1970-01-01T00:00:00Z"),
    )


def load_minimal_config(config_input: MinimalConfigSource) -> MinimalSimulationConfig:
    if isinstance(config_input, MinimalSimulationConfig):
        return config_input
    elif isinstance(config_input, dict):
        return normalize_minimal_config(config_input)
    else:
        return normalize_minimal_config(config_input.SIMULATION_CONFIG)


def validate_minimal_config(config: MinimalSimulationConfig) -> None:
    if not config.rounds:
        raise ValueError("config.rounds must be non-empty")
    if not config.simulation_id:
        raise ValueError("config.simulation_id must be non-empty")
    if not config.config_id:
        raise ValueError("config.config_id must be non-empty")
    if not config.config_version:
        raise ValueError("config.config_version must be non-empty")
    if not config.engine_version:
        raise ValueError("config.engine_version must be non-empty")
    if not config.schema_version:
        raise ValueError("config.schema_version must be non-empty")
    if not config.mode:
        raise ValueError("config.mode must be non-empty")
    if config.bet_amount <= 0:
        raise ValueError("config.bet_amount must be positive")
    if config.bet_level <= 0:
        raise ValueError("config.bet_level must be positive")
    if not config.timestamp:
        raise ValueError("config.timestamp must be non-empty")
    for i, round_config in enumerate(config.rounds):
        if round_config.round_id != i:
            raise ValueError(f"config.rounds[{i}].round_id must equal its position")
        if round_config.round_type not in {"basic", "free"}:
            raise ValueError(f"config.rounds[{i}].round_type must be 'basic' or 'free'")
        if not round_config.roll_wins:
            raise ValueError(f"config.rounds[{i}].roll_wins must be non-empty")
        for j, value in enumerate(round_config.roll_wins):
            if value < 0:
                raise ValueError(f"config.rounds[{i}].roll_wins[{j}] must be non-negative")
