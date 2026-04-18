from configs.game import olympus_mini
from validation.api import run


def test_pipeline_reproducibility_same_seed():
    result_a = run(olympus_mini)
    result_b = run(olympus_mini)

    bet_a = result_a.canonical_result.bets[0]
    bet_b = result_b.canonical_result.bets[0]

    rolls_a = [r.roll_win_amount for rnd in bet_a.rounds for r in rnd.rolls]
    rolls_b = [r.roll_win_amount for rnd in bet_b.rounds for r in rnd.rolls]

    assert rolls_a == rolls_b
