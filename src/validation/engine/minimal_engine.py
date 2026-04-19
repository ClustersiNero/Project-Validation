from validation.core.types import CanonicalResult, BetRecord, RoundRecord, RollRecord, SimulationMetadata
from validation.config.minimal_config import MinimalSimulationConfig
from validation.engine.rng import RNG


def build_minimal_canonical_result(config: MinimalSimulationConfig, rng: RNG) -> CanonicalResult:
    rounds = []
    for round_index, round_data in enumerate(config.rounds):
        rolls = [
            RollRecord(
                roll_id=roll_index,
                roll_type="initial" if roll_index == 0 else "cascade",
                roll_win_amount=round_data.roll_wins[
                    rng.next_int(0, len(round_data.roll_wins) - 1)
                ],
                strip_set_id=0,
                multiplier_profile_id=0,
            )
            for roll_index in range(len(round_data.roll_wins))
        ]
        base_symbol_win_amount = sum(r.roll_win_amount for r in rolls)
        round_ = RoundRecord(
            round_id=round_data.round_id,
            round_type=round_data.round_type,
            roll_count=len(rolls),
            rolls=rolls,
            base_symbol_win_amount=base_symbol_win_amount,
            round_total_multiplier=1.0,
            round_win_amount=base_symbol_win_amount,
            round_final_state=[],
        )
        rounds.append(round_)
    basic_win_amount = sum(rnd.round_win_amount for rnd in rounds if rnd.round_type == "basic")
    free_win_amount = sum(rnd.round_win_amount for rnd in rounds if rnd.round_type == "free")
    bet = BetRecord(
        bet_id=0,
        round_count=len(rounds),
        rounds=rounds,
        basic_win_amount=basic_win_amount,
        free_win_amount=free_win_amount,
        bet_win_amount=basic_win_amount + free_win_amount,
        bet_final_state={},
    )
    metadata = SimulationMetadata(
        simulation_id=config.simulation_id,
        config_id=config.config_id,
        config_version=config.config_version,
        engine_version=config.engine_version,
        schema_version=config.schema_version,
        mode=config.mode,
        seed=config.seed,
        bet_amount=config.bet_amount,
        bet_level=config.bet_level,
        total_bets=1,
        timestamp=config.timestamp,
    )
    return CanonicalResult(simulation_metadata=metadata, bets=[bet])
