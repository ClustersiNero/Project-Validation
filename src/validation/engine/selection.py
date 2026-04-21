from validation.engine.rng import RNG


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


def choose_round_strip_set_id(
    implementation_config: dict,
    mode_id: int,
    round_type: str,
    rng: RNG,
) -> int:
    weights = implementation_config[mode_id][round_type]["round_strip_set_weights"]
    return choose_weighted_id(weights, rng)


def choose_round_multiplier_profile_id(
    implementation_config: dict,
    mode_id: int,
    round_type: str,
    rng: RNG,
) -> int:
    weights = implementation_config[mode_id][round_type]["round_multiplier_profile_weights"]
    return choose_weighted_id(weights, rng)


def choose_multiplier_value(
    multiplier_data: dict,
    multiplier_profile_id: int,
    rng: RNG,
) -> int:
    weights = multiplier_data["weight"][multiplier_profile_id]
    multiplier_value_id = choose_weighted_id(weights, rng)
    return multiplier_data["value"][multiplier_value_id - 1]
