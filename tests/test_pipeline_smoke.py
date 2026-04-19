from configs.game import olympus_mini
from validation.api import run
from validation.core.types import PipelineResult


def test_pipeline_smoke():
    result = run(olympus_mini)

    assert isinstance(result, PipelineResult)

    # canonical structure
    metadata = result.canonical_result.simulation_metadata
    assert metadata.simulation_id == "minimal-seed-42"
    assert metadata.config_id == "minimal_config"
    assert metadata.config_version == "0.1.0"
    assert metadata.engine_version == "minimal_engine.v1"
    assert metadata.schema_version == "canonical.v1"
    assert metadata.mode == "normal"
    assert metadata.seed == 42
    assert metadata.bet_amount == 1.0
    assert metadata.bet_level == 1.0
    assert metadata.total_bets == 1
    assert metadata.timestamp == "1970-01-01T00:00:00Z"

    assert len(result.canonical_result.bets) == 1
    assert len(result.canonical_result.bets[0].rounds) == 2
    assert len(result.canonical_result.bets[0].rounds[0].rolls) == 2
    assert len(result.canonical_result.bets[0].rounds[1].rolls) == 2

    # round ids
    assert result.canonical_result.bets[0].rounds[0].round_id == 0
    assert result.canonical_result.bets[0].rounds[1].round_id == 1

    # canonical internal consistency
    bet = result.canonical_result.bets[0]
    assert bet.round_count == 2
    assert bet.bet_win_amount == sum(rnd.round_win_amount for rnd in bet.rounds)
    assert bet.basic_win_amount == sum(rnd.round_win_amount for rnd in bet.rounds if rnd.round_type == "basic")
    assert bet.free_win_amount == sum(rnd.round_win_amount for rnd in bet.rounds if rnd.round_type == "free")
    assert bet.bet_win_amount == bet.basic_win_amount + bet.free_win_amount
    for rnd in bet.rounds:
        assert rnd.base_symbol_win_amount == sum(r.roll_win_amount for r in rnd.rolls)
        assert rnd.round_total_multiplier == 1.0
        assert rnd.round_win_amount == rnd.base_symbol_win_amount * rnd.round_total_multiplier + rnd.scatter_win_amount
        assert rnd.rolls[0].roll_type == "initial"
        assert [roll.roll_type for roll in rnd.rolls[1:]] == ["cascade"]

    # metrics counts
    assert result.metrics_bundle.bet_count == 1
    assert result.metrics_bundle.round_count == 2
    assert result.metrics_bundle.roll_count == 4

    # metrics totals consistent with canonical
    assert result.metrics_bundle.total_bet_win_amount == bet.bet_win_amount
    assert result.metrics_bundle.total_round_win_amount == sum(rnd.round_win_amount for rnd in bet.rounds)
    assert result.metrics_bundle.total_roll_win_amount == sum(
        r.roll_win_amount for rnd in bet.rounds for r in rnd.rolls
    )

    # validation
    assert result.canonical_validation.is_valid is True
    assert result.canonical_validation.issues == []
    assert result.metrics_validation.is_valid is True
    assert result.metrics_validation.issues == []
