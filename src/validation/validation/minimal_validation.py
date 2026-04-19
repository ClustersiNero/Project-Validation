from validation.core.types import CanonicalResult, MetricsBundle, ValidationReport


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
    for bet in result.bets:
        if bet.round_count < 0:
            issues.append(f"bet {bet.bet_id} round_count must be non-negative")
        if bet.bet_win_amount < 0.0:
            issues.append(f"bet {bet.bet_id} bet_win_amount must be non-negative")
        if bet.round_count != len(bet.rounds):
            issues.append(f"bet {bet.bet_id} round_count does not match len(rounds)")
        for rnd in bet.rounds:
            if rnd.roll_count < 0:
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll_count must be non-negative")
            if rnd.round_win_amount < 0.0:
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} round_win_amount must be non-negative")
            if rnd.roll_count != len(rnd.rolls):
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll_count does not match len(rolls)")
            for roll in rnd.rolls:
                if roll.roll_win_amount < 0.0:
                    issues.append(f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} roll_win_amount must be non-negative")
            if rnd.round_win_amount != sum(roll.roll_win_amount for roll in rnd.rolls):
                issues.append(f"bet {bet.bet_id} round {rnd.round_id} round_win_amount does not equal sum(roll_win_amount)")
        if bet.bet_win_amount != sum(rnd.round_win_amount for rnd in bet.rounds):
            issues.append(f"bet {bet.bet_id} bet_win_amount does not equal sum(round_win_amount)")
    return ValidationReport(is_valid=len(issues) == 0, issues=issues)
