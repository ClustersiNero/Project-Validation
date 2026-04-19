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

    # canonical internal consistency
    bet = result.canonical_result.bets[0]
    assert bet.round_count == 2
    assert bet.bet_win_amount == sum(rnd.round_win_amount for rnd in bet.rounds)
    for rnd in bet.rounds:
        assert rnd.round_win_amount == sum(r.roll_win_amount for r in rnd.rolls)

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
