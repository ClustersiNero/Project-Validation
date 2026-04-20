from validation.config.simulation_config import normalize_simulation_config
from validation.engine.engine import run_engine
from validation.engine.rng import RNG

_RAW_CONFIG = {
    "seed": 0,
    "mode_id": 1,
    "bet_count": 2,
    "paytable": {
        symbol_id: {"symbol_name": f"symbol_{symbol_id}", "symbol_type": "regular", "payouts": {}}
        for symbol_id in range(1, 13)
    },
    "strip_sets": {
        1: {strip_id: [strip_id] for strip_id in range(1, 7)},
        2: {strip_id: [strip_id + 6] for strip_id in range(1, 7)},
    },
    "implementation_config": {
        1: {
            "basic": {
                "round_strip_set_weights": [1, 1],
                "round_multiplier_profile_weights": [1],
            },
            "free": {
                "round_strip_set_weights": [1, 0],
                "round_multiplier_profile_weights": [1],
            },
        },
    },
    "multiplier_data": {
        "value": [2],
        "weight": {
            1: [1],
        },
    },
}


def _build(seed: int):
    config = normalize_simulation_config(_RAW_CONFIG)
    rng = RNG(seed=seed)
    return run_engine(config, rng)


def test_same_seed_produces_identical_engine_execution():
    result_a = _build(seed=42)
    result_b = _build(seed=42)
    for bet_a, bet_b in zip(result_a.bets, result_b.bets):
        for rnd_a, rnd_b in zip(bet_a.rounds, bet_b.rounds):
            strip_ids_a = [r.strip_set_id for r in rnd_a.rolls]
            strip_ids_b = [r.strip_set_id for r in rnd_b.rolls]
            assert strip_ids_a == strip_ids_b


def test_different_seeds_can_differ():
    results = {
        _build(seed=s).bets[0].rounds[0].rolls[0].strip_set_id
        for s in range(20)
    }
    assert len(results) > 1, "expected at least two distinct outcomes across 20 seeds"
