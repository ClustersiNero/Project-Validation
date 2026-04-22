from validation.canonical.schema import (
    BetRecord,
    CanonicalResult,
    RollRecord,
    RoundRecord,
    SimulationMetadata,
)
from validation.metrics.metrics import compute_metrics_impl


def test_metrics_are_computed_from_canonical_only():
    result = CanonicalResult(
        simulation_metadata=SimulationMetadata(
            simulation_id="metrics-test",
            config_id="simulation_config",
            config_version="0.1.0",
            engine_version="engine.v1",
            schema_version="canonical.v1",
            mode="normal",
            seed=7,
            bet_amount=2.0,
            bet_level=1.0,
            total_bets=2,
            timestamp="1970-01-01T00:00:00Z",
        ),
        bets=[
            BetRecord(
                bet_id=0,
                bet_win_amount=4.0,
                basic_win_amount=3.0,
                free_win_amount=1.0,
                round_count=1,
                rounds=[
                    RoundRecord(
                        round_id=0,
                        round_type="basic",
                        round_win_amount=4.0,
                        roll_count=1,
                        rolls=[RollRecord(roll_id=0, roll_type="initial", roll_win_amount=4.0)],
                    ),
                ],
            ),
            BetRecord(
                bet_id=1,
                bet_win_amount=0.0,
                basic_win_amount=0.0,
                free_win_amount=0.0,
                round_count=1,
                rounds=[
                    RoundRecord(
                        round_id=0,
                        round_type="basic",
                        round_win_amount=0.0,
                        roll_count=1,
                        rolls=[RollRecord(roll_id=0, roll_type="initial", roll_win_amount=0.0)],
                    ),
                ],
            ),
        ],
    )

    metrics = compute_metrics_impl(result)

    assert metrics.meta.total_bets == 2
    assert metrics.meta.total_bet_amount == 4.0
    assert metrics.meta.total_bet_win_amount == 4.0
    assert metrics.bet_metrics.core.empirical_rtp.observed == 1.0
    assert metrics.bet_metrics.core.empirical_rtp.sample_size == 2
    assert metrics.bet_metrics.core.avg_bet_win_amount.observed == 2.0
    assert metrics.bet_metrics.core.bet_hit_frequency.observed == 0.5
    assert metrics.bet_metrics.core.free_containing_bet_frequency.observed == 0.0
    assert metrics.bet_metrics.core.basic_rtp == 0.75
    assert metrics.bet_metrics.core.free_rtp == 0.25
    assert metrics.round_metrics.core.round_count == 2
    assert metrics.round_metrics.core.basic_round_count == 2
    assert metrics.round_metrics.core.free_round_count == 0
    assert metrics.round_metrics.core.avg_round_win_amount.observed == 2.0
    assert metrics.round_metrics.core.free_award_frequency.observed == 0.0
    assert metrics.round_metrics.core.avg_free_rounds_awarded.observed == 0.0
    assert metrics.round_metrics.basic.round_count == 2
    assert metrics.round_metrics.basic.avg_round_win_amount.observed == 2.0
    assert metrics.round_metrics.basic.round_hit_frequency.observed == 0.5
    assert metrics.round_metrics.basic.avg_free_rounds_awarded.observed == 0.0
    assert metrics.round_metrics.free.round_count == 0
    assert metrics.round_metrics.free.avg_round_win_amount.observed is None
    assert metrics.round_metrics.free.round_hit_frequency.observed is None
    assert metrics.round_metrics.free.avg_free_rounds_awarded.observed is None
    assert metrics.roll_metrics.core.roll_count == 2
    assert metrics.roll_metrics.core.avg_roll_win_amount.observed == 2.0
    assert metrics.roll_metrics.core.roll_hit_frequency.observed == 0.5
    assert metrics.roll_metrics.core.roll_type_distribution.initial == 1.0
    assert metrics.roll_metrics.core.roll_type_distribution.cascade == 0.0
    assert metrics.roll_metrics.initial.roll_count == 2
    assert metrics.roll_metrics.initial.avg_roll_win_amount.observed == 2.0
    assert metrics.roll_metrics.initial.roll_hit_frequency.observed == 0.5
    assert metrics.roll_metrics.cascade.roll_count == 0
    assert metrics.roll_metrics.cascade.avg_roll_win_amount.observed is None
    assert metrics.roll_metrics.cascade.roll_hit_frequency.observed is None


def test_metrics_describe_free_rounds_and_cascade_rolls():
    result = CanonicalResult(
        simulation_metadata=SimulationMetadata(
            simulation_id="metrics-free-test",
            config_id="simulation_config",
            config_version="0.1.0",
            engine_version="engine.v1",
            schema_version="canonical.v1",
            mode="normal",
            seed=11,
            bet_amount=1.0,
            bet_level=1.0,
            total_bets=2,
            timestamp="1970-01-01T00:00:00Z",
        ),
        bets=[
            BetRecord(
                bet_id=0,
                bet_win_amount=5.0,
                basic_win_amount=2.0,
                free_win_amount=3.0,
                round_count=2,
                rounds=[
                    RoundRecord(
                        round_id=0,
                        round_type="basic",
                        round_win_amount=2.0,
                        award_free_rounds=15,
                        roll_count=2,
                        rolls=[
                            RollRecord(roll_id=0, roll_type="initial", roll_win_amount=1.0),
                            RollRecord(roll_id=1, roll_type="cascade", roll_win_amount=1.0),
                        ],
                    ),
                    RoundRecord(
                        round_id=1,
                        round_type="free",
                        round_win_amount=3.0,
                        roll_count=1,
                        rolls=[RollRecord(roll_id=0, roll_type="initial", roll_win_amount=3.0)],
                    ),
                ],
            ),
            BetRecord(
                bet_id=1,
                bet_win_amount=0.0,
                basic_win_amount=0.0,
                free_win_amount=0.0,
                round_count=1,
                rounds=[
                    RoundRecord(
                        round_id=0,
                        round_type="basic",
                        round_win_amount=0.0,
                        roll_count=1,
                        rolls=[RollRecord(roll_id=0, roll_type="initial", roll_win_amount=0.0)],
                    ),
                ],
            ),
        ],
    )

    metrics = compute_metrics_impl(result)

    assert metrics.round_metrics.core.round_count == 3
    assert metrics.round_metrics.core.basic_round_count == 2
    assert metrics.round_metrics.core.free_round_count == 1
    assert metrics.round_metrics.core.free_award_frequency.observed == 1 / 3
    assert metrics.round_metrics.core.avg_free_rounds_awarded.observed == 5.0
    assert metrics.round_metrics.basic.round_count == 2
    assert metrics.round_metrics.basic.avg_round_win_amount.observed == 1.0
    assert metrics.round_metrics.basic.round_hit_frequency.observed == 0.5
    assert metrics.round_metrics.basic.avg_free_rounds_awarded.observed == 7.5
    assert metrics.round_metrics.free.round_count == 1
    assert metrics.round_metrics.free.avg_round_win_amount.observed == 3.0
    assert metrics.round_metrics.free.round_hit_frequency.observed == 1.0
    assert metrics.round_metrics.free.avg_free_rounds_awarded.observed == 0.0
    assert metrics.bet_metrics.core.free_containing_bet_frequency.observed == 0.5
    assert metrics.bet_metrics.core.free_containing_bet_frequency.sample_size == 2
    assert metrics.roll_metrics.core.roll_count == 4
    assert metrics.roll_metrics.core.roll_hit_frequency.observed == 0.75
    assert metrics.roll_metrics.core.roll_type_distribution.initial == 0.75
    assert metrics.roll_metrics.core.roll_type_distribution.cascade == 0.25
    assert metrics.roll_metrics.initial.roll_count == 3
    assert metrics.roll_metrics.initial.avg_roll_win_amount.observed == 4 / 3
    assert metrics.roll_metrics.initial.roll_hit_frequency.observed == 2 / 3
    assert metrics.roll_metrics.cascade.roll_count == 1
    assert metrics.roll_metrics.cascade.avg_roll_win_amount.observed == 1.0
    assert metrics.roll_metrics.cascade.roll_hit_frequency.observed == 1.0


def test_statistical_metric_small_sample_contract():
    empty_metrics = compute_metrics_impl(CanonicalResult())

    assert empty_metrics.bet_metrics.core.avg_bet_win_amount.observed is None
    assert empty_metrics.bet_metrics.core.avg_bet_win_amount.standard_deviation is None
    assert empty_metrics.bet_metrics.core.avg_bet_win_amount.sample_size == 0

    one_bet_result = CanonicalResult(
        simulation_metadata=SimulationMetadata(bet_amount=1.0, total_bets=1),
        bets=[
            BetRecord(
                bet_id=0,
                bet_win_amount=3.0,
                basic_win_amount=3.0,
                round_count=1,
                rounds=[
                    RoundRecord(
                        round_id=0,
                        round_type="basic",
                        round_win_amount=3.0,
                        roll_count=1,
                        rolls=[RollRecord(roll_id=0, roll_type="initial", roll_win_amount=3.0)],
                    ),
                ],
            ),
        ],
    )
    one_bet_metrics = compute_metrics_impl(one_bet_result)

    assert one_bet_metrics.bet_metrics.core.avg_bet_win_amount.observed == 3.0
    assert one_bet_metrics.bet_metrics.core.avg_bet_win_amount.standard_deviation is None
    assert one_bet_metrics.bet_metrics.core.avg_bet_win_amount.sample_size == 1
