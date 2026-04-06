from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricsMeta:
	run_id: str
	config_id: str
	engine_version: str
	metric_version: str
	total_wagers: int
	total_bet: float
	total_win: float


@dataclass(frozen=True)
class CoreMetrics:
	empirical_rtp: float
	hit_frequency: float
	avg_win: float
	avg_win_when_hit: float


@dataclass(frozen=True)
class DistributionMetrics:
	win_distribution: dict[str, int]
	quantiles: dict[str, float]
	max_win: float


@dataclass(frozen=True)
class TailMetrics:
	top_1pct_win_share: float
	extreme_win_freq_p99: float


@dataclass(frozen=True)
class OptionalMetrics:
	max_losing_streak: int
	avg_losing_streak: float


@dataclass(frozen=True)
class MetricsBundle:
	meta: MetricsMeta
	core: CoreMetrics
	distribution: DistributionMetrics
	tail: TailMetrics
	optional: OptionalMetrics
