from __future__ import annotations

import math


def top_share(values: list[float], top_fraction: float) -> float:
	if not values:
		return 0.0
	if top_fraction <= 0 or top_fraction > 1:
		raise ValueError("top_fraction must be in (0, 1]")

	total = sum(values)
	if total <= 0:
		return 0.0

	n = len(values)
	k = max(1, int(math.ceil(n * top_fraction)))
	top_sum = sum(sorted(values, reverse=True)[:k])
	return float(top_sum / total)
