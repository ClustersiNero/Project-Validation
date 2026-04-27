from pathlib import Path
from collections.abc import Callable

from validation.canonical.schema import CanonicalResult, Cell
from validation.export.helpers import final_free_carry, win_x


def export_trace_markdown(
    result: CanonicalResult,
    paytable: dict,
    output_path: str,
    *,
    config_module_path: str,
    progress_callback: Callable[[int, int], None] | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    total_steps = sum(len(bet.rounds) for bet in result.bets) + sum(
        len(rnd.rolls) for bet in result.bets for rnd in bet.rounds
    )
    completed_steps = 0

    with path.open("w", encoding="utf-8", newline="") as handle:
        _write_lines(
            handle,
            _build_trace_header(result, paytable, config_module_path=config_module_path),
        )
        for bet in result.bets:
            _write_lines(handle, _build_bet_lines(bet, result.simulation_metadata))
            for rnd in bet.rounds:
                _write_lines(handle, _build_round_lines(rnd, result.simulation_metadata, paytable))
                completed_steps += 1
                if progress_callback is not None:
                    progress_callback(completed_steps, total_steps)
                for roll in rnd.rolls:
                    _write_lines(handle, _build_roll_lines(roll, result.simulation_metadata, paytable))
                    completed_steps += 1
                    if progress_callback is not None:
                        progress_callback(completed_steps, total_steps)


def build_trace_markdown(
    result: CanonicalResult,
    paytable: dict,
    *,
    config_module_path: str,
) -> str:
    lines = _build_trace_header(result, paytable, config_module_path=config_module_path)
    for bet in result.bets:
        lines.extend(_build_bet_lines(bet, result.simulation_metadata))
        for rnd in bet.rounds:
            lines.extend(_build_round_lines(rnd, result.simulation_metadata, paytable))
            for roll in rnd.rolls:
                lines.extend(_build_roll_lines(roll, result.simulation_metadata, paytable))
    return "\n".join(lines).strip() + "\n"


def _build_trace_header(
    result: CanonicalResult,
    paytable: dict,
    *,
    config_module_path: str,
) -> list[str]:
    metadata = result.simulation_metadata
    lines = [
        "# Run Trace",
        "",
        "## Run",
        f"- config_module: `{config_module_path}`",
        f"- config_id: `{metadata.config_id}`",
        f"- mode: `{metadata.mode}`",
        f"- seed: `{metadata.seed}`",
        f"- total_bets: `{metadata.total_bets}`",
        f"- bet_amount: `{metadata.bet_amount}`",
        f"- bet_level: `{metadata.bet_level}`",
        "",
        "## Legend",
    ]
    for symbol_id in sorted(paytable):
        symbol_config = paytable[symbol_id]
        code = _symbol_code(symbol_id, paytable)
        symbol_name = symbol_config["symbol_name"]
        symbol_type = symbol_config["symbol_type"]
        if symbol_type == "multiplier":
            lines.append(f"- `{code}<n>` = {symbol_name} (multiplier)")
        else:
            lines.append(f"- `{code}` = {symbol_name} ({symbol_type})")
    return lines


def _build_bet_lines(bet, metadata) -> list[str]:
    return [
        "",
        f"## Bet {bet.bet_id}",
        f"- bet_win_amount: `{bet.bet_win_amount:.6f}`",
        f"- bet_win_x: `{win_x(bet.bet_win_amount, metadata.bet_amount):.6f}`",
        f"- basic_win_amount: `{bet.basic_win_amount:.6f}`",
        f"- free_win_amount: `{bet.free_win_amount:.6f}`",
        f"- round_count: `{bet.round_count}`",
        f"- final_free_carried_multiplier: `{final_free_carry(bet):.6f}`",
    ]


def _build_round_lines(rnd, metadata, paytable: dict) -> list[str]:
    lines = [
        "",
        f"### Round {rnd.round_id} ({rnd.round_type})",
        f"- round_win_amount: `{rnd.round_win_amount:.6f}`",
        f"- round_win_x: `{win_x(rnd.round_win_amount, metadata.bet_amount):.6f}`",
        f"- roll_count: `{rnd.roll_count}`",
        f"- base_symbol_win_amount: `{rnd.base_symbol_win_amount:.6f}`",
        f"- scatter_win_amount: `{rnd.scatter_win_amount:.6f}`",
        f"- multiplier_gained_this_round: `{rnd.round_multiplier_increment:.6f}`",
        f"- round_total_multiplier: `{rnd.round_total_multiplier:.6f}`",
        f"- multiplier_carried_in: `{rnd.carried_multiplier:.6f}`",
        f"- round_scatter_increment: `{rnd.round_scatter_increment}`",
        f"- award_free_rounds: `{rnd.award_free_rounds}`",
        f"- scatter_present: `{rnd.round_scatter_increment > 0}`",
        f"- multiplier_present: `{rnd.round_multiplier_increment > 0}`",
    ]
    if rnd.round_final_state:
        lines.extend(
            [
                "",
                "#### Round Final Board",
                _render_board_markdown(rnd.round_final_state, paytable),
            ]
        )
    return lines


def _build_roll_lines(roll, metadata, paytable: dict) -> list[str]:
    return [
        "",
        f"#### Roll {roll.roll_id} ({roll.roll_type})",
        f"- roll_win_amount: `{roll.roll_win_amount:.6f}`",
        f"- roll_win_x: `{win_x(roll.roll_win_amount, metadata.bet_amount):.6f}`",
        f"- strip_set_id: `{roll.strip_set_id}`",
        f"- multiplier_profile_id: `{roll.multiplier_profile_id}`",
        f"- column_strip_ids: `{roll.column_strip_ids}`",
        f"- fill_start_indices: `{roll.fill_start_indices}`",
        f"- fill_end_indices: `{roll.fill_end_indices}`",
        f"- roll_multi_symbols_num: `{roll.roll_multi_symbols_num}`",
        f"- roll_multi_symbols_carry: `{roll.roll_multi_symbols_carry}`",
        f"- roll_scatter_symbols_num: `{roll.roll_scatter_symbols_num}`",
        "",
        "Pre-Fill Board",
        _render_board_markdown(roll.roll_pre_fill_state, paytable),
        "",
        "Filled Board",
        _render_board_markdown(roll.roll_filled_state, paytable),
        "",
        "Cleared Board",
        _render_board_markdown(roll.roll_cleared_state, paytable),
        "",
        "Gravity Board",
        _render_board_markdown(roll.roll_gravity_state, paytable),
    ]


def _write_lines(handle, lines: list[str]) -> None:
    handle.write("\n".join(lines))
    handle.write("\n")


def _render_board_markdown(board: list[list[Cell | None]], paytable: dict) -> str:
    column_headers = [f"C{index}" for index in range(1, 7)]
    lines = [
        "| Row | " + " | ".join(column_headers) + " |",
        "| --- | " + " | ".join(["---"] * len(column_headers)) + " |",
    ]
    for row_index, row in enumerate(board, start=1):
        rendered_cells = [_render_cell(cell, paytable) for cell in row]
        lines.append(f"| R{row_index} | " + " | ".join(rendered_cells) + " |")
    return "\n".join(lines)


def _render_cell(cell: Cell | None, paytable: dict) -> str:
    if cell is None:
        return "."
    code = _symbol_code(cell.symbol_id, paytable)
    if cell.multiplier_value is not None:
        return f"{code}{cell.multiplier_value}"
    return code


def _symbol_code(symbol_id: int, paytable: dict) -> str:
    symbol_name = paytable[symbol_id]["symbol_name"]
    parts = [part for part in symbol_name.replace("-", "_").split("_") if part]
    if len(parts) >= 2:
        return "".join(part[0].upper() for part in parts[:2])
    if parts:
        return parts[0][:2].upper()
    return f"S{symbol_id}"
