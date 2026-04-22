from validation.canonical.schema import CanonicalResult
from validation.metrics.bet import compute_bet_metrics
from validation.metrics.roll import compute_roll_metrics
from validation.metrics.round import compute_round_metrics
from validation.metrics.types import MetricsBundle, MetricsMeta

# Metrics are descriptive projections of CanonicalResult.
# They do not judge, validate, or reconstruct hidden engine state.


def compute_metrics_impl(result: CanonicalResult) -> MetricsBundle:
    metadata = result.simulation_metadata
    bets = result.bets
    rounds = [rnd for bet in bets for rnd in bet.rounds]
    rolls = [roll for rnd in rounds for roll in rnd.rolls]

    bet_amount = metadata.bet_amount
    total_bet_amount = len(bets) * bet_amount
    total_bet_win_amount = sum(bet.bet_win_amount for bet in bets)

    return MetricsBundle(
        meta=MetricsMeta(
            simulation_id=metadata.simulation_id,
            config_id=metadata.config_id,
            config_version=metadata.config_version,
            engine_version=metadata.engine_version,
            schema_version=metadata.schema_version,
            mode=metadata.mode,
            seed=metadata.seed,
            bet_amount=metadata.bet_amount,
            bet_level=metadata.bet_level,
            total_bets=len(bets),
            timestamp=metadata.timestamp,
            total_bet_amount=total_bet_amount,
            total_bet_win_amount=total_bet_win_amount,
        ),
        bet_metrics=compute_bet_metrics(bets, bet_amount, total_bet_amount),
        round_metrics=compute_round_metrics(rounds),
        roll_metrics=compute_roll_metrics(rolls),
    )
