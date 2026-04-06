from __future__ import annotations

from slot_validation.metrics.distribution import top_share


def top_1pct_share(values: list[float]) -> float:
	return top_share(values, top_fraction=0.01)
