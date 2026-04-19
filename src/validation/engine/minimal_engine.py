from validation.config.minimal_config import MinimalSimulationConfig
from validation.canonical.minimal_canonical import (
    BetRecord,
    CanonicalResult,
    RollRecord,
    RoundRecord,
    SimulationMetadata,
)
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
                roll_filled_state=[],
                roll_final_state=[],
                roll_multi_symbols_num=0,
                roll_multi_symbols_carry=[],
                roll_scatter_symbols_num=0,
            )
            for roll_index in range(len(round_data.roll_wins))
        ]
        base_symbol_win_amount = sum(r.roll_win_amount for r in rolls)
        round_ = RoundRecord(
            round_id=round_data.round_id,
            round_type=round_data.round_type,
            round_win_amount=base_symbol_win_amount,
            base_symbol_win_amount=base_symbol_win_amount,
            carried_multiplier=0.0,
            round_multiplier_increment=0.0,
            round_total_multiplier=1.0,
            round_scatter_increment=0,
            award_free_rounds=0,
            scatter_win_amount=0.0,
            roll_count=len(rolls),
            round_final_state={},
            rolls=rolls,
        )
        rounds.append(round_)
    basic_win_amount = sum(rnd.round_win_amount for rnd in rounds if rnd.round_type == "basic")
    free_win_amount = sum(rnd.round_win_amount for rnd in rounds if rnd.round_type == "free")
    bet = BetRecord(
        bet_id=0,
        bet_win_amount=basic_win_amount + free_win_amount,
        basic_win_amount=basic_win_amount,
        free_win_amount=free_win_amount,
        round_count=len(rounds),
        bet_final_state={},
        rounds=rounds,
    )
    metadata = SimulationMetadata(
        simulation_id=f"minimal-seed-{config.seed}",
        config_id="minimal_config",
        config_version="0.1.0",
        engine_version="minimal_engine.v1",
        schema_version="minimal_canonical.v1",
        mode="normal",
        seed=config.seed,
        bet_amount=1.0,
        bet_level=1.0,
        total_bets=1,
        timestamp="1970-01-01T00:00:00Z",
    )
    return CanonicalResult(simulation_metadata=metadata, bets=[bet])


def choose_weighted_id(weights: list[int], rng: RNG) -> int:
    if not weights:
        raise ValueError("weights must be non-empty")
    if any(weight < 0 for weight in weights):
        raise ValueError("weights must be non-negative")

    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("sum(weights) must be positive")

    draw = rng.next_int(1, total_weight)
    cumulative_weight = 0
    for index, weight in enumerate(weights):
        cumulative_weight += weight
        if draw <= cumulative_weight:
            return index + 1

    raise RuntimeError("weighted selection failed")


def choose_round_strip_set_id(implementation_config: dict, mode_id: int, round_type: str, rng: RNG) -> int:
    weights = implementation_config[mode_id][round_type]["round_strip_set_weights"]
    return choose_weighted_id(weights, rng)
