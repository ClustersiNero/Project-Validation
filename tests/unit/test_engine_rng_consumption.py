from validation.config.minimal_config import normalize_minimal_config
from validation.engine.minimal_engine import build_minimal_canonical_result
from validation.engine.rng import RNG

_RAW_CONFIG = {
    "seed": 0,
    "rounds": [
        {"round_id": 0, "round_type": "basic", "roll_wins": [0.0, 1.0, 2.0]},
        {"round_id": 1, "round_type": "basic", "roll_wins": [0.5, 1.5]},
    ],
}


def _build(seed: int):
    config = normalize_minimal_config(_RAW_CONFIG)
    rng = RNG(seed=seed)
    return build_minimal_canonical_result(config, rng)


def test_same_seed_produces_identical_canonical_result():
    result_a = _build(seed=42)
    result_b = _build(seed=42)
    for bet_a, bet_b in zip(result_a.bets, result_b.bets):
        for rnd_a, rnd_b in zip(bet_a.rounds, bet_b.rounds):
            wins_a = [r.roll_win_amount for r in rnd_a.rolls]
            wins_b = [r.roll_win_amount for r in rnd_b.rolls]
            assert wins_a == wins_b


def test_different_seeds_can_differ():
    results = {_build(seed=s).bets[0].bet_win_amount for s in range(20)}
    assert len(results) > 1, "expected at least two distinct outcomes across 20 seeds"
