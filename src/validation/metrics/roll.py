from validation.metrics.statistics import statistical_metric
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
            initial_roll_count=len(initial_rolls),
            cascade_roll_count=len(cascade_rolls),
            total_roll_win_amount=total_roll_win_amount,
            avg_roll_win_amount=statistical_metric([roll.roll_win_amount for roll in rolls]),
            roll_hit_frequency=statistical_metric(
                [1.0 if roll.roll_win_amount > 0 else 0.0 for roll in rolls]
            ),
            roll_type_distribution=RollTypeDistribution(
                initial=statistical_metric(
                    [1.0 if roll.roll_type == "initial" else 0.0 for roll in rolls]
                ),
                cascade=statistical_metric(
                    [1.0 if roll.roll_type == "cascade" else 0.0 for roll in rolls]
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
