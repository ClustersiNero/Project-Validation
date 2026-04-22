from validation.metrics.statistics import ratio_or_none, statistical_metric
from validation.metrics.types import BetCoreMetrics, BetMetrics


def compute_bet_metrics(bets: list, bet_amount: float, total_bet_amount: float) -> BetMetrics:
    total_basic_win_amount = sum(bet.basic_win_amount for bet in bets)
    total_free_win_amount = sum(bet.free_win_amount for bet in bets)

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
            basic_rtp=ratio_or_none(total_basic_win_amount, total_bet_amount),
            free_rtp=ratio_or_none(total_free_win_amount, total_bet_amount),
        ),
    )
