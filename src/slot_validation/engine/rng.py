from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class DeterministicRNG:
	"""Seeded RNG wrapper used across engine components."""

	seed: int

	def __post_init__(self) -> None:
		self._random = random.Random(self.seed)

	def randint(self, a: int, b: int) -> int:
		return self._random.randint(a, b)

	def random(self) -> float:
		return self._random.random()

	def shuffle(self, values: list[int]) -> None:
		self._random.shuffle(values)

	def weighted_index(self, weights: tuple[int, ...]) -> int:
		if not weights:
			raise ValueError("weights must not be empty")
		total = sum(weights)
		if total <= 0:
			raise ValueError("weights total must be > 0")

		pick = self._random.uniform(0.0, float(total))
		running = 0.0
		for idx, weight in enumerate(weights):
			running += weight
			if pick <= running:
				return idx
		return len(weights) - 1

	def choice_from_population(self, population: tuple[int, ...], weights: tuple[int, ...]) -> int:
		idx = self.weighted_index(weights)
		return population[idx]
