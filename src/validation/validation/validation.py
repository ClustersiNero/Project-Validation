from dataclasses import dataclass, field

from validation.canonical.schema import CanonicalResult
from validation.metrics.metrics import MetricsBundle


@dataclass
class ValidationReport:
    is_valid: bool = True
    issues: list[str] = field(default_factory=list)


_FLOAT_TOLERANCE = 1e-9
_BOARD_COLUMN_COUNT = 6


def _almost_equal(left: float, right: float) -> bool:
    return abs(left - right) <= _FLOAT_TOLERANCE


def _expected_award_free_rounds(round_type: str, round_scatter_increment: int) -> int:
    if round_type == "basic" and round_scatter_increment >= 4:
        return 15
    if round_type == "free" and round_scatter_increment >= 3:
        return 5
    return 0


def validate_metrics_impl(metrics: MetricsBundle) -> ValidationReport:
    issues: list[str] = []
    if metrics.bet_count < 0:
        issues.append("bet_count must be non-negative")
    if metrics.round_count < 0:
        issues.append("round_count must be non-negative")
    if metrics.roll_count < 0:
        issues.append("roll_count must be non-negative")
    if metrics.total_bet_win_amount < 0.0:
        issues.append("total_bet_win_amount must be non-negative")
    if metrics.total_round_win_amount < 0.0:
        issues.append("total_round_win_amount must be non-negative")
    if metrics.total_roll_win_amount < 0.0:
        issues.append("total_roll_win_amount must be non-negative")
    return ValidationReport(is_valid=len(issues) == 0, issues=issues)


def validate_canonical_impl(result: CanonicalResult) -> ValidationReport:
    issues: list[str] = []
    metadata = result.simulation_metadata
    if metadata.total_bets != len(result.bets):
        issues.append("simulation_metadata.total_bets does not match len(bets)")
    if not result.bets:
        issues.append("bets must be non-empty")
    for bet in result.bets:
        expected_carried_multiplier = 0.0
        if bet.round_count < 0:
            issues.append(f"bet {bet.bet_id} round_count must be non-negative")
        if bet.bet_win_amount < 0.0:
            issues.append(f"bet {bet.bet_id} bet_win_amount must be non-negative")
        if bet.round_count != len(bet.rounds):
            issues.append(f"bet {bet.bet_id} round_count does not match len(rounds)")
        round_ids = [rnd.round_id for rnd in bet.rounds]
        if round_ids != sorted(round_ids) or len(round_ids) != len(set(round_ids)):
            issues.append(f"bet {bet.bet_id} round_id values must be strictly ascending")
        for rnd in bet.rounds:
            if rnd.round_type == "basic":
                if not _almost_equal(rnd.carried_multiplier, 0.0):
                    issues.append(f"bet {bet.bet_id} round {rnd.round_id} basic round carried_multiplier must be 0")
            elif rnd.round_type == "free":
                if not _almost_equal(rnd.carried_multiplier, expected_carried_multiplier):
                    issues.append(f"bet {bet.bet_id} round {rnd.round_id} carried_multiplier does not match prior free round carry state")
            if rnd.round_type not in {"basic", "free"}:
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} round_type must be 'basic' or 'free'")
            if rnd.roll_count < 0:
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll_count must be non-negative")
            if rnd.round_win_amount < 0.0:
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} round_win_amount must be non-negative")
            if rnd.roll_count != len(rnd.rolls):
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll_count does not match len(rolls)")
            roll_ids = [roll.roll_id for roll in rnd.rolls]
            if roll_ids != sorted(roll_ids) or len(roll_ids) != len(set(roll_ids)):
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll_id values must be strictly ascending")
            for roll_index, roll in enumerate(rnd.rolls):
                expected_roll_type = "initial" if roll_index == 0 else "cascade"
                if roll.roll_type not in {"initial", "cascade"}:
                    issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} roll_type must be 'initial' or 'cascade'")
                elif roll.roll_type != expected_roll_type:
                    issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} roll_type must be '{expected_roll_type}'")
                if roll.roll_win_amount < 0.0:
                    issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} roll_win_amount must be non-negative")
                if len(roll.column_strip_ids) != _BOARD_COLUMN_COUNT:
                    issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} column_strip_ids must have length 6")
                if len(roll.refill_start_indices) != _BOARD_COLUMN_COUNT:
                    issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} refill_start_indices must have length 6")
                if len(roll.refill_end_indices) != _BOARD_COLUMN_COUNT:
                    issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} refill_end_indices must have length 6")
                if roll_index > 0:
                    previous_roll = rnd.rolls[roll_index - 1]
                    if roll.refill_start_indices != previous_roll.refill_end_indices:
                        issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} refill_start_indices must equal previous roll refill_end_indices")
            if not _almost_equal(rnd.base_symbol_win_amount, sum(roll.roll_win_amount for roll in rnd.rolls)):
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} base_symbol_win_amount does not equal sum(roll_win_amount)")
            expected_round_win = rnd.base_symbol_win_amount * rnd.round_total_multiplier + rnd.scatter_win_amount
            if not _almost_equal(rnd.round_win_amount, expected_round_win):
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} round_win_amount does not equal base_symbol_win_amount times round_total_multiplier plus scatter_win_amount")
            if rnd.round_multiplier_increment == 0 and not _almost_equal(rnd.round_total_multiplier, 1.0):
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} round_total_multiplier must be 1 when round_multiplier_increment is 0")
            expected_award_free_rounds = _expected_award_free_rounds(
                rnd.round_type,
                rnd.round_scatter_increment,
            )
            if rnd.award_free_rounds != expected_award_free_rounds:
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} award_free_rounds does not match round_type and round_scatter_increment")
            if rnd.round_type == "free" and rnd.base_symbol_win_amount > 0.0:
                expected_carried_multiplier += rnd.round_multiplier_increment
        if not _almost_equal(bet.bet_win_amount, sum(rnd.round_win_amount for rnd in bet.rounds)):
            issues.append(f"bet {bet.bet_id} bet_win_amount does not equal sum(round_win_amount)")
        expected_basic_win = sum(rnd.round_win_amount for rnd in bet.rounds if rnd.round_type == "basic")
        expected_free_win = sum(rnd.round_win_amount for rnd in bet.rounds if rnd.round_type == "free")
        if not _almost_equal(bet.basic_win_amount, expected_basic_win):
            issues.append(f"bet {bet.bet_id} basic_win_amount does not equal sum(basic round_win_amount)")
        if not _almost_equal(bet.free_win_amount, expected_free_win):
            issues.append(f"bet {bet.bet_id} free_win_amount does not equal sum(free round_win_amount)")
        if not _almost_equal(bet.bet_win_amount, bet.basic_win_amount + bet.free_win_amount):
            issues.append(f"bet {bet.bet_id} bet_win_amount does not equal basic_win_amount plus free_win_amount")
    return ValidationReport(is_valid=len(issues) == 0, issues=issues)
