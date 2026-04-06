from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class DeterministicRNG:
	seed: int

	def __post_init__(self) -> None:
		self._random = random.Random(self.seed)

	def randint(self, low: int, high: int) -> int:
		return self._random.randint(low, high)

	def shuffle(self, values: list[int]) -> None:
		self._random.shuffle(values)

	def weighted_index(self, weights: tuple[int, ...]) -> int:
		if not weights:
			raise ValueError("weights must not be empty")
		total = sum(weights)
		if total <= 0:
			raise ValueError("weights total must be > 0")

		pick = self._random.uniform(0.0, float(total))
		acc = 0.0
		for idx, weight in enumerate(weights):
			acc += float(weight)
			if pick <= acc:
				return idx
		return len(weights) - 1

	def choice_weighted(self, values: tuple[int, ...], weights: tuple[int, ...]) -> int:
		return values[self.weighted_index(weights)]
