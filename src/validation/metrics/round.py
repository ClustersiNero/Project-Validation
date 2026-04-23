from validation.metrics.statistics import statistical_metric
from validation.metrics.types import RoundCoreMetrics, RoundMetrics, RoundPartitionMetrics


def compute_round_metrics(rounds: list) -> RoundMetrics:
    basic_rounds = [rnd for rnd in rounds if rnd.round_type == "basic"]
    free_rounds = [rnd for rnd in rounds if rnd.round_type == "free"]
    total_round_win_amount = sum(rnd.round_win_amount for rnd in rounds)

    return RoundMetrics(
        core=RoundCoreMetrics(
            round_count=len(rounds),
            basic_round_count=len(basic_rounds),
            free_round_count=len(free_rounds),
            total_round_win_amount=total_round_win_amount,
            avg_round_win_amount=statistical_metric([rnd.round_win_amount for rnd in rounds]),
            round_hit_frequency=statistical_metric(
                [1.0 if rnd.round_win_amount > 0 else 0.0 for rnd in rounds]
            ),
            free_round_award_frequency=statistical_metric(
                [1.0 if rnd.award_free_rounds > 0 else 0.0 for rnd in rounds]
            ),
            avg_free_rounds_awarded=statistical_metric(
                [float(rnd.award_free_rounds) for rnd in rounds]
            ),
        ),
        basic=compute_round_partition_metrics(basic_rounds),
        free=compute_round_partition_metrics(free_rounds),
    )


def compute_round_partition_metrics(rounds: list) -> RoundPartitionMetrics:
    return RoundPartitionMetrics(
        round_count=len(rounds),
        avg_round_win_amount=statistical_metric([rnd.round_win_amount for rnd in rounds]),
        round_hit_frequency=statistical_metric(
            [1.0 if rnd.round_win_amount > 0 else 0.0 for rnd in rounds]
        ),
        avg_free_rounds_awarded=statistical_metric(
            [float(rnd.award_free_rounds) for rnd in rounds]
        ),
    )
