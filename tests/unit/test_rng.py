from validation.engine.rng import RNG


def test_same_seed_produces_identical_int_sequence():
    rng_a = RNG(seed=42)
    rng_b = RNG(seed=42)
    for _ in range(10):
        assert rng_a.next_int(0, 100) == rng_b.next_int(0, 100)


def test_same_seed_produces_identical_float_sequence():
    rng_a = RNG(seed=42)
    rng_b = RNG(seed=42)
    for _ in range(10):
        assert rng_a.next_float() == rng_b.next_float()
