from validation.core.types import CanonicalResult, BetRecord, RoundRecord, RollRecord


def build_minimal_canonical_result(config) -> CanonicalResult:
    rounds = []
    for round_index, round_data in enumerate(config["rounds"]):
        rolls = [
            RollRecord(roll_id=roll_index, roll_win_amount=win_amount)
            for roll_index, win_amount in enumerate(round_data["roll_wins"])
        ]
        round_ = RoundRecord(
            round_id=round_index,
            round_type="basic",
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
