import csv
from pathlib import Path

from validation.canonical.schema import CanonicalResult
from validation.export.helpers import final_free_carry, fmt_float, win_x


def export_tuning_csvs(
    result: CanonicalResult,
    output_prefix: str,
    *,
    config_module_path: str,
) -> tuple[str, str]:
    prefix_path = Path(output_prefix)
    prefix_path.parent.mkdir(parents=True, exist_ok=True)

    bet_path = prefix_path.parent / f"{prefix_path.name}_bets.csv"
    round_path = prefix_path.parent / f"{prefix_path.name}_rounds.csv"

    bet_rows = build_bet_rows(result, config_module_path=config_module_path)
    round_rows = build_round_rows(result, config_module_path=config_module_path)

    _write_csv(bet_path, bet_rows)
    _write_csv(round_path, round_rows)
    return str(bet_path), str(round_path)


def build_bet_rows(
    result: CanonicalResult,
    *,
    config_module_path: str,
) -> list[dict]:
    metadata = result.simulation_metadata
    rows: list[dict] = []
    for bet in result.bets:
        free_rounds = [rnd for rnd in bet.rounds if rnd.round_type == "free"]
        rows.append(
            {
                "config_module": config_module_path,
                "config_id": metadata.config_id,
                "mode": metadata.mode,
                "seed": metadata.seed,
                "bet_id": bet.bet_id,
                "bet_win_amount": fmt_float(bet.bet_win_amount),
                "bet_win_x": fmt_float(win_x(bet.bet_win_amount, metadata.bet_amount)),
                "basic_win_amount": fmt_float(bet.basic_win_amount),
                "free_win_amount": fmt_float(bet.free_win_amount),
                "round_count": bet.round_count,
                "basic_round_count": sum(1 for rnd in bet.rounds if rnd.round_type == "basic"),
                "free_round_count": len(free_rounds),
                "free_containing_bet": len(free_rounds) > 0
                or any(rnd.award_free_rounds > 0 for rnd in bet.rounds if rnd.round_type == "basic"),
                "final_free_carried_multiplier": fmt_float(final_free_carry(bet)),
            }
        )
    return rows


def build_round_rows(
    result: CanonicalResult,
    *,
    config_module_path: str,
) -> list[dict]:
    metadata = result.simulation_metadata
    rows: list[dict] = []
    for bet in result.bets:
        for rnd in bet.rounds:
            rows.append(
                {
                    "config_module": config_module_path,
                    "config_id": metadata.config_id,
                    "mode": metadata.mode,
                    "seed": metadata.seed,
                    "bet_id": bet.bet_id,
                    "round_id": rnd.round_id,
                    "round_type": rnd.round_type,
                    "round_win_amount": fmt_float(rnd.round_win_amount),
                    "round_win_x": fmt_float(win_x(rnd.round_win_amount, metadata.bet_amount)),
                    "base_symbol_win_amount": fmt_float(rnd.base_symbol_win_amount),
                    "scatter_win_amount": fmt_float(rnd.scatter_win_amount),
                    "roll_count": rnd.roll_count,
                    "carried_multiplier": fmt_float(rnd.carried_multiplier),
                    "round_multiplier_increment": fmt_float(rnd.round_multiplier_increment),
                    "round_total_multiplier": fmt_float(rnd.round_total_multiplier),
                    "round_scatter_increment": rnd.round_scatter_increment,
                    "award_free_rounds": rnd.award_free_rounds,
                    "scatter_present": rnd.round_scatter_increment > 0,
                    "multiplier_present": rnd.round_multiplier_increment > 0.0,
                }
            )
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8", newline="")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
