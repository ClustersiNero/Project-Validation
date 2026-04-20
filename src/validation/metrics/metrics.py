from dataclasses import dataclass

from validation.canonical.schema import CanonicalResult


@dataclass
class MetricsBundle:
    bet_count: int = 0
    round_count: int = 0
    roll_count: int = 0
    total_bet_win_amount: float = 0.0
    total_round_win_amount: float = 0.0
    total_roll_win_amount: float = 0.0


def compute_metrics_impl(result: CanonicalResult) -> MetricsBundle:
    bet_count = len(result.bets)
    round_count = sum(len(b.rounds) for b in result.bets)
    roll_count = sum(len(r.rolls) for b in result.bets for r in b.rounds)
    total_bet_win_amount = sum(b.bet_win_amount for b in result.bets)
    total_round_win_amount = sum(r.round_win_amount for b in result.bets for r in b.rounds)
    total_roll_win_amount = sum(ro.roll_win_amount for b in result.bets for r in b.rounds for ro in r.rolls)
    return MetricsBundle(
        bet_count=bet_count,
        round_count=round_count,
        roll_count=roll_count,
        total_bet_win_amount=total_bet_win_amount,
        total_round_win_amount=total_round_win_amount,
        total_roll_win_amount=total_roll_win_amount,
    )
