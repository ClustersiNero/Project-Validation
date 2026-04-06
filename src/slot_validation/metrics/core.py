from __future__ import annotations

from slot_validation.canonical.schema import CanonicalResult
from slot_validation.metrics.distribution import build_win_distribution, quantile
from slot_validation.metrics.schema import (
	CoreMetrics,
	DistributionMetrics,
	MetricsBundle,
	MetricsMeta,
	OptionalMetrics,
	TailMetrics,
)
from slot_validation.metrics.tail import extreme_win_freq, top_1pct_win_share


METRIC_VERSION = "1.0.0"


def _losing_streaks(win_values: list[float]) -> list[int]:
	streaks: list[int] = []
	current = 0
	for value in win_values:
		if value <= 0:
			current += 1
		elif current > 0:
			streaks.append(current)
			current = 0
	if current > 0:
		streaks.append(current)
	return streaks


def compute_metrics_from_canonical(result: CanonicalResult) -> MetricsBundle:
	win_values = [w.total_win for w in result.wagers]
	total_wagers = len(result.wagers)
	hit_count = sum(1 for w in result.wagers if w.total_win > 0)
	total_bet = result.summary.total_bet
	total_win = result.summary.total_win

	empirical_rtp = float(total_win / total_bet) if total_bet > 0 else 0.0
	hit_frequency = float(hit_count / total_wagers) if total_wagers > 0 else 0.0
	avg_win = float(total_win / total_wagers) if total_wagers > 0 else 0.0
	avg_win_when_hit = float(total_win / hit_count) if hit_count > 0 else 0.0

	p99 = quantile(win_values, 0.99)
	streaks = _losing_streaks(win_values)

	return MetricsBundle(
		meta=MetricsMeta(
			run_id=result.run.run_id,
			config_id=result.run.config_id,
			engine_version=result.run.engine_version,
			metric_version=METRIC_VERSION,
			total_wagers=total_wagers,
			total_bet=total_bet,
			total_win=total_win,
		),
		core=CoreMetrics(
			empirical_rtp=empirical_rtp,
			hit_frequency=hit_frequency,
			avg_win=avg_win,
			avg_win_when_hit=avg_win_when_hit,
		),
		distribution=DistributionMetrics(
			win_distribution=build_win_distribution(win_values),
			quantiles={
				"p50": quantile(win_values, 0.50),
				"p90": quantile(win_values, 0.90),
				"p95": quantile(win_values, 0.95),
				"p99": p99,
			},
			max_win=max(win_values) if win_values else 0.0,
		),
		tail=TailMetrics(
			top_1pct_win_share=top_1pct_win_share(win_values),
			extreme_win_freq_p99=extreme_win_freq(win_values, p99),
		),
		optional=OptionalMetrics(
			max_losing_streak=max(streaks) if streaks else 0,
			avg_losing_streak=(sum(streaks) / len(streaks)) if streaks else 0.0,
		),
	)
