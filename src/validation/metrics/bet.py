from validation.metrics.statistics import statistical_metric
from validation.metrics.types import BetCoreMetrics, BetMetrics, BetStructureMetrics


def compute_bet_metrics(bets: list, bet_amount: float, total_bet_amount: float) -> BetMetrics:
    return BetMetrics(
        core=BetCoreMetrics(
            empirical_rtp=statistical_metric(
                [bet.bet_win_amount / bet_amount for bet in bets]
                if bet_amount > 0
                else None,
                sample_size=len(bets),
            ),
            avg_bet_win_amount=statistical_metric([bet.bet_win_amount for bet in bets]),
            bet_hit_frequency=statistical_metric(
                [1.0 if bet.bet_win_amount > 0 else 0.0 for bet in bets]
            ),
            free_containing_bet_frequency=statistical_metric(
                [
                    1.0 if any(rnd.round_type == "free" for rnd in bet.rounds) else 0.0
                    for bet in bets
                ]
            ),
            basic_rtp=statistical_metric(
                [bet.basic_win_amount / bet_amount for bet in bets]
                if bet_amount > 0
                else None,
                sample_size=len(bets),
            ),
            free_rtp=statistical_metric(
                [bet.free_win_amount / bet_amount for bet in bets]
                if bet_amount > 0
                else None,
                sample_size=len(bets),
            ),
        ),
        structure=BetStructureMetrics(
            avg_rounds_per_bet=statistical_metric([float(bet.round_count) for bet in bets]),
            avg_free_rounds_per_bet=statistical_metric(
                [
                    float(sum(1 for rnd in bet.rounds if rnd.round_type == "free"))
                    for bet in bets
                ]
            ),
            avg_rolls_per_bet=statistical_metric(
                [float(sum(rnd.roll_count for rnd in bet.rounds)) for bet in bets]
            ),
        ),
    )
