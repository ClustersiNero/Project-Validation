from validation.metrics.types import MetricsBundle, StatisticalMetric
from validation.validation.types import ValidationReport


def validate_metrics_impl(metrics: MetricsBundle) -> ValidationReport:
    issues: list[str] = []
    if metrics.meta.total_bets < 0:
        issues.append("MetricsBundle.meta.total_bets must be non-negative")
    if metrics.round_metrics.core.round_count < 0:
        issues.append("MetricsBundle.round_metrics.core.round_count must be non-negative")
    if metrics.round_metrics.core.basic_round_count < 0:
        issues.append("MetricsBundle.round_metrics.core.basic_round_count must be non-negative")
    if metrics.round_metrics.core.free_round_count < 0:
        issues.append("MetricsBundle.round_metrics.core.free_round_count must be non-negative")
    if metrics.roll_metrics.core.roll_count < 0:
        issues.append("MetricsBundle.roll_metrics.core.roll_count must be non-negative")
    if metrics.roll_metrics.core.initial_roll_count < 0:
        issues.append("MetricsBundle.roll_metrics.core.initial_roll_count must be non-negative")
    if metrics.roll_metrics.core.cascade_roll_count < 0:
        issues.append("MetricsBundle.roll_metrics.core.cascade_roll_count must be non-negative")
    if metrics.meta.total_bet_amount < 0.0:
        issues.append("MetricsBundle.meta.total_bet_amount must be non-negative")
    if metrics.meta.total_bet_win_amount < 0.0:
        issues.append("MetricsBundle.meta.total_bet_win_amount must be non-negative")
    if metrics.round_metrics.core.total_round_win_amount < 0.0:
        issues.append("MetricsBundle.round_metrics.core.total_round_win_amount must be non-negative")
    if metrics.roll_metrics.core.total_roll_win_amount < 0.0:
        issues.append("MetricsBundle.roll_metrics.core.total_roll_win_amount must be non-negative")
    _validate_statistical_metric(
        metrics.bet_metrics.core.empirical_rtp,
        "MetricsBundle.bet_metrics.core.empirical_rtp",
        issues,
    )
    _validate_statistical_metric(
        metrics.bet_metrics.core.avg_bet_win_amount,
        "MetricsBundle.bet_metrics.core.avg_bet_win_amount",
        issues,
    )
    _validate_statistical_metric(
        metrics.bet_metrics.core.bet_hit_frequency,
        "MetricsBundle.bet_metrics.core.bet_hit_frequency",
        issues,
    )
    _validate_statistical_metric(
        metrics.bet_metrics.core.free_containing_bet_frequency,
        "MetricsBundle.bet_metrics.core.free_containing_bet_frequency",
        issues,
    )
    _validate_statistical_metric(
        metrics.bet_metrics.core.basic_rtp,
        "MetricsBundle.bet_metrics.core.basic_rtp",
        issues,
    )
    _validate_statistical_metric(
        metrics.bet_metrics.core.free_rtp,
        "MetricsBundle.bet_metrics.core.free_rtp",
        issues,
    )
    _validate_statistical_metric(
        metrics.bet_metrics.structure.avg_rounds_per_bet,
        "MetricsBundle.bet_metrics.structure.avg_rounds_per_bet",
        issues,
    )
    _validate_statistical_metric(
        metrics.bet_metrics.structure.avg_free_rounds_per_bet,
        "MetricsBundle.bet_metrics.structure.avg_free_rounds_per_bet",
        issues,
    )
    _validate_statistical_metric(
        metrics.bet_metrics.structure.avg_rolls_per_bet,
        "MetricsBundle.bet_metrics.structure.avg_rolls_per_bet",
        issues,
    )
    _validate_statistical_metric(
        metrics.round_metrics.core.avg_round_win_amount,
        "MetricsBundle.round_metrics.core.avg_round_win_amount",
        issues,
    )
    _validate_statistical_metric(
        metrics.round_metrics.core.round_hit_frequency,
        "MetricsBundle.round_metrics.core.round_hit_frequency",
        issues,
    )
    _validate_statistical_metric(
        metrics.round_metrics.core.free_round_award_frequency,
        "MetricsBundle.round_metrics.core.free_round_award_frequency",
        issues,
    )
    _validate_statistical_metric(
        metrics.round_metrics.core.avg_free_rounds_awarded,
        "MetricsBundle.round_metrics.core.avg_free_rounds_awarded",
        issues,
    )
    _validate_round_partition_metrics(
        metrics.round_metrics.basic,
        "MetricsBundle.round_metrics.basic",
        issues,
    )
    _validate_round_partition_metrics(
        metrics.round_metrics.free,
        "MetricsBundle.round_metrics.free",
        issues,
    )
    _validate_statistical_metric(
        metrics.roll_metrics.core.avg_roll_win_amount,
        "MetricsBundle.roll_metrics.core.avg_roll_win_amount",
        issues,
    )
    _validate_statistical_metric(
        metrics.roll_metrics.core.roll_hit_frequency,
        "MetricsBundle.roll_metrics.core.roll_hit_frequency",
        issues,
    )
    _validate_statistical_metric(
        metrics.roll_metrics.core.roll_type_distribution.initial,
        "MetricsBundle.roll_metrics.core.roll_type_distribution.initial",
        issues,
    )
    _validate_statistical_metric(
        metrics.roll_metrics.core.roll_type_distribution.cascade,
        "MetricsBundle.roll_metrics.core.roll_type_distribution.cascade",
        issues,
    )
    _validate_roll_partition_metrics(
        metrics.roll_metrics.initial,
        "MetricsBundle.roll_metrics.initial",
        issues,
    )
    _validate_roll_partition_metrics(
        metrics.roll_metrics.cascade,
        "MetricsBundle.roll_metrics.cascade",
        issues,
    )
    return ValidationReport(is_valid=len(issues) == 0, issues=issues)


def _validate_statistical_metric(metric: StatisticalMetric, path: str, issues: list[str]) -> None:
    if metric.sample_size < 0:
        issues.append(f"{path}.sample_size must be non-negative")
    if metric.observed is not None and metric.observed < 0.0:
        issues.append(f"{path}.observed must be non-negative")
    if metric.standard_deviation is not None and metric.standard_deviation < 0.0:
        issues.append(f"{path}.standard_deviation must be non-negative")


def _validate_round_partition_metrics(metrics, path: str, issues: list[str]) -> None:
    if metrics.round_count < 0:
        issues.append(f"{path}.round_count must be non-negative")
    _validate_statistical_metric(metrics.avg_round_win_amount, f"{path}.avg_round_win_amount", issues)
    _validate_statistical_metric(metrics.round_hit_frequency, f"{path}.round_hit_frequency", issues)
    _validate_statistical_metric(metrics.avg_free_rounds_awarded, f"{path}.avg_free_rounds_awarded", issues)


def _validate_roll_partition_metrics(metrics, path: str, issues: list[str]) -> None:
    if metrics.roll_count < 0:
        issues.append(f"{path}.roll_count must be non-negative")
    _validate_statistical_metric(metrics.avg_roll_win_amount, f"{path}.avg_roll_win_amount", issues)
    _validate_statistical_metric(metrics.roll_hit_frequency, f"{path}.roll_hit_frequency", issues)
