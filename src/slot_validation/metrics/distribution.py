from __future__ import annotations


FIXED_BINS: tuple[str, ...] = ("0", "(0,1]", "(1,5]", "(5,10]", "(10,+inf)")


def build_win_distribution(win_values: list[float]) -> dict[str, int]:
	bins = {name: 0 for name in FIXED_BINS}
	for value in win_values:
		if value <= 0:
			bins["0"] += 1
		elif value <= 1:
			bins["(0,1]"] += 1
		elif value <= 5:
			bins["(1,5]"] += 1
		elif value <= 10:
			bins["(5,10]"] += 1
		else:
			bins["(10,+inf)"] += 1
	return bins


def quantile(values: list[float], q: float) -> float:
	if not values:
		return 0.0
	if q < 0 or q > 1:
		raise ValueError("q must be in [0, 1]")
	sorted_values = sorted(values)
	idx = int((len(sorted_values) - 1) * q)
	return float(sorted_values[idx])
