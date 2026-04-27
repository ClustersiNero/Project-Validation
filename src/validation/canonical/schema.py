from dataclasses import dataclass, field


@dataclass
class SimulationMetadata:
    simulation_id: str = ""
    config_id: str = ""
    config_version: str = ""
    engine_version: str = ""
    schema_version: str = ""
    mode: str = ""
    seed: int = 0
    bet_amount: float = 0.0
    bet_level: float = 0.0
    total_bets: int = 0
    timestamp: str = ""


@dataclass
class Cell:
    symbol_id: int
    multiplier_value: int | None = None


BoardState = list[list[Cell | None]]


@dataclass
class RollRecord:
    roll_id: int = 0
    roll_win_amount: float = 0.0
    roll_type: str = ""
    strip_set_id: int = 0
    multiplier_profile_id: int = 0
    column_strip_ids: list[int] = field(default_factory=list)
    fill_start_indices: list[int] = field(default_factory=list)
    fill_end_indices: list[int] = field(default_factory=list)
    roll_pre_fill_state: BoardState = field(default_factory=list)
    roll_filled_state: BoardState = field(default_factory=list)
    roll_cleared_state: BoardState = field(default_factory=list)
    roll_gravity_state: BoardState = field(default_factory=list)
    roll_multi_symbols_num: int = 0
    roll_multi_symbols_carry: list[int] = field(default_factory=list)
    roll_scatter_symbols_num: int = 0


@dataclass
class RoundRecord:
    round_id: int = 0
    round_type: str = ""
    round_win_amount: float = 0.0
    base_symbol_win_amount: float = 0.0
    carried_multiplier: float = 0.0
    round_multiplier_increment: float = 0.0
    round_total_multiplier: float = 1.0
    round_scatter_increment: int = 0
    award_free_rounds: int = 0
    scatter_win_amount: float = 0.0
    roll_count: int = 0
    round_final_state: BoardState | None = None
    rolls: list[RollRecord] = field(default_factory=list)


@dataclass
class BetRecord:
    bet_id: int = 0
    bet_win_amount: float = 0.0
    basic_win_amount: float = 0.0
    free_win_amount: float = 0.0
    round_count: int = 0
    bet_final_state: BoardState | None = None
    rounds: list[RoundRecord] = field(default_factory=list)


@dataclass
class CanonicalResult:
    simulation_metadata: SimulationMetadata = field(default_factory=SimulationMetadata)
    bets: list[BetRecord] = field(default_factory=list)
