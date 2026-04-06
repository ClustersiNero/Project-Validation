from __future__ import annotations

import math


def top_1pct_win_share(win_values: list[float]) -> float:
	if not win_values:
		return 0.0
	total_win = sum(win_values)
	if total_win <= 0:
		return 0.0
	k = max(1, int(math.ceil(len(win_values) * 0.01)))
	top_sum = sum(sorted(win_values, reverse=True)[:k])
	return float(top_sum / total_win)


def extreme_win_freq(win_values: list[float], p99: float) -> float:
	if not win_values:
		return 0.0
	extreme_count = sum(1 for value in win_values if value >= p99)
	return float(extreme_count / len(win_values))
