from configs.game import olympus_mini
from validation.api import run
from validation.core.types import PipelineResult


def test_pipeline_smoke():
    result = run(olympus_mini)

    assert isinstance(result, PipelineResult)

    # canonical structure
    assert len(result.canonical_result.bets) == 1
    assert len(result.canonical_result.bets[0].rounds) == 2
    assert len(result.canonical_result.bets[0].rounds[0].rolls) == 2
    assert len(result.canonical_result.bets[0].rounds[1].rolls) == 2

    # round ids
    assert result.canonical_result.bets[0].rounds[0].round_id == 0
    assert result.canonical_result.bets[0].rounds[1].round_id == 1

    # canonical values
    assert result.canonical_result.bets[0].bet_win_amount == 3.0
    assert result.canonical_result.bets[0].round_count == 2
    assert result.canonical_result.bets[0].rounds[0].round_win_amount == 1.0
    assert result.canonical_result.bets[0].rounds[1].round_win_amount == 2.0

    # metrics
    assert result.metrics_bundle.bet_count == 1
    assert result.metrics_bundle.round_count == 2
    assert result.metrics_bundle.roll_count == 4
    assert result.metrics_bundle.total_bet_win_amount == 3.0
    assert result.metrics_bundle.total_round_win_amount == 3.0
    assert result.metrics_bundle.total_roll_win_amount == 3.0

    # validation
    assert result.canonical_validation.is_valid is True
    assert result.canonical_validation.issues == []
    assert result.metrics_validation.is_valid is True
    assert result.metrics_validation.issues == []
