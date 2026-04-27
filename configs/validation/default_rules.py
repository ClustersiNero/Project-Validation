from validation.core.types import MetricRule, ValidationRules


_Z_VALUE = 1.96


def _rule(expected_value: float) -> MetricRule:
    return MetricRule(expected_value=expected_value, z_value=_Z_VALUE)


DEFAULT_VALIDATION_RULES = ValidationRules(
    metrics_by_mode={
        "normal": {
            "MetricsBundle.bet_metrics.core.empirical_rtp": _rule(0.959),
            "MetricsBundle.bet_metrics.core.basic_rtp": _rule(0.647),
            "MetricsBundle.bet_metrics.core.free_rtp": _rule(0.312),
            "MetricsBundle.bet_metrics.core.bet_hit_frequency": _rule(0.304),
            "MetricsBundle.round_metrics.core.round_hit_frequency": _rule(0.302),
            "MetricsBundle.roll_metrics.core.roll_hit_frequency": _rule(0.299),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.initial": _rule(0.701),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.cascade": _rule(0.299),
            "MetricsBundle.bet_metrics.core.free_containing_bet_frequency": _rule(0.0043),
            "MetricsBundle.bet_metrics.structure.avg_free_rounds_per_bet": _rule(0.077),
            "MetricsBundle.round_metrics.basic.round_hit_frequency": _rule(0.304),
            "MetricsBundle.round_metrics.free.round_hit_frequency": _rule(0.279),
            "MetricsBundle.round_metrics.basic.avg_round_win_amount": _rule(0.647),
            "MetricsBundle.round_metrics.free.avg_round_win_amount": _rule(4.037),
        },
        "buy_free": {
            "MetricsBundle.bet_metrics.core.empirical_rtp": _rule(0.95),
            "MetricsBundle.bet_metrics.core.basic_rtp": _rule(0.038),
            "MetricsBundle.bet_metrics.core.free_rtp": _rule(0.912),
            "MetricsBundle.bet_metrics.core.bet_hit_frequency": _rule(1.0),
            "MetricsBundle.round_metrics.core.round_hit_frequency": _rule(0.315),
            "MetricsBundle.roll_metrics.core.roll_hit_frequency": _rule(0.262),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.initial": _rule(0.738),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.cascade": _rule(0.262),
            "MetricsBundle.bet_metrics.core.free_containing_bet_frequency": _rule(1.0),
            "MetricsBundle.bet_metrics.structure.avg_free_rounds_per_bet": _rule(18.274),
            "MetricsBundle.round_metrics.basic.round_hit_frequency": _rule(1.0),
            "MetricsBundle.round_metrics.free.round_hit_frequency": _rule(0.277),
            "MetricsBundle.round_metrics.basic.avg_round_win_amount": _rule(3.0),
            "MetricsBundle.round_metrics.free.avg_round_win_amount": _rule(3.995),
        },
        "chance_increase": {
            "MetricsBundle.bet_metrics.core.empirical_rtp": _rule(0.978),
            "MetricsBundle.bet_metrics.core.basic_rtp": _rule(0.457),
            "MetricsBundle.bet_metrics.core.free_rtp": _rule(0.52),
            "MetricsBundle.bet_metrics.core.bet_hit_frequency": _rule(0.302),
            "MetricsBundle.round_metrics.core.round_hit_frequency": _rule(0.3),
            "MetricsBundle.roll_metrics.core.roll_hit_frequency": _rule(0.293),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.initial": _rule(0.707),
            "MetricsBundle.roll_metrics.core.roll_type_distribution.cascade": _rule(0.293),
            "MetricsBundle.bet_metrics.core.free_containing_bet_frequency": _rule(0.0089),
            "MetricsBundle.bet_metrics.structure.avg_free_rounds_per_bet": _rule(0.162),
            "MetricsBundle.round_metrics.basic.round_hit_frequency": _rule(0.302),
            "MetricsBundle.round_metrics.free.round_hit_frequency": _rule(0.282),
            "MetricsBundle.round_metrics.basic.avg_round_win_amount": _rule(0.572),
            "MetricsBundle.round_metrics.free.avg_round_win_amount": _rule(4.008),
        },
    }
)
