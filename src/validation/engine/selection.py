from math import gcd

from validation.engine.rng import RNG


def choose_weighted_id(weights: list[int], rng: RNG) -> int:
    if not weights:
        raise ValueError("weights must be non-empty")
    if any(weight < 0 for weight in weights):
        raise ValueError("weights must be non-negative")

    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("sum(weights) must be positive")

    reachable_ids = [index + 1 for index, weight in enumerate(weights) if weight > 0]
    if len(reachable_ids) == 1:
        return reachable_ids[0]

    normalized_weights = _normalize_weights(weights)
    normalized_total_weight = sum(normalized_weights)

    draw = rng.next_int(1, normalized_total_weight)
    cumulative_weight = 0
    for index, weight in enumerate(normalized_weights):
        cumulative_weight += weight
        if draw <= cumulative_weight:
            return index + 1

    raise RuntimeError("weighted selection failed")


def _normalize_weights(weights: list[int]) -> list[int]:
    positive_weights = [weight for weight in weights if weight > 0]
    common_divisor = positive_weights[0]
    for weight in positive_weights[1:]:
        common_divisor = gcd(common_divisor, weight)
    if common_divisor == 1:
        return list(weights)
    return [
        0 if weight == 0 else weight // common_divisor
        for weight in weights
    ]


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
