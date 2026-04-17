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


class MinimalConfigModule(Protocol):
    SIMULATION_CONFIG: dict


MinimalConfigSource = Union[MinimalSimulationConfig, dict, MinimalConfigModule]


def normalize_minimal_config(raw_config: dict) -> MinimalSimulationConfig:
    rounds = [
        MinimalRoundConfig(
            round_id=round_data["round_id"],
            round_type=round_data["round_type"],
            roll_wins=round_data["roll_wins"],
        )
        for round_data in raw_config["rounds"]
    ]
    return MinimalSimulationConfig(rounds=rounds)


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
    for i, round_config in enumerate(config.rounds):
        if round_config.round_id != i:
            raise ValueError(f"config.rounds[{i}].round_id must equal its position")
        if round_config.round_type != "basic":
            raise ValueError(f"config.rounds[{i}].round_type must be 'basic'")
        if not round_config.roll_wins:
            raise ValueError(f"config.rounds[{i}].roll_wins must be non-empty")
        for j, value in enumerate(round_config.roll_wins):
            if value < 0:
                raise ValueError(f"config.rounds[{i}].roll_wins[{j}] must be non-negative")
