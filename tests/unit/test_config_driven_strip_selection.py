import pytest

from configs.game import olympus_mini
from validation.engine.minimal_engine import choose_round_strip_set_id, choose_weighted_id
from validation.engine.rng import RNG


def test_same_seed_produces_same_strip_set_id():
    rng_a = RNG(seed=42)
    rng_b = RNG(seed=42)

    selected_a = choose_round_strip_set_id(olympus_mini.IMPLEMENTATION_CONFIG, 1, "basic", rng_a)
    selected_b = choose_round_strip_set_id(olympus_mini.IMPLEMENTATION_CONFIG, 1, "basic", rng_b)

    assert selected_a == selected_b


def test_zero_weight_id_is_unreachable_when_other_weights_are_positive():
    selected_ids = {
        choose_round_strip_set_id(olympus_mini.IMPLEMENTATION_CONFIG, 1, "basic", RNG(seed=seed))
        for seed in range(100)
    }

    assert 3 not in selected_ids
    assert selected_ids <= {1, 2}


def test_index_to_id_mapping_returns_one_based_id():
    rng = RNG(seed=0)

    assert choose_weighted_id([0, 0, 1], rng) == 3


def test_all_zero_weights_raise():
    with pytest.raises(ValueError) as exc_info:
        choose_weighted_id([0, 0, 0], RNG(seed=0))

    assert str(exc_info.value) == "sum(weights) must be positive"
