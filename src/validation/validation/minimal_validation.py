from validation.core.types import (
    CanonicalResult,
    CheckResult,
    MetricsBundle,
    ValidationMeta,
    ValidationReport,
    ValidationSummary,
)


_FLOAT_TOLERANCE = 1e-9


def _almost_equal(left: float, right: float) -> bool:
    return abs(left - right) <= _FLOAT_TOLERANCE


def _summary(
    structural_checks: list[CheckResult],
    statistical_checks: list[CheckResult],
    regression_checks: list[CheckResult],
) -> ValidationSummary:
    structural_failed = sum(1 for check in structural_checks if check.verdict == "fail")
    statistical_failed = sum(1 for check in statistical_checks if check.verdict == "fail")
    regression_failed = sum(1 for check in regression_checks if check.verdict == "fail")
    structural_passed = len(structural_checks) - structural_failed
    statistical_passed = len(statistical_checks) - statistical_failed
    regression_passed = len(regression_checks) - regression_failed
    failed = structural_failed + statistical_failed + regression_failed
    passed = structural_passed + statistical_passed + regression_passed
    return ValidationSummary(
        total_checks=passed + failed,
        passed=passed,
        failed=failed,
        structural_passed=structural_passed,
        structural_failed=structural_failed,
        statistical_passed=statistical_passed,
        statistical_failed=statistical_failed,
        regression_passed=regression_passed,
        regression_failed=regression_failed,
        overall_verdict="pass" if failed == 0 else "fail",
    )


def _check(metric_path: str, verdict: str, notes: str) -> CheckResult:
    return CheckResult(metric_path=metric_path, verdict=verdict, notes=notes)


def _report(
    *,
    issues: list[str],
    structural_checks: list[CheckResult] | None = None,
    statistical_checks: list[CheckResult] | None = None,
    regression_checks: list[CheckResult] | None = None,
    meta: ValidationMeta | None = None,
) -> ValidationReport:
    structural_checks = structural_checks or []
    statistical_checks = statistical_checks or []
    regression_checks = regression_checks or []
    summary = _summary(structural_checks, statistical_checks, regression_checks)
    return ValidationReport(
        is_valid=summary.overall_verdict == "pass",
        issues=issues,
        meta=meta,
        structural_checks=structural_checks,
        statistical_checks=statistical_checks,
        regression_checks=regression_checks,
        summary=summary,
    )


def validate_metrics_impl(metrics: MetricsBundle) -> ValidationReport:
    issues: list[str] = []
    statistical_checks: list[CheckResult] = []
    if metrics.bet_count < 0:
        note = "bet_count must be non-negative"
        issues.append(note)
        statistical_checks.append(_check("MetricsBundle.meta.bet_count", "fail", note))
    if metrics.round_count < 0:
        note = "round_count must be non-negative"
        issues.append(note)
        statistical_checks.append(_check("MetricsBundle.meta.round_count", "fail", note))
    if metrics.roll_count < 0:
        note = "roll_count must be non-negative"
        issues.append(note)
        statistical_checks.append(_check("MetricsBundle.meta.roll_count", "fail", note))
    if metrics.total_bet_win_amount < 0.0:
        note = "total_bet_win_amount must be non-negative"
        issues.append(note)
        statistical_checks.append(_check("MetricsBundle.meta.total_bet_win_amount", "fail", note))
    if metrics.total_round_win_amount < 0.0:
        note = "total_round_win_amount must be non-negative"
        issues.append(note)
        statistical_checks.append(_check("MetricsBundle.meta.total_round_win_amount", "fail", note))
    if metrics.total_roll_win_amount < 0.0:
        note = "total_roll_win_amount must be non-negative"
        issues.append(note)
        statistical_checks.append(_check("MetricsBundle.meta.total_roll_win_amount", "fail", note))
    if not statistical_checks:
        statistical_checks.append(_check("MetricsBundle.minimal_non_negative_checks", "pass", "minimal metrics checks passed"))
    return _report(issues=issues, statistical_checks=statistical_checks)


def validate_canonical_impl(result: CanonicalResult) -> ValidationReport:
    issues: list[str] = []
    structural_checks: list[CheckResult] = []
    metadata = result.simulation_metadata
    meta = ValidationMeta(
        simulation_id=metadata.simulation_id,
        config_id=metadata.config_id,
        config_version=metadata.config_version,
        schema_version=metadata.schema_version,
        engine_version=metadata.engine_version,
        timestamp=metadata.timestamp,
    )
    required_metadata_fields = [
        "simulation_id",
        "config_id",
        "config_version",
        "engine_version",
        "schema_version",
        "mode",
        "seed",
        "bet_amount",
        "bet_level",
        "total_bets",
        "timestamp",
    ]
    for field_name in required_metadata_fields:
        if getattr(metadata, field_name) is None:
            note = f"simulation_metadata.{field_name} must be non-null"
            issues.append(note)
            structural_checks.append(_check(f"CanonicalResult.simulation_metadata.{field_name}", "fail", note))
    if metadata.total_bets != len(result.bets):
        note = "simulation_metadata.total_bets does not match len(bets)"
        issues.append(note)
        structural_checks.append(_check("CanonicalResult.simulation_metadata.total_bets", "fail", note))
    if not result.bets:
        note = "bets must be non-empty"
        issues.append(note)
        structural_checks.append(_check("CanonicalResult.bets", "fail", note))
    for bet in result.bets:
        if bet.round_count < 0:
            note = f"bet {bet.bet_id} round_count must be non-negative"
            issues.append(note)
            structural_checks.append(_check("CanonicalResult.bets.round_count", "fail", note))
        if bet.bet_win_amount < 0.0:
            note = f"bet {bet.bet_id} bet_win_amount must be non-negative"
            issues.append(note)
            structural_checks.append(_check("CanonicalResult.bets.bet_win_amount", "fail", note))
        if bet.round_count != len(bet.rounds):
            note = f"bet {bet.bet_id} round_count does not match len(rounds)"
            issues.append(note)
            structural_checks.append(_check("CanonicalResult.bets.round_count", "fail", note))
        round_ids = [rnd.round_id for rnd in bet.rounds]
        if round_ids != sorted(round_ids) or len(round_ids) != len(set(round_ids)):
            note = f"bet {bet.bet_id} round_id values must be strictly ascending"
            issues.append(note)
            structural_checks.append(_check("CanonicalResult.bets.rounds.round_id", "fail", note))
        for rnd in bet.rounds:
            if rnd.round_type not in {"basic", "free"}:
                note = f"bet {bet.bet_id} round {rnd.round_id} round_type must be 'basic' or 'free'"
                issues.append(note)
                structural_checks.append(_check("CanonicalResult.bets.rounds.round_type", "fail", note))
            if rnd.roll_count < 0:
                note = f"bet {bet.bet_id} round {rnd.round_id} roll_count must be non-negative"
                issues.append(note)
                structural_checks.append(_check("CanonicalResult.bets.rounds.roll_count", "fail", note))
            if rnd.round_win_amount < 0.0:
                note = f"bet {bet.bet_id} round {rnd.round_id} round_win_amount must be non-negative"
                issues.append(note)
                structural_checks.append(_check("CanonicalResult.bets.rounds.round_win_amount", "fail", note))
            if rnd.roll_count != len(rnd.rolls):
                note = f"bet {bet.bet_id} round {rnd.round_id} roll_count does not match len(rolls)"
                issues.append(note)
                structural_checks.append(_check("CanonicalResult.bets.rounds.roll_count", "fail", note))
            roll_ids = [roll.roll_id for roll in rnd.rolls]
            if roll_ids != sorted(roll_ids) or len(roll_ids) != len(set(roll_ids)):
                note = f"bet {bet.bet_id} round {rnd.round_id} roll_id values must be strictly ascending"
                issues.append(note)
                structural_checks.append(_check("CanonicalResult.bets.rounds.rolls.roll_id", "fail", note))
            for roll_index, roll in enumerate(rnd.rolls):
                expected_roll_type = "initial" if roll_index == 0 else "cascade"
                if roll.roll_type not in {"initial", "cascade"}:
                    note = f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} roll_type must be 'initial' or 'cascade'"
                    issues.append(note)
                    structural_checks.append(_check("CanonicalResult.bets.rounds.rolls.roll_type", "fail", note))
                elif roll.roll_type != expected_roll_type:
                    note = f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} roll_type must be '{expected_roll_type}'"
                    issues.append(note)
                    structural_checks.append(_check("CanonicalResult.bets.rounds.rolls.roll_type", "fail", note))
                if roll.roll_win_amount < 0.0:
                    note = f"bet {bet.bet_id} round {rnd.round_id} roll {roll.roll_id} roll_win_amount must be non-negative"
                    issues.append(note)
                    structural_checks.append(_check("CanonicalResult.bets.rounds.rolls.roll_win_amount", "fail", note))
            if rnd.round_multiplier_increment == 0 and not _almost_equal(rnd.round_total_multiplier, 1.0):
                note = f"bet {bet.bet_id} round {rnd.round_id} round_total_multiplier must be 1 when round_multiplier_increment is 0"
                issues.append(note)
                structural_checks.append(_check("CanonicalResult.bets.rounds.round_total_multiplier", "fail", note))
            if rnd.round_multiplier_increment > 0 and not _almost_equal(
                rnd.round_total_multiplier,
                rnd.carried_multiplier + rnd.round_multiplier_increment,
            ):
                note = f"bet {bet.bet_id} round {rnd.round_id} round_total_multiplier does not equal carried_multiplier plus round_multiplier_increment"
                issues.append(note)
                structural_checks.append(_check("CanonicalResult.bets.rounds.round_total_multiplier", "fail", note))
            expected_round_win = rnd.base_symbol_win_amount * rnd.round_total_multiplier + rnd.scatter_win_amount
            if not _almost_equal(rnd.round_win_amount, expected_round_win):
                note = f"bet {bet.bet_id} round {rnd.round_id} round_win_amount does not equal base_symbol_win_amount times round_total_multiplier plus scatter_win_amount"
                issues.append(note)
                structural_checks.append(_check("CanonicalResult.bets.rounds.round_win_amount", "fail", note))
        if not _almost_equal(bet.bet_win_amount, sum(rnd.round_win_amount for rnd in bet.rounds)):
            note = f"bet {bet.bet_id} bet_win_amount does not equal sum(round_win_amount)"
            issues.append(note)
            structural_checks.append(_check("CanonicalResult.bets.bet_win_amount", "fail", note))
        expected_basic_win = sum(rnd.round_win_amount for rnd in bet.rounds if rnd.round_type == "basic")
        expected_free_win = sum(rnd.round_win_amount for rnd in bet.rounds if rnd.round_type == "free")
        if not _almost_equal(bet.basic_win_amount, expected_basic_win):
            note = f"bet {bet.bet_id} basic_win_amount does not equal sum(basic round_win_amount)"
            issues.append(note)
            structural_checks.append(_check("CanonicalResult.bets.basic_win_amount", "fail", note))
        if not _almost_equal(bet.free_win_amount, expected_free_win):
            note = f"bet {bet.bet_id} free_win_amount does not equal sum(free round_win_amount)"
            issues.append(note)
            structural_checks.append(_check("CanonicalResult.bets.free_win_amount", "fail", note))
        if not _almost_equal(bet.bet_win_amount, bet.basic_win_amount + bet.free_win_amount):
            note = f"bet {bet.bet_id} bet_win_amount does not equal basic_win_amount plus free_win_amount"
            issues.append(note)
            structural_checks.append(_check("CanonicalResult.bets.bet_win_amount", "fail", note))
    if not structural_checks:
        structural_checks.append(_check("CanonicalResult.minimal_structural_checks", "pass", "minimal structural checks passed"))
    return _report(issues=issues, structural_checks=structural_checks, meta=meta)
