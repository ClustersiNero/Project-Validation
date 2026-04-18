from validation.core.types import CanonicalResult, BetRecord, RoundRecord, RollRecord
from validation.config.minimal_config import MinimalSimulationConfig
from validation.engine.rng import RNG


def build_minimal_canonical_result(config: MinimalSimulationConfig, rng: RNG) -> CanonicalResult:
    rounds = []
    for round_index, round_data in enumerate(config.rounds):
        rolls = [
            RollRecord(
                roll_id=roll_index,
                roll_win_amount=round_data.roll_wins[
                    rng.next_int(0, len(round_data.roll_wins) - 1)
                ],
            )
            for roll_index in range(len(round_data.roll_wins))
        ]
        round_ = RoundRecord(
            round_id=round_data.round_id,
            round_type=round_data.round_type,
            roll_count=len(rolls),
            rolls=rolls,
            round_win_amount=sum(r.roll_win_amount for r in rolls),
        )
        rounds.append(round_)
    bet = BetRecord(
        bet_id=0,
        round_count=len(rounds),
        rounds=rounds,
        bet_win_amount=sum(rnd.round_win_amount for rnd in rounds),
    )
    return CanonicalResult(bets=[bet])
