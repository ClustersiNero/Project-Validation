from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass
class StripBuildConfig:
    run_lengths: list[int]
    run_weights: list[int]
    symbols: list[int]
    symbol_weights: list[int]
    axis_count: int = 1
    seed: int | None = None


def validate_config(config: StripBuildConfig) -> None:
    if len(config.run_lengths) != len(config.run_weights):
        raise ValueError("run_lengths and run_weights length mismatch")
    if len(config.symbols) != len(config.symbol_weights):
        raise ValueError("symbols and symbol_weights length mismatch")
    if not config.run_lengths:
        raise ValueError("run_lengths must not be empty")
    if not config.symbols:
        raise ValueError("symbols must not be empty")
    if config.axis_count <= 0:
        raise ValueError("axis_count must be positive")
    if any(length <= 0 for length in config.run_lengths):
        raise ValueError("run_lengths must all be positive")
    if any(weight < 0 for weight in config.run_weights):
        raise ValueError("run_weights must not be negative")
    if any(weight < 0 for weight in config.symbol_weights):
        raise ValueError("symbol_weights must not be negative")
    if sum(config.run_weights) <= 0:
        raise ValueError("run_weights total must be positive")
    if sum(config.symbol_weights) <= 0:
        raise ValueError("symbol_weights total must be positive")


def build_symbol_counts(config: StripBuildConfig) -> dict[int, int]:
    run_weight_sum = sum(config.run_weights)

    return {
        symbol: symbol_weight * run_weight_sum
        for symbol, symbol_weight in zip(config.symbols, config.symbol_weights)
        if symbol_weight > 0
    }


def can_make_circular_no_adjacent(symbol_counts: dict[int, int]) -> bool:
    total = sum(symbol_counts.values())
    if total <= 1:
        return True
    return max(symbol_counts.values()) <= total // 2


def _future_feasible_after_pick(counts: Counter[int], picked: int) -> bool:
    test = counts.copy()
    test[picked] -= 1
    if test[picked] == 0:
        del test[picked]

    remaining = sum(test.values())
    if remaining <= 1:
        return True
    return max(test.values(), default=0) <= (remaining + 1) // 2


def arrange_symbols_linear(symbol_counts: dict[int, int], rng: random.Random) -> list[int]:
    counts = Counter(symbol_counts)
    result: list[int] = []

    while counts:
        last = result[-1] if result else None

        candidates = [
            symbol for symbol in counts
            if symbol != last and _future_feasible_after_pick(counts, symbol)
        ]

        if not candidates:
            # 理论上不该发生；兜底选剩余最多的合法 symbol。
            candidates = [symbol for symbol in counts if symbol != last]

        if not candidates:
            raise RuntimeError("Failed to arrange symbols without adjacent duplicates.")

        symbol = rng.choices(
            candidates,
            weights=[counts[symbol] for symbol in candidates],
            k=1,
        )[0]

        result.append(symbol)
        counts[symbol] -= 1
        if counts[symbol] == 0:
            del counts[symbol]

    return result


def make_sequence_circular(sequence: list[int], rng: random.Random) -> list[int]:
    if len(sequence) <= 1 or sequence[0] != sequence[-1]:
        return sequence

    n = len(sequence)
    last_symbol = sequence[-1]

    candidate_indices = list(range(1, n - 1))
    rng.shuffle(candidate_indices)

    for i in candidate_indices:
        candidate = sequence[i]

        # 把 sequence[i] 换到最后之后，需要：
        # 1) 新最后 != 首块
        # 2) 倒数第二块 != 新最后
        # 3) 被换入 i 的旧最后，不能等于 i 左右邻居
        if candidate == sequence[0]:
            continue
        if sequence[-2] == candidate:
            continue
        if sequence[i - 1] == last_symbol:
            continue
        if i + 1 < n and sequence[i + 1] == last_symbol:
            continue

        sequence[i], sequence[-1] = sequence[-1], sequence[i]
        return sequence

    raise RuntimeError("Failed to repair circular boundary.")


def arrange_symbols_circular(symbol_counts: dict[int, int], rng: random.Random) -> list[int]:
    if not can_make_circular_no_adjacent(symbol_counts):
        raise ValueError(
            "Cannot build circular no-adjacent symbol sequence: "
            "one symbol appears too often."
        )

    sequence = arrange_symbols_linear(symbol_counts, rng)
    return make_sequence_circular(sequence, rng)


def build_run_length_pockets(config: StripBuildConfig) -> dict[int, list[int]]:
    pockets: dict[int, list[int]] = defaultdict(list)

    for symbol, symbol_weight in zip(config.symbols, config.symbol_weights):
        for run_length, run_weight in zip(config.run_lengths, config.run_weights):
            pockets[symbol].extend([run_length] * (symbol_weight * run_weight))

    return dict(pockets)


def assign_run_lengths(
    symbol_sequence: list[int],
    config: StripBuildConfig,
    rng: random.Random,
) -> list[tuple[int, int]]:
    pockets = build_run_length_pockets(config)

    for pocket in pockets.values():
        rng.shuffle(pocket)

    blocks: list[tuple[int, int]] = []

    for symbol in symbol_sequence:
        if not pockets[symbol]:
            raise RuntimeError(f"run_length pocket for symbol {symbol} is empty")
        blocks.append((symbol, pockets[symbol].pop()))

    return blocks


def expand_blocks_to_axis(blocks: list[tuple[int, int]]) -> list[int]:
    axis: list[int] = []
    for symbol, run_length in blocks:
        axis.extend([symbol] * run_length)
    return axis


def build_axis(config: StripBuildConfig, rng: random.Random | None = None) -> list[int]:
    validate_config(config)
    local_rng = rng if rng is not None else random.Random(config.seed)

    symbol_counts = build_symbol_counts(config)
    symbol_sequence = arrange_symbols_circular(symbol_counts, local_rng)
    blocks = assign_run_lengths(symbol_sequence, config, local_rng)
    return expand_blocks_to_axis(blocks)


def build_axes(config: StripBuildConfig) -> dict[int, list[int]]:
    validate_config(config)
    rng = random.Random(config.seed)

    result: dict[int, list[int]] = {}
    for axis_id in range(1, config.axis_count + 1):
        result[axis_id] = build_axis(config, rng)
    return result


def print_custom_format(axes: dict[int, list[int]], outer_key: str = "￥") -> None:
    print(f"    {outer_key}: {{")
    for axis_id, axis in axes.items():
        print(f"        {axis_id}: {axis},")
    print("    },")


if __name__ == "__main__":
    config = StripBuildConfig(
        run_lengths=    [1, 2, 3, 4, 5],
        run_weights=    [9, 0, 0, 0, 0],
        symbols=        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        # symbol_weights= [3, 3, 3, 3, 3, 2, 2, 2, 1],  # 长条轴专用：1.包含4\5连片；2.符号全涵盖
        # symbol_weights= [0, 4, 0, 4, 0, 2, 0, 2, 1],  # 错位轴组件1
        # symbol_weights= [3, 0, 3, 0, 3, 0, 2, 0, 1],  # 错位轴组件2
        # symbol_weights= [1, 0, 1, 0, 1, 0, 1, 0, 1],    # buy free专用1
        symbol_weights= [1, 1, 0, 1, 0, 1, 0, 1, 0],    # buy free专用2
        axis_count=6,
        seed=12345,
    )

    axes = build_axes(config)
    print_custom_format(axes)
