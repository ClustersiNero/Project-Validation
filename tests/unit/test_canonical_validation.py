from validation.canonical.schema import (
    BetRecord,
    CanonicalResult,
    RollRecord,
    RoundRecord,
    SimulationMetadata,
)
from validation.core.validation import validate_canonical


def _valid_result() -> CanonicalResult:
    column_strip_ids = [1, 2, 3, 4, 5, 6]
    rolls = [
        RollRecord(
            roll_id=0,
            roll_win_amount=1.0,
            roll_type="initial",
            column_strip_ids=column_strip_ids,
            refill_start_indices=[0, 0, 0, 0, 0, 0],
            refill_end_indices=[1, 1, 1, 1, 1, 1],
        ),
        RollRecord(
            roll_id=1,
            roll_win_amount=2.0,
            roll_type="cascade",
            column_strip_ids=column_strip_ids,
            refill_start_indices=[1, 1, 1, 1, 1, 1],
            refill_end_indices=[2, 2, 2, 2, 2, 2],
        ),
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
        config_id="simulation_config",
        config_version="0.1.0",
        engine_version="engine.v1",
        schema_version="canonical.v1",
        mode="normal",
        seed=1,
        bet_amount=1.0,
        bet_level=1.0,
        total_bets=1,
        timestamp="1970-01-01T00:00:00Z",
    )
    return CanonicalResult(simulation_metadata=metadata, bets=[bet])


def test_valid_canonical_result_passes():
    report = validate_canonical(_valid_result())

    assert report.is_valid is True
    assert report.issues == []


def test_total_bets_mismatch_fails():
    result = _valid_result()
    result.simulation_metadata.total_bets = 2

    report = validate_canonical(result)

    assert report.is_valid is False
    assert "simulation_metadata.total_bets does not match len(bets)" in report.issues


def test_basic_win_aggregation_mismatch_fails():
    result = _valid_result()
    result.bets[0].basic_win_amount = 0.0

    report = validate_canonical(result)

    assert report.is_valid is False
    assert "bet 0 basic_win_amount does not equal sum(basic round_win_amount)" in report.issues


def test_roll_type_sequence_mismatch_fails():
    result = _valid_result()
    result.bets[0].rounds[0].rolls[1].roll_type = "initial"

    report = validate_canonical(result)

    assert report.is_valid is False
    assert "bet 0 round 0 roll 1 roll_type must be 'cascade'" in report.issues


def test_round_multiplier_without_increment_fails():
    result = _valid_result()
    result.bets[0].rounds[0].round_total_multiplier = 2.0
    result.bets[0].rounds[0].round_win_amount = 6.0
    result.bets[0].bet_win_amount = 6.0
    result.bets[0].basic_win_amount = 6.0

    report = validate_canonical(result)

    assert report.is_valid is False
    assert "bet 0 round 0 round_total_multiplier must be 1 when round_multiplier_increment is 0" in report.issues


def test_roll_refill_index_length_mismatch_fails():
    result = _valid_result()
    result.bets[0].rounds[0].rolls[0].refill_start_indices = [0, 0, 0]

    report = validate_canonical(result)

    assert report.is_valid is False
    assert "bet 0 round 0 roll 0 refill_start_indices must have length 6" in report.issues


def test_cascade_refill_start_must_match_previous_refill_end():
    result = _valid_result()
    result.bets[0].rounds[0].rolls[1].refill_start_indices = [9, 9, 9, 9, 9, 9]

    report = validate_canonical(result)

    assert report.is_valid is False
    assert (
        "bet 0 round 0 roll 1 refill_start_indices must equal previous roll refill_end_indices"
        in report.issues
    )


def test_basic_scatter_award_mismatch_fails():
    result = _valid_result()
    result.bets[0].rounds[0].round_scatter_increment = 4
    result.bets[0].rounds[0].award_free_rounds = 0

    report = validate_canonical(result)

    assert report.is_valid is False
    assert (
        "bet 0 round 0 award_free_rounds does not match round_type and round_scatter_increment"
        in report.issues
    )


def test_free_scatter_award_mismatch_fails():
    result = _valid_result()
    result.bets[0].rounds[0].round_type = "free"
    result.bets[0].rounds[0].round_scatter_increment = 3
    result.bets[0].rounds[0].award_free_rounds = 0

    report = validate_canonical(result)

    assert report.is_valid is False
    assert (
        "bet 0 round 0 award_free_rounds does not match round_type and round_scatter_increment"
        in report.issues
    )


def test_no_scatter_award_mismatch_fails():
    result = _valid_result()
    result.bets[0].rounds[0].round_scatter_increment = 3
    result.bets[0].rounds[0].award_free_rounds = 15

    report = validate_canonical(result)

    assert report.is_valid is False
    assert (
        "bet 0 round 0 award_free_rounds does not match round_type and round_scatter_increment"
        in report.issues
    )


def test_free_round_carried_multiplier_continuity_mismatch_fails():
    result = _valid_result()
    first_free_round = RoundRecord(
        round_id=1,
        round_type="free",
        round_win_amount=10.0,
        base_symbol_win_amount=1.0,
        carried_multiplier=0.0,
        round_multiplier_increment=10.0,
        round_total_multiplier=10.0,
        roll_count=1,
        rolls=[
            RollRecord(
                roll_id=0,
                roll_win_amount=1.0,
                roll_type="initial",
                column_strip_ids=[1, 2, 3, 4, 5, 6],
                refill_start_indices=[0, 0, 0, 0, 0, 0],
                refill_end_indices=[1, 1, 1, 1, 1, 1],
            ),
        ],
    )
    second_free_round = RoundRecord(
        round_id=2,
        round_type="free",
        round_win_amount=1.0,
        base_symbol_win_amount=1.0,
        carried_multiplier=0.0,
        round_total_multiplier=1.0,
        roll_count=1,
        rolls=[
            RollRecord(
                roll_id=0,
                roll_win_amount=1.0,
                roll_type="initial",
                column_strip_ids=[1, 2, 3, 4, 5, 6],
                refill_start_indices=[0, 0, 0, 0, 0, 0],
                refill_end_indices=[1, 1, 1, 1, 1, 1],
            ),
        ],
    )
    result.bets[0].rounds.extend([first_free_round, second_free_round])
    result.bets[0].round_count = 3
    result.bets[0].bet_win_amount = 14.0
    result.bets[0].free_win_amount = 11.0

    report = validate_canonical(result)

    assert report.is_valid is False
    assert (
        "bet 0 round 2 carried_multiplier does not match prior free round carry state"
        in report.issues
    )
