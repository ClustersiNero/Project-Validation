from dataclasses import dataclass, field

from validation.config.simulation_config import SimulationConfig
from validation.engine.rng import RNG

BOARD_ROW_COUNT = 5
MAX_CASCADE_ROLLS = 100
MAX_FREE_ROUNDS_PER_BET = 1000


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


def run_engine(config: SimulationConfig, rng: RNG) -> SimulationExecution:
    bets = [
        run_bet(config=config, rng=rng, bet_id=bet_id)
        for bet_id in range(config.bet_count)
    ]
    return SimulationExecution(
        seed=config.seed,
        mode_id=config.mode_id,
        bet_count=config.bet_count,
        bets=bets,
    )


def run_bet(
    config: SimulationConfig,
    rng: RNG,
    bet_id: int,
) -> BetExecution:
    rounds = []
    carried_multiplier = 0.0
    next_round_id = 0
    remaining_award_rounds = 0

    basic_round = run_basic_round(
        config=config,
        rng=rng,
        round_id=next_round_id,
        carried_multiplier=carried_multiplier,
    )
    rounds.append(basic_round)
    next_round_id += 1
    remaining_award_rounds += basic_round.award_free_rounds

    while remaining_award_rounds > 0:
        if next_round_id > MAX_FREE_ROUNDS_PER_BET:
            raise RuntimeError("free round limit exceeded")
        free_round = run_free_round(
            config=config,
            rng=rng,
            round_id=next_round_id,
            carried_multiplier=carried_multiplier,
        )
        rounds.append(free_round)
        next_round_id += 1
        remaining_award_rounds -= 1
        remaining_award_rounds += free_round.award_free_rounds

        if free_round.base_symbol_win_amount > 0.0:
            carried_multiplier += free_round.round_multiplier_increment

    final_state = rounds[-1].final_state

    return BetExecution(bet_id=bet_id, rounds=rounds, final_state=final_state)


def run_basic_round(
    config: SimulationConfig,
    rng: RNG,
    round_id: int,
    carried_multiplier: float,
) -> RoundExecution:
    return run_round(
        config=config,
        rng=rng,
        round_id=round_id,
        round_type="basic",
        carried_multiplier=carried_multiplier,
    )


def run_free_round(
    config: SimulationConfig,
    rng: RNG,
    round_id: int,
    carried_multiplier: float,
) -> RoundExecution:
    return run_round(
        config=config,
        rng=rng,
        round_id=round_id,
        round_type="free",
        carried_multiplier=carried_multiplier,
    )


def run_round(
    config: SimulationConfig,
    rng: RNG,
    round_id: int,
    round_type: str,
    carried_multiplier: float,
) -> RoundExecution:
    rolls = []
    roll = run_initial_roll(config=config, rng=rng, round_type=round_type)
    rolls.append(roll)

    while has_regular_win(roll.final_state, config.paytable):
        if len(rolls) > MAX_CASCADE_ROLLS:
            raise RuntimeError("cascade roll limit exceeded")
        roll = run_cascade_roll(
            config=config,
            rng=rng,
            roll_id=len(rolls),
            round_type=round_type,
            strip_set_id=roll.strip_set_id,
            multiplier_profile_id=roll.multiplier_profile_id,
            column_strip_ids=roll.column_strip_ids,
            next_strip_indices=roll.refill_end_indices,
            filled_state=roll.final_state,
        )
        rolls.append(roll)

    base_symbol_win_amount = sum(roll.roll_win_amount for roll in rolls)
    final_state = rolls[-1].final_state
    special_summary = summarize_round_specials(
        final_state=final_state,
        paytable=config.paytable,
        carried_multiplier=carried_multiplier,
        bet_level=1.0,
    )
    return RoundExecution(
        round_id=round_id,
        round_type=round_type,
        rolls=rolls,
        base_symbol_win_amount=base_symbol_win_amount,
        carried_multiplier=carried_multiplier,
        round_multiplier_increment=special_summary.round_multiplier_increment,
        round_total_multiplier=special_summary.round_total_multiplier,
        round_scatter_increment=special_summary.round_scatter_increment,
        award_free_rounds=determine_awarded_free_rounds(
            round_type=round_type,
            round_scatter_increment=special_summary.round_scatter_increment,
        ),
        scatter_win_amount=special_summary.scatter_win_amount,
        final_state=final_state,
    )


def run_initial_roll(
    config: SimulationConfig,
    rng: RNG,
    round_type: str,
) -> RollExecution:
    strip_set_id = choose_round_strip_set_id(
        config.implementation_config,
        config.mode_id,
        round_type,
        rng,
    )
    multiplier_profile_id = choose_round_multiplier_profile_id(
        config.implementation_config,
        config.mode_id,
        round_type,
        rng,
    )
    board_generation = generate_initial_board(
        strip_set=config.strip_sets[strip_set_id],
        paytable=config.paytable,
        multiplier_data=config.multiplier_data,
        multiplier_profile_id=multiplier_profile_id,
        rng=rng,
    )
    filled_state = board_generation.board
    multi_symbols_num, scatter_symbols_num, multi_symbols_carry = collect_board_special_symbols(
        filled_state,
        config.paytable,
    )
    settlement = settle_regular_wins(
        board=filled_state,
        paytable=config.paytable,
        strip_set=config.strip_sets[strip_set_id],
        column_strip_ids=board_generation.column_strip_ids,
        next_strip_indices=board_generation.next_strip_indices,
        multiplier_data=config.multiplier_data,
        multiplier_profile_id=multiplier_profile_id,
        rng=rng,
        bet_level=1.0,
    )

    return RollExecution(
        roll_id=0,
        roll_type="initial",
        roll_win_amount=settlement.win_amount,
        strip_set_id=strip_set_id,
        multiplier_profile_id=multiplier_profile_id,
        column_strip_ids=board_generation.column_strip_ids,
        refill_start_indices=settlement.refill_start_indices,
        refill_end_indices=settlement.refill_end_indices,
        filled_state=filled_state,
        final_state=settlement.final_state,
        multi_symbols_num=multi_symbols_num,
        multi_symbols_carry=multi_symbols_carry,
        scatter_symbols_num=scatter_symbols_num,
    )


def run_cascade_roll(
    config: SimulationConfig,
    rng: RNG,
    roll_id: int,
    round_type: str,
    strip_set_id: int,
    multiplier_profile_id: int,
    column_strip_ids: list[int],
    next_strip_indices: list[int],
    filled_state: list[list[CellExecution]],
) -> RollExecution:
    multi_symbols_num, scatter_symbols_num, multi_symbols_carry = collect_board_special_symbols(
        filled_state,
        config.paytable,
    )
    settlement = settle_regular_wins(
        board=filled_state,
        paytable=config.paytable,
        strip_set=config.strip_sets[strip_set_id],
        column_strip_ids=column_strip_ids,
        next_strip_indices=next_strip_indices,
        multiplier_data=config.multiplier_data,
        multiplier_profile_id=multiplier_profile_id,
        rng=rng,
        bet_level=1.0,
    )

    return RollExecution(
        roll_id=roll_id,
        roll_type="cascade",
        roll_win_amount=settlement.win_amount,
        strip_set_id=strip_set_id,
        multiplier_profile_id=multiplier_profile_id,
        column_strip_ids=column_strip_ids,
        refill_start_indices=settlement.refill_start_indices,
        refill_end_indices=settlement.refill_end_indices,
        filled_state=filled_state,
        final_state=settlement.final_state,
        multi_symbols_num=multi_symbols_num,
        multi_symbols_carry=multi_symbols_carry,
        scatter_symbols_num=scatter_symbols_num,
    )


@dataclass
class RollSettlement:
    win_amount: float
    final_state: list[list[CellExecution]]
    refill_start_indices: list[int]
    refill_end_indices: list[int]


def settle_regular_wins(
    board: list[list[CellExecution]],
    paytable: dict,
    strip_set: dict[int, list[int]],
    column_strip_ids: list[int],
    next_strip_indices: list[int],
    multiplier_data: dict,
    multiplier_profile_id: int,
    rng: RNG,
    bet_level: float,
) -> RollSettlement:
    evaluation = evaluate_regular_wins(board, paytable, bet_level)
    cleared_board = clear_winning_positions(board, evaluation.winning_positions)
    settled_board = apply_gravity(cleared_board)
    refill_start_indices = list(next_strip_indices)
    refill_result = refill_board(
        board=settled_board,
        strip_set=strip_set,
        column_strip_ids=column_strip_ids,
        next_strip_indices=refill_start_indices,
        paytable=paytable,
        multiplier_data=multiplier_data,
        multiplier_profile_id=multiplier_profile_id,
        rng=rng,
    )
    return RollSettlement(
        win_amount=evaluation.win_amount,
        final_state=refill_result.board,
        refill_start_indices=refill_start_indices,
        refill_end_indices=refill_result.next_strip_indices,
    )


def evaluate_regular_wins(
    board: list[list[CellExecution]],
    paytable: dict,
    bet_level: float,
) -> RegularWinEvaluation:
    symbol_counts: dict[int, int] = {}
    symbol_positions: dict[int, set[tuple[int, int]]] = {}

    for row_index, row in enumerate(board):
        for col_index, cell in enumerate(row):
            symbol_config = paytable[cell.symbol_id]
            if symbol_config["symbol_type"] != "regular":
                continue
            symbol_counts[cell.symbol_id] = symbol_counts.get(cell.symbol_id, 0) + 1
            symbol_positions.setdefault(cell.symbol_id, set()).add((row_index, col_index))

    win_amount = 0.0
    winning_positions: set[tuple[int, int]] = set()
    for symbol_id, count in symbol_counts.items():
        payouts = paytable[symbol_id].get("payouts", {})
        qualifying_counts = [required_count for required_count in payouts if required_count <= count]
        if not qualifying_counts:
            continue

        matched_count = max(qualifying_counts)
        win_amount += payouts[matched_count] * bet_level
        winning_positions.update(symbol_positions[symbol_id])

    return RegularWinEvaluation(
        win_amount=win_amount,
        winning_positions=winning_positions,
    )


def has_regular_win(board: list[list[CellExecution]], paytable: dict) -> bool:
    return bool(evaluate_regular_wins(board, paytable, bet_level=1.0).winning_positions)


def summarize_round_specials(
    final_state: list[list[CellExecution | None]],
    paytable: dict,
    carried_multiplier: float,
    bet_level: float,
) -> RoundSpecialSummary:
    _, round_scatter_increment, multiplier_values = collect_board_special_symbols(
        final_state,
        paytable,
    )
    round_multiplier_increment = float(sum(multiplier_values))
    round_total_multiplier = (
        carried_multiplier + round_multiplier_increment
        if round_multiplier_increment > 0
        else 1.0
    )
    scatter_win_amount = evaluate_scatter_win(
        final_state,
        paytable,
        bet_level,
    )
    return RoundSpecialSummary(
        round_multiplier_increment=round_multiplier_increment,
        round_total_multiplier=round_total_multiplier,
        round_scatter_increment=round_scatter_increment,
        scatter_win_amount=scatter_win_amount,
    )


def evaluate_scatter_win(
    final_state: list[list[CellExecution | None]],
    paytable: dict,
    bet_level: float,
) -> float:
    scatter_counts: dict[int, int] = {}
    for row in final_state:
        for cell in row:
            if cell is None:
                continue
            symbol_config = paytable[cell.symbol_id]
            if symbol_config["symbol_type"] == "scatter":
                scatter_counts[cell.symbol_id] = scatter_counts.get(cell.symbol_id, 0) + 1

    scatter_win_amount = 0.0
    for symbol_id, scatter_count in scatter_counts.items():
        payouts = paytable[symbol_id].get("payouts", {})
        qualifying_counts = [
            required_count
            for required_count in payouts
            if required_count <= scatter_count
        ]
        if not qualifying_counts:
            continue

        matched_count = max(qualifying_counts)
        scatter_win_amount += payouts[matched_count] * bet_level

    return scatter_win_amount


def determine_awarded_free_rounds(
    round_type: str,
    round_scatter_increment: int,
) -> int:
    if round_type == "basic" and round_scatter_increment >= 4:
        return 15
    if round_type == "free" and round_scatter_increment >= 3:
        return 5
    return 0


def clear_winning_positions(
    board: list[list[CellExecution]],
    winning_positions: set[tuple[int, int]],
) -> list[list[CellExecution | None]]:
    return [
        [
            None if (row_index, col_index) in winning_positions else cell
            for col_index, cell in enumerate(row)
        ]
        for row_index, row in enumerate(board)
    ]


def apply_gravity(
    board: list[list[CellExecution | None]],
) -> list[list[CellExecution | None]]:
    if not board:
        return []

    row_count = len(board)
    col_count = len(board[0])
    settled_board: list[list[CellExecution | None]] = [
        [None for _ in range(col_count)] for _ in range(row_count)
    ]

    for col_index in range(col_count):
        non_empty_cells = [
            board[row_index][col_index]
            for row_index in range(row_count)
            if board[row_index][col_index] is not None
        ]
        for row_index, cell in enumerate(non_empty_cells):
            settled_board[row_index][col_index] = cell

    return settled_board


def refill_board(
    board: list[list[CellExecution | None]],
    strip_set: dict[int, list[int]],
    column_strip_ids: list[int],
    next_strip_indices: list[int],
    paytable: dict,
    multiplier_data: dict,
    multiplier_profile_id: int,
    rng: RNG,
) -> RefillResult:
    refilled_board = [list(row) for row in board]
    updated_next_indices = list(next_strip_indices)

    for col_index, strip_id in enumerate(column_strip_ids):
        strip = strip_set[strip_id]
        next_index = updated_next_indices[col_index]
        empty_row_indices = [
            row_index
            for row_index, row in enumerate(refilled_board)
            if row[col_index] is None
        ]

        for row_index in empty_row_indices:
            symbol_id = strip[next_index]
            refilled_board[row_index][col_index] = make_cell(
                symbol_id,
                paytable,
                multiplier_data,
                multiplier_profile_id,
                rng,
            )
            next_index = (next_index + 1) % len(strip)
        updated_next_indices[col_index] = next_index

    return RefillResult(
        board=refilled_board,
        next_strip_indices=updated_next_indices,
    )


def generate_initial_board(
    strip_set: dict[int, list[int]],
    paytable: dict,
    multiplier_data: dict,
    multiplier_profile_id: int,
    rng: RNG,
) -> BoardGeneration:
    strip_ids = list(strip_set.keys())
    shuffled_strip_ids = shuffle_strip_ids(strip_ids, rng)
    next_strip_indices = []
    board: list[list[CellExecution | None]] = [
        [None for _ in shuffled_strip_ids] for _ in range(BOARD_ROW_COUNT)
    ]

    for col_index, strip_id in enumerate(shuffled_strip_ids):
        sample = sample_strip_column(strip_set[strip_id], BOARD_ROW_COUNT, rng)
        next_strip_indices.append(sample.next_index)
        for row_index, symbol_id in enumerate(sample.symbols):
            board[row_index][col_index] = make_cell(
                symbol_id,
                paytable,
                multiplier_data,
                multiplier_profile_id,
                rng,
            )

    return BoardGeneration(
        board=board,
        column_strip_ids=shuffled_strip_ids,
        next_strip_indices=next_strip_indices,
    )


def shuffle_strip_ids(strip_ids: list[int], rng: RNG) -> list[int]:
    shuffled = list(strip_ids)
    for index in range(len(shuffled) - 1, 0, -1):
        swap_index = rng.next_int(0, index)
        shuffled[index], shuffled[swap_index] = shuffled[swap_index], shuffled[index]
    return shuffled


def sample_strip_column(strip: list[int], row_count: int, rng: RNG) -> StripSample:
    start_index = rng.next_int(0, len(strip) - 1)
    return StripSample(
        symbols=[strip[(start_index + offset) % len(strip)] for offset in range(row_count)],
        next_index=(start_index + row_count) % len(strip),
    )


def make_cell(
    symbol_id: int,
    paytable: dict,
    multiplier_data: dict,
    multiplier_profile_id: int,
    rng: RNG,
) -> CellExecution:
    symbol_config = paytable[symbol_id]
    if symbol_config["symbol_type"] == "multiplier":
        return CellExecution(
            symbol_id=symbol_id,
            multiplier_value=choose_multiplier_value(
                multiplier_data,
                multiplier_profile_id,
                rng,
            ),
        )
    return CellExecution(symbol_id=symbol_id)


def collect_board_special_symbols(
    board: list[list[CellExecution | None]],
    paytable: dict,
) -> tuple[int, int, list[int]]:
    multiplier_count = 0
    scatter_count = 0
    multiplier_values = []
    for row in board:
        for cell in row:
            if cell is None:
                continue
            symbol_type = paytable[cell.symbol_id]["symbol_type"]
            if symbol_type == "multiplier":
                multiplier_count += 1
                if cell.multiplier_value is not None:
                    multiplier_values.append(cell.multiplier_value)
            elif symbol_type == "scatter":
                scatter_count += 1
    return multiplier_count, scatter_count, multiplier_values


def choose_weighted_id(weights: list[int], rng: RNG) -> int:
    if not weights:
        raise ValueError("weights must be non-empty")
    if any(weight < 0 for weight in weights):
        raise ValueError("weights must be non-negative")

    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("sum(weights) must be positive")

    draw = rng.next_int(1, total_weight)
    cumulative_weight = 0
    for index, weight in enumerate(weights):
        cumulative_weight += weight
        if draw <= cumulative_weight:
            return index + 1

    raise RuntimeError("weighted selection failed")


def choose_round_strip_set_id(
    implementation_config: dict,
    mode_id: int,
    round_type: str,
    rng: RNG,
) -> int:
    weights = implementation_config[mode_id][round_type]["round_strip_set_weights"]
    return choose_weighted_id(weights, rng)


def choose_round_multiplier_profile_id(
    implementation_config: dict,
    mode_id: int,
    round_type: str,
    rng: RNG,
) -> int:
    weights = implementation_config[mode_id][round_type]["round_multiplier_profile_weights"]
    return choose_weighted_id(weights, rng)


def choose_multiplier_value(
    multiplier_data: dict,
    multiplier_profile_id: int,
    rng: RNG,
) -> int:
    weights = multiplier_data["weight"][multiplier_profile_id]
    multiplier_value_id = choose_weighted_id(weights, rng)
    return multiplier_data["value"][multiplier_value_id - 1]
