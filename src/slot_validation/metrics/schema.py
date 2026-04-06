from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricsBundle:
	empirical_rtp: float
	hit_frequency: float
	avg_win_per_spin: float
	max_single_spin_win: float
	top_1pct_payout_share: float
