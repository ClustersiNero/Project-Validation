from __future__ import annotations

from math import sqrt


def normal_ci_for_mean(*, mean: float, n: int, z: float = 1.96) -> tuple[float, float]:
	if n <= 0:
		raise ValueError("n must be > 0")

	# Conservative variance proxy when full sample variance is not passed in.
	variance_proxy = max(mean * (1.0 - mean), 1e-12)
	margin = z * sqrt(variance_proxy / n)
	return mean - margin, mean + margin
