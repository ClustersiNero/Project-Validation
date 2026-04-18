import random


class RNG:
    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def next_int(self, low: int, high: int) -> int:
        """Return a random integer N such that low <= N <= high."""
        return self._rng.randint(low, high)

    def next_float(self) -> float:
        """Return a random float in [0.0, 1.0)."""
        return self._rng.random()
