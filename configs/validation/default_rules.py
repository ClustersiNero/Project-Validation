from validation.core.types import MetricRule, ValidationRules


_Z_VALUE = 1.96


def _rule(expected_value: float) -> MetricRule:
    return MetricRule(expected_value=expected_value, z_value=_Z_VALUE)


DEFAULT_VALIDATION_RULES = ValidationRules(
    metrics_by_mode={
        "normal": {
            "MetricsBundle.bet_metrics.core.empirical_rtp": _rule(0.97),
            "MetricsBundle.bet_metrics.core.basic_rtp": _rule(0.63),
            "MetricsBundle.bet_metrics.core.free_rtp": _rule(0.34),
            "MetricsBundle.bet_metrics.core.bet_hit_frequency": _rule(0.30),
            "MetricsBundle.round_metrics.core.round_hit_frequency": _rule(0.30),
            "MetricsBundle.roll_metrics.core.roll_hit_frequency": _rule(0.40),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.initial": _rule(0.50),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.cascade": _rule(0.50),
            "MetricsBundle.bet_metrics.core.free_containing_bet_frequency": _rule(0.005),
            "MetricsBundle.bet_metrics.structure.avg_free_rounds_per_bet": _rule(0.15),
            "MetricsBundle.round_metrics.basic.round_hit_frequency": _rule(0.30),
            "MetricsBundle.round_metrics.free.round_hit_frequency": _rule(0.30),
            "MetricsBundle.round_metrics.basic.avg_round_win_amount": _rule(2.0),
            "MetricsBundle.round_metrics.free.avg_round_win_amount": _rule(4.0),
        },
        "buy_free": {
            "MetricsBundle.bet_metrics.core.empirical_rtp": _rule(0.97),
            "MetricsBundle.bet_metrics.core.basic_rtp": _rule(0.01),
            "MetricsBundle.bet_metrics.core.free_rtp": _rule(0.95),
            "MetricsBundle.bet_metrics.core.bet_hit_frequency": _rule(1.0),
            "MetricsBundle.round_metrics.core.round_hit_frequency": _rule(0.32),
            "MetricsBundle.roll_metrics.core.roll_hit_frequency": _rule(0.44),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.initial": _rule(0.45),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.cascade": _rule(0.55),
            "MetricsBundle.bet_metrics.core.free_containing_bet_frequency": _rule(1.0),
            "MetricsBundle.bet_metrics.structure.avg_free_rounds_per_bet": _rule(15.0),
            "MetricsBundle.round_metrics.basic.round_hit_frequency": _rule(1.0),
            "MetricsBundle.round_metrics.free.round_hit_frequency": _rule(0.30),
            "MetricsBundle.round_metrics.basic.avg_round_win_amount": _rule(3.0),
            "MetricsBundle.round_metrics.free.avg_round_win_amount": _rule(5.0),
        },
        "chance_increase": {
            "MetricsBundle.bet_metrics.core.empirical_rtp": _rule(0.97),
            "MetricsBundle.bet_metrics.core.basic_rtp": _rule(0.35),
            "MetricsBundle.bet_metrics.core.free_rtp": _rule(0.62),
            "MetricsBundle.bet_metrics.core.bet_hit_frequency": _rule(0.25),
            "MetricsBundle.round_metrics.core.round_hit_frequency": _rule(0.25),
            "MetricsBundle.roll_metrics.core.roll_hit_frequency": _rule(0.44),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.initial": _rule(0.55),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.cascade": _rule(0.45),
            "MetricsBundle.bet_metrics.core.free_containing_bet_frequency": _rule(0.0075),
            "MetricsBundle.bet_metrics.structure.avg_free_rounds_per_bet": _rule(15.0),
            "MetricsBundle.round_metrics.basic.round_hit_frequency": _rule(0.25),
            "MetricsBundle.round_metrics.free.round_hit_frequency": _rule(0.30),
            "MetricsBundle.round_metrics.basic.avg_round_win_amount": _rule(2.0),
            "MetricsBundle.round_metrics.free.avg_round_win_amount": _rule(5.0),
        },
    }
)
