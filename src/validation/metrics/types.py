from dataclasses import dataclass, field


@dataclass
class StatisticalMetric:
    observed: float | None = None
    standard_deviation: float | None = None
    sample_size: int = 0


@dataclass
class MetricsMeta:
    simulation_id: str = ""
    config_id: str = ""
    config_version: str = ""
    engine_version: str = ""
    schema_version: str = ""
    mode: str = ""
    seed: int = 0
    bet_amount: float = 0.0
    bet_level: float = 0.0
    total_bets: int = 0
    timestamp: str = ""
    total_bet_amount: float = 0.0
    total_bet_win_amount: float = 0.0


@dataclass
class BetCoreMetrics:
    # Validation-facing outcome metrics.
    empirical_rtp: StatisticalMetric = field(default_factory=StatisticalMetric)
    avg_bet_win_amount: StatisticalMetric = field(default_factory=StatisticalMetric)
    bet_hit_frequency: StatisticalMetric = field(default_factory=StatisticalMetric)
    free_containing_bet_frequency: StatisticalMetric = field(default_factory=StatisticalMetric)
    basic_rtp: StatisticalMetric = field(default_factory=StatisticalMetric)
    free_rtp: StatisticalMetric = field(default_factory=StatisticalMetric)


@dataclass
class BetStructureMetrics:
    # Structure / tuning-facing flow metrics.
    avg_rounds_per_bet: StatisticalMetric = field(default_factory=StatisticalMetric)
    avg_free_rounds_per_bet: StatisticalMetric = field(default_factory=StatisticalMetric)
    avg_rolls_per_bet: StatisticalMetric = field(default_factory=StatisticalMetric)


@dataclass
class BetMetrics:
    core: BetCoreMetrics = field(default_factory=BetCoreMetrics)
    structure: BetStructureMetrics = field(default_factory=BetStructureMetrics)


@dataclass
class RoundCoreMetrics:
    # Validation-facing round totals and hit rate.
    round_count: int = 0
    basic_round_count: int = 0
    free_round_count: int = 0
    total_round_win_amount: float = 0.0
    avg_round_win_amount: StatisticalMetric = field(default_factory=StatisticalMetric)
    round_hit_frequency: StatisticalMetric = field(default_factory=StatisticalMetric)

    # Structure / tuning-facing free-award flow metrics.
    free_round_award_frequency: StatisticalMetric = field(default_factory=StatisticalMetric)
    avg_free_rounds_awarded: StatisticalMetric = field(default_factory=StatisticalMetric)


@dataclass
class RoundPartitionMetrics:
    # Structure / tuning-facing partition metrics.
    round_count: int = 0
    avg_round_win_amount: StatisticalMetric = field(default_factory=StatisticalMetric)
    round_hit_frequency: StatisticalMetric = field(default_factory=StatisticalMetric)
    avg_free_rounds_awarded: StatisticalMetric = field(default_factory=StatisticalMetric)


@dataclass
class RoundMetrics:
    core: RoundCoreMetrics = field(default_factory=RoundCoreMetrics)
    basic: RoundPartitionMetrics = field(default_factory=RoundPartitionMetrics)
    free: RoundPartitionMetrics = field(default_factory=RoundPartitionMetrics)


@dataclass
class RollTypeDistribution:
    initial: StatisticalMetric = field(default_factory=StatisticalMetric)
    cascade: StatisticalMetric = field(default_factory=StatisticalMetric)


@dataclass
class RollCoreMetrics:
    # Validation-facing roll totals and hit rate.
    roll_count: int = 0
    initial_roll_count: int = 0
    cascade_roll_count: int = 0
    total_roll_win_amount: float = 0.0
    avg_roll_win_amount: StatisticalMetric = field(default_factory=StatisticalMetric)
    roll_hit_frequency: StatisticalMetric = field(default_factory=StatisticalMetric)

    # Structure / tuning-facing roll progression mix.
    roll_type_distribution: RollTypeDistribution = field(default_factory=RollTypeDistribution)


@dataclass
class RollPartitionMetrics:
    # Structure / tuning-facing partition metrics.
    roll_count: int = 0
    avg_roll_win_amount: StatisticalMetric = field(default_factory=StatisticalMetric)
    roll_hit_frequency: StatisticalMetric = field(default_factory=StatisticalMetric)


@dataclass
class RollMetrics:
    core: RollCoreMetrics = field(default_factory=RollCoreMetrics)
    initial: RollPartitionMetrics = field(default_factory=RollPartitionMetrics)
    cascade: RollPartitionMetrics = field(default_factory=RollPartitionMetrics)


@dataclass
class MetricsBundle:
    meta: MetricsMeta = field(default_factory=MetricsMeta)
    bet_metrics: BetMetrics = field(default_factory=BetMetrics)
    round_metrics: RoundMetrics = field(default_factory=RoundMetrics)
    roll_metrics: RollMetrics = field(default_factory=RollMetrics)
