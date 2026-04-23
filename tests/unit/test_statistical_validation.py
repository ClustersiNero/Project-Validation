from configs.validation.default_rules import DEFAULT_VALIDATION_RULES
from validation.core.types import MetricRule, ValidationRules
from validation.core.validation import validate_statistics
from validation.metrics.types import MetricsBundle


def test_statistical_validation_runs_ci_and_range_checks():
    metrics = MetricsBundle()
    metrics.bet_metrics.core.empirical_rtp.observed = 0.97
    metrics.bet_metrics.core.empirical_rtp.standard_deviation = 0.10
    metrics.bet_metrics.core.empirical_rtp.sample_size = 100
    rules = ValidationRules(
        metrics={
            "MetricsBundle.bet_metrics.core.empirical_rtp": MetricRule(
                expected_value=0.96,
                expected_range=(0.90, 1.05),
                z_value=1.96,
            )
        }
    )

    report = validate_statistics(metrics, rules)

    assert report.is_valid is True
    assert len(report.statistical_checks) == 2
    assert {check.check_type for check in report.statistical_checks} == {"ci", "range"}


def test_statistical_validation_fails_invalid_metric_path():
    report = validate_statistics(
        MetricsBundle(),
        ValidationRules(
            metrics={
                "MetricsBundle.bet_metrics.core.missing_metric": MetricRule(
                    expected_range=(0.0, 1.0),
                )
            }
        ),
    )

    assert report.is_valid is False
    assert report.statistical_checks[0].verdict == "fail"
    assert "observed value is missing" in report.statistical_checks[0].notes


def test_statistical_validation_fails_ci_for_scalar_metric():
    metrics = MetricsBundle()
    metrics.round_metrics.core.round_count = 10
    report = validate_statistics(
        metrics,
        ValidationRules(
            metrics={
                "MetricsBundle.round_metrics.core.round_count": MetricRule(
                    expected_value=10.0,
                    z_value=1.96,
                )
            }
        ),
    )

    assert report.is_valid is False
    assert report.statistical_checks[0].verdict == "fail"
    assert "StatisticalMetric" in report.statistical_checks[0].notes


def test_statistical_validation_fails_non_computable_ci():
    metrics = MetricsBundle()
    metrics.bet_metrics.core.bet_hit_frequency.observed = 0.30
    metrics.bet_metrics.core.bet_hit_frequency.sample_size = 1
    report = validate_statistics(
        metrics,
        ValidationRules(
            metrics={
                "MetricsBundle.bet_metrics.core.bet_hit_frequency": MetricRule(
                    expected_value=0.30,
                    z_value=1.96,
                )
            }
        ),
    )

    assert report.is_valid is False
    assert report.statistical_checks[0].verdict == "fail"
    assert "non-computable" in report.statistical_checks[0].notes


def test_statistical_validation_uses_external_default_rules():
    normal_rule_paths = set(DEFAULT_VALIDATION_RULES.metrics_by_mode["normal"])
    buy_free_rule_paths = set(DEFAULT_VALIDATION_RULES.metrics_by_mode["buy_free"])
    chance_increase_rule_paths = set(DEFAULT_VALIDATION_RULES.metrics_by_mode["chance_increase"])

    expected_paths = {
        "MetricsBundle.bet_metrics.core.empirical_rtp",
        "MetricsBundle.bet_metrics.core.basic_rtp",
        "MetricsBundle.bet_metrics.core.free_rtp",
        "MetricsBundle.bet_metrics.core.bet_hit_frequency",
        "MetricsBundle.round_metrics.core.round_hit_frequency",
        "MetricsBundle.roll_metrics.core.roll_hit_frequency",
        "MetricsBundle.roll_metrics.core.roll_type_distribution.initial",
        "MetricsBundle.roll_metrics.core.roll_type_distribution.cascade",
        "MetricsBundle.bet_metrics.core.free_containing_bet_frequency",
        "MetricsBundle.bet_metrics.structure.avg_free_rounds_per_bet",
        "MetricsBundle.round_metrics.basic.round_hit_frequency",
        "MetricsBundle.round_metrics.free.round_hit_frequency",
        "MetricsBundle.round_metrics.basic.avg_round_win_amount",
        "MetricsBundle.round_metrics.free.avg_round_win_amount",
    }
    assert normal_rule_paths == expected_paths
    assert buy_free_rule_paths == expected_paths
    assert chance_increase_rule_paths == expected_paths
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["normal"]["MetricsBundle.bet_metrics.core.basic_rtp"].expected_value == 0.63
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["normal"]["MetricsBundle.bet_metrics.core.free_rtp"].expected_value == 0.34
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["buy_free"]["MetricsBundle.bet_metrics.core.basic_rtp"].expected_value == 0.01
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["buy_free"]["MetricsBundle.bet_metrics.core.free_rtp"].expected_value == 0.95
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["chance_increase"]["MetricsBundle.bet_metrics.core.basic_rtp"].expected_value == 0.35
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["chance_increase"]["MetricsBundle.bet_metrics.core.free_rtp"].expected_value == 0.62
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["normal"]["MetricsBundle.roll_metrics.core.roll_type_distribution.initial"].expected_value == 0.50
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["normal"]["MetricsBundle.roll_metrics.core.roll_type_distribution.cascade"].expected_value == 0.50
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["buy_free"]["MetricsBundle.roll_metrics.core.roll_type_distribution.initial"].expected_value == 0.45
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["buy_free"]["MetricsBundle.roll_metrics.core.roll_type_distribution.cascade"].expected_value == 0.55
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["chance_increase"]["MetricsBundle.roll_metrics.core.roll_type_distribution.initial"].expected_value == 0.55
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["chance_increase"]["MetricsBundle.roll_metrics.core.roll_type_distribution.cascade"].expected_value == 0.45
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["normal"]["MetricsBundle.bet_metrics.core.bet_hit_frequency"].expected_value == 0.30
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["buy_free"]["MetricsBundle.bet_metrics.core.bet_hit_frequency"].expected_value == 1.0
    assert DEFAULT_VALIDATION_RULES.metrics_by_mode["chance_increase"]["MetricsBundle.bet_metrics.core.bet_hit_frequency"].expected_value == 0.25


def test_statistical_validation_uses_current_mode_rules_over_global_rules():
    metrics = MetricsBundle()
    metrics.meta.mode = "buy_free"
    metrics.bet_metrics.core.bet_hit_frequency.observed = 1.0
    metrics.bet_metrics.core.bet_hit_frequency.standard_deviation = 0.1
    metrics.bet_metrics.core.bet_hit_frequency.sample_size = 100
    rules = ValidationRules(
        metrics={
            "MetricsBundle.bet_metrics.core.bet_hit_frequency": MetricRule(
                expected_value=0.30,
                z_value=1.96,
            )
        },
        metrics_by_mode={
            "buy_free": {
                "MetricsBundle.bet_metrics.core.bet_hit_frequency": MetricRule(
                    expected_value=1.0,
                    z_value=1.96,
                )
            }
        },
    )

    report = validate_statistics(metrics, rules)

    assert report.is_valid is True
    assert report.statistical_checks[0].expected_value == 1.0
