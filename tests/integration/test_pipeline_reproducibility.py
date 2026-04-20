from configs.game import olympus_mini
from validation.api import run


def test_pipeline_reproducibility_same_seed():
    config = {
        "seed": 42,
        "mode_id": 1,
        "bet_count": 1,
        "simulation_mode": olympus_mini.SIMULATION_MODE,
        "paytable": olympus_mini.PAYTABLE,
        "multiplier_data": olympus_mini.MULTIPLIER_DATA,
        "strip_sets": olympus_mini.STRIP_SETS,
        "implementation_config": olympus_mini.IMPLEMENTATION_CONFIG,
    }
    result_a = run(config)
    result_b = run(config)

    bet_a = result_a.canonical_result.bets[0]
    bet_b = result_b.canonical_result.bets[0]

    rolls_a = [r.roll_win_amount for rnd in bet_a.rounds for r in rnd.rolls]
    rolls_b = [r.roll_win_amount for rnd in bet_b.rounds for r in rnd.rolls]

    assert rolls_a == rolls_b
