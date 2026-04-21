from dataclasses import dataclass, field


@dataclass
class CellExecution:
    symbol_id: int
    multiplier_value: int | None = None


@dataclass
class RollExecution:
    roll_id: int
    roll_type: str
    roll_win_amount: float
    strip_set_id: int
    multiplier_profile_id: int
    column_strip_ids: list[int] = field(default_factory=list)
    refill_start_indices: list[int] = field(default_factory=list)
    refill_end_indices: list[int] = field(default_factory=list)
    filled_state: list[list[CellExecution]] = field(default_factory=list)
    final_state: list[list[CellExecution | None]] = field(default_factory=list)
    multi_symbols_num: int = 0
    multi_symbols_carry: list[int] = field(default_factory=list)
    scatter_symbols_num: int = 0


@dataclass
class RoundExecution:
    round_id: int
    round_type: str
    rolls: list[RollExecution]
    base_symbol_win_amount: float = 0.0
    carried_multiplier: float = 0.0
    round_multiplier_increment: float = 0.0
    round_total_multiplier: float = 1.0
    round_scatter_increment: int = 0
    award_free_rounds: int = 0
    scatter_win_amount: float = 0.0
    final_state: list[list[CellExecution | None]] = field(default_factory=list)


@dataclass
class BetExecution:
    bet_id: int
    rounds: list[RoundExecution]
    final_state: list[list[CellExecution | None]] = field(default_factory=list)


@dataclass
class SimulationExecution:
    seed: int
    mode_id: int
    bet_count: int
    bets: list[BetExecution]


@dataclass
class RegularWinEvaluation:
    win_amount: float
    winning_positions: set[tuple[int, int]] = field(default_factory=set)


@dataclass
class StripSample:
    symbols: list[int]
    next_index: int


@dataclass
class BoardGeneration:
    board: list[list[CellExecution]]
    column_strip_ids: list[int]
    next_strip_indices: list[int]


@dataclass
class RefillResult:
    board: list[list[CellExecution]]
    next_strip_indices: list[int]


@dataclass
class RoundSpecialSummary:
    round_multiplier_increment: float
    round_total_multiplier: float
    round_scatter_increment: int
    scatter_win_amount: float


@dataclass
class RollSettlement:
    win_amount: float
    final_state: list[list[CellExecution]]
    refill_start_indices: list[int]
    refill_end_indices: list[int]
