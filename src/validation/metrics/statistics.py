from math import sqrt

from validation.metrics.types import StatisticalMetric


def statistical_metric(
    series: list[float] | None,
    *,
    sample_size: int | None = None,
) -> StatisticalMetric:
    if series is None:
        return StatisticalMetric(sample_size=0 if sample_size is None else sample_size)

    size = len(series)
    if size == 0:
        return StatisticalMetric(sample_size=0)

    observed = sum(series) / size
    if size == 1:
        return StatisticalMetric(
            observed=observed,
            standard_deviation=None,
            sample_size=1,
        )

    variance = sum((value - observed) ** 2 for value in series) / (size - 1)
    return StatisticalMetric(
        observed=observed,
        standard_deviation=sqrt(variance),
        sample_size=size,
    )


def ratio_or_none(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator
