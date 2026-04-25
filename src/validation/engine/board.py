from validation.engine.rng import RNG
from validation.engine.selection import choose_multiplier_value
from validation.engine.types import BoardGeneration, CellExecution, RefillResult, StripSample

BOARD_ROW_COUNT = 5


def make_empty_board(column_count: int) -> list[list[CellExecution | None]]:
    return [[None for _ in range(column_count)] for _ in range(BOARD_ROW_COUNT)]


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
    fill_start_indices = list(next_strip_indices)
    fill_end_indices = list(next_strip_indices)
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
            fill_end_indices[col_index] = next_index
            next_index = (next_index + 1) % len(strip)
        updated_next_indices[col_index] = next_index

    return RefillResult(
        board=refilled_board,
        fill_start_indices=fill_start_indices,
        fill_end_indices=fill_end_indices,
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
    fill_start_indices = []
    fill_end_indices = []
    next_strip_indices = []
    board: list[list[CellExecution | None]] = [
        [None for _ in shuffled_strip_ids] for _ in range(BOARD_ROW_COUNT)
    ]

    for col_index, strip_id in enumerate(shuffled_strip_ids):
        sample = sample_strip_column(strip_set[strip_id], BOARD_ROW_COUNT, rng)
        fill_start_indices.append(sample.start_index)
        fill_end_indices.append(sample.end_index)
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
        fill_start_indices=fill_start_indices,
        fill_end_indices=fill_end_indices,
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
        start_index=start_index,
        end_index=(start_index + row_count - 1) % len(strip),
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
