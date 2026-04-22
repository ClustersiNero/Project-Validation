from validation.metrics.statistics import ratio_or_none, statistical_metric
from validation.metrics.types import (
    RollCoreMetrics,
    RollMetrics,
    RollPartitionMetrics,
    RollTypeDistribution,
)


def compute_roll_metrics(rolls: list) -> RollMetrics:
    initial_rolls = [roll for roll in rolls if roll.roll_type == "initial"]
    cascade_rolls = [roll for roll in rolls if roll.roll_type == "cascade"]
    total_roll_win_amount = sum(roll.roll_win_amount for roll in rolls)

    return RollMetrics(
        core=RollCoreMetrics(
            roll_count=len(rolls),
            total_roll_win_amount=total_roll_win_amount,
            avg_roll_win_amount=statistical_metric([roll.roll_win_amount for roll in rolls]),
            roll_hit_frequency=statistical_metric(
                [1.0 if roll.roll_win_amount > 0 else 0.0 for roll in rolls]
            ),
            roll_type_distribution=RollTypeDistribution(
                initial=ratio_or_none(
                    sum(1 for roll in rolls if roll.roll_type == "initial"),
                    len(rolls),
                ),
                cascade=ratio_or_none(
                    sum(1 for roll in rolls if roll.roll_type == "cascade"),
                    len(rolls),
                ),
            ),
        ),
        initial=compute_roll_partition_metrics(initial_rolls),
        cascade=compute_roll_partition_metrics(cascade_rolls),
    )


def compute_roll_partition_metrics(rolls: list) -> RollPartitionMetrics:
    return RollPartitionMetrics(
        roll_count=len(rolls),
        avg_roll_win_amount=statistical_metric([roll.roll_win_amount for roll in rolls]),
        roll_hit_frequency=statistical_metric(
            [1.0 if roll.roll_win_amount > 0 else 0.0 for roll in rolls]
        ),
    )
