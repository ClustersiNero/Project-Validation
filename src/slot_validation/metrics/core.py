from __future__ import annotations

from slot_validation.canonical.schema import CanonicalResult
from slot_validation.metrics.schema import MetricsBundle
from slot_validation.metrics.tail import top_1pct_share


def compute_metrics_from_canonical(result: CanonicalResult) -> MetricsBundle:
	spin_wins = [float(s.total_win) for s in result.spin_results]
	win_spins = sum(1 for amount in spin_wins if amount > 0)

	empirical_rtp = 0.0 if result.total_bet <= 0 else float(result.total_win / result.total_bet)
	hit_frequency = 0.0 if result.spins <= 0 else float(win_spins / result.spins)
	avg_win_per_spin = 0.0 if result.spins <= 0 else float(result.total_win / result.spins)
	max_single_spin_win = 0.0 if not spin_wins else max(spin_wins)

	return MetricsBundle(
		empirical_rtp=empirical_rtp,
		hit_frequency=hit_frequency,
		avg_win_per_spin=avg_win_per_spin,
		max_single_spin_win=max_single_spin_win,
		top_1pct_payout_share=top_1pct_share(spin_wins),
	)
