from math import sqrt
from typing import Any

from validation.metrics.types import MetricsBundle, StatisticalMetric
from validation.validation.types import (
    MetricRule,
    StatisticalCheckResult,
    StatisticalValidationReport,
    ValidationRules,
)


def validate_statistics_impl(
    metrics: MetricsBundle,
    validation_rules: ValidationRules,
) -> StatisticalValidationReport:
    checks: list[StatisticalCheckResult] = []
    active_rules = _active_metric_rules(metrics, validation_rules)
    for metric_path, rule in active_rules.items():
        metric_leaf = _resolve_metric_path(metrics, metric_path)
        if rule.expected_range is not None:
            checks.append(_check_expected_range(metric_path, metric_leaf, rule.expected_range))
        if rule.expected_value is not None or rule.z_value is not None:
            checks.append(_check_expected_value(metric_path, metric_leaf, rule))
    return StatisticalValidationReport(
        is_valid=all(check.verdict == "pass" for check in checks),
        statistical_checks=checks,
    )


def _active_metric_rules(
    metrics: MetricsBundle,
    validation_rules: ValidationRules,
) -> dict[str, MetricRule]:
    active_rules = dict(validation_rules.metrics)
    active_rules.update(validation_rules.metrics_by_mode.get(metrics.meta.mode, {}))
    return active_rules


def _resolve_metric_path(metrics: MetricsBundle, metric_path: str) -> Any:
    if not metric_path.startswith("MetricsBundle."):
        return None
    current: Any = metrics
    for part in metric_path.removeprefix("MetricsBundle.").split("."):
        if not hasattr(current, part):
            return None
        current = getattr(current, part)
    return current


def _observed_value(metric_leaf: Any) -> float | None:
    if isinstance(metric_leaf, StatisticalMetric):
        return metric_leaf.observed
    if isinstance(metric_leaf, (int, float)):
        return float(metric_leaf)
    return None


def _check_expected_range(
    metric_path: str,
    metric_leaf: Any,
    expected_range: tuple[float, float],
) -> StatisticalCheckResult:
    observed = _observed_value(metric_leaf)
    if observed is None:
        return StatisticalCheckResult(
            metric_path=metric_path,
            check_type="range",
            verdict="fail",
            observed=observed,
            expected_range=expected_range,
            notes="range check is non-computable because observed value is missing",
        )
    lower, upper = expected_range
    return StatisticalCheckResult(
        metric_path=metric_path,
        check_type="range",
        verdict="pass" if lower <= observed <= upper else "fail",
        observed=observed,
        expected_range=expected_range,
    )


def _check_expected_value(
    metric_path: str,
    metric_leaf: Any,
    rule: MetricRule,
) -> StatisticalCheckResult:
    if rule.expected_value is None or rule.z_value is None:
        return StatisticalCheckResult(
            metric_path=metric_path,
            check_type="ci",
            verdict="fail",
            expected_value=rule.expected_value,
            notes="expected_value and z_value must both be defined for CI check",
        )
    if not isinstance(metric_leaf, StatisticalMetric):
        return StatisticalCheckResult(
            metric_path=metric_path,
            check_type="ci",
            verdict="fail",
            expected_value=rule.expected_value,
            notes="CI check requires a StatisticalMetric leaf",
        )
    observed = metric_leaf.observed
    deviation = None if observed is None else observed - rule.expected_value
    if observed is None or metric_leaf.standard_deviation is None or metric_leaf.sample_size < 2:
        return StatisticalCheckResult(
            metric_path=metric_path,
            check_type="ci",
            verdict="fail",
            observed=observed,
            expected_value=rule.expected_value,
            deviation=deviation,
            notes="CI check is non-computable because observed, standard_deviation, or sample_size is insufficient",
        )
    tolerance = rule.z_value * (metric_leaf.standard_deviation / sqrt(metric_leaf.sample_size))
    return StatisticalCheckResult(
        metric_path=metric_path,
        check_type="ci",
        verdict="pass" if abs(deviation) <= tolerance else "fail",
        observed=observed,
        expected_value=rule.expected_value,
        deviation=deviation,
    )
