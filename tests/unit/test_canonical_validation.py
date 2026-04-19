from validation.canonical.minimal_canonical import (
    BetRecord,
    CanonicalResult,
    RollRecord,
    RoundRecord,
    SimulationMetadata,
)
from validation.validation.minimal_validation import validate_canonical_impl


def _valid_result() -> CanonicalResult:
    rolls = [
        RollRecord(roll_id=0, roll_win_amount=1.0, roll_type="initial"),
        RollRecord(roll_id=1, roll_win_amount=2.0, roll_type="cascade"),
    ]
    round_ = RoundRecord(
        round_id=0,
        round_type="basic",
        round_win_amount=3.0,
        base_symbol_win_amount=3.0,
        round_total_multiplier=1.0,
        roll_count=2,
        round_final_state={},
        rolls=rolls,
    )
    bet = BetRecord(
        bet_id=0,
        bet_win_amount=3.0,
        basic_win_amount=3.0,
        free_win_amount=0.0,
        round_count=1,
        bet_final_state={},
        rounds=[round_],
    )
    metadata = SimulationMetadata(
        simulation_id="test",
        config_id="minimal_config",
        config_version="0.1.0",
        engine_version="minimal_engine.v1",
        schema_version="minimal_canonical.v1",
        mode="normal",
        seed=1,
        bet_amount=1.0,
        bet_level=1.0,
        total_bets=1,
        timestamp="1970-01-01T00:00:00Z",
    )
    return CanonicalResult(simulation_metadata=metadata, bets=[bet])


def test_valid_canonical_result_passes():
    report = validate_canonical_impl(_valid_result())

    assert report.is_valid is True
    assert report.issues == []


def test_total_bets_mismatch_fails():
    result = _valid_result()
    result.simulation_metadata.total_bets = 2

    report = validate_canonical_impl(result)

    assert report.is_valid is False
    assert "simulation_metadata.total_bets does not match len(bets)" in report.issues


def test_basic_win_aggregation_mismatch_fails():
    result = _valid_result()
    result.bets[0].basic_win_amount = 0.0

    report = validate_canonical_impl(result)

    assert report.is_valid is False
    assert "bet 0 basic_win_amount does not equal sum(basic round_win_amount)" in report.issues


def test_roll_type_sequence_mismatch_fails():
    result = _valid_result()
    result.bets[0].rounds[0].rolls[1].roll_type = "initial"

    report = validate_canonical_impl(result)

    assert report.is_valid is False
    assert "bet 0 round 0 roll 1 roll_type must be 'cascade'" in report.issues


def test_round_multiplier_without_increment_fails():
    result = _valid_result()
    result.bets[0].rounds[0].round_total_multiplier = 2.0
    result.bets[0].rounds[0].round_win_amount = 6.0
    result.bets[0].bet_win_amount = 6.0
    result.bets[0].basic_win_amount = 6.0

    report = validate_canonical_impl(result)

    assert report.is_valid is False
    assert "bet 0 round 0 round_total_multiplier must be 1 when round_multiplier_increment is 0" in report.issues
