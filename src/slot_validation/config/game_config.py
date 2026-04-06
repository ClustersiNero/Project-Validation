from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from slot_validation.games.olympus_mini.definition import OlympusMiniDefinition


# ============================================================
# Engine-facing normalized config models
# ============================================================

@dataclass(frozen=True)
class WagerMode:
    mode_id: int
    mode_name: str
    wager_cost_multiplier: float


@dataclass(frozen=True)
class SymbolDef:
    symbol_id: int
    symbol_name: str
    symbol_type: str
    payouts: dict[int, float]


@dataclass(frozen=True)
class MultiplierProfile:
    profile_id: int
    weights: tuple[int, ...]


@dataclass(frozen=True)
class RoundFlowConfig:
    strip_set_weights: tuple[int, ...]
    multiplier_profile_weights: tuple[int, ...]


@dataclass(frozen=True)
class ModeImplementationConfig:
    basic: RoundFlowConfig
    free: RoundFlowConfig


@dataclass(frozen=True)
class GameConfig:
    game_id: str
    config_version: str

    definition: OlympusMiniDefinition

    wager_modes: dict[int, WagerMode]
    symbols: dict[int, SymbolDef]

    scatter_symbol_id: int
    multiplier_symbol_id: int

    multiplier_values: tuple[int, ...]
    multiplier_profiles: dict[int, MultiplierProfile]

    strip_sets: dict[int, dict[int, tuple[int, ...]]]
    implementation: dict[int, ModeImplementationConfig]


# ============================================================
# Public API
# ============================================================

def build_game_config(
    module: Any,
    definition: OlympusMiniDefinition,
) -> GameConfig:
    """
    Build engine-facing GameConfig from:
    - external config module
    - fixed game definition

    Flow:
    1. precheck raw module structure
    2. normalize / build config objects
    3. derive engine-facing special symbol ids
    4. validate cross references
    """
    _precheck_module(module)
    _precheck_definition(definition)

    wager_modes_raw = module.WAGER_MODE
    paytable_raw = module.PAYTABLE
    multiplier_data_raw = module.MULTIPLIER_DATA
    strip_sets_raw = module.STRIP_SETS
    implementation_raw = module.IMPLEMENTATION_CONFIG

    wager_modes = _build_wager_modes(wager_modes_raw)
    symbols = _build_symbols(paytable_raw)
    scatter_symbol_id = _find_symbol_id_by_type(symbols, "scatter")
    multiplier_symbol_id = _find_symbol_id_by_type(symbols, "multiplier")
    multiplier_values, multiplier_profiles = _build_multiplier_data(multiplier_data_raw)
    strip_sets = _build_strip_sets(strip_sets_raw)
    implementation = _build_implementation(implementation_raw)

    config = GameConfig(
        game_id=definition.game_id,
        config_version="0.1.0",
        definition=definition,
        wager_modes=wager_modes,
        symbols=symbols,
        scatter_symbol_id=scatter_symbol_id,
        multiplier_symbol_id=multiplier_symbol_id,
        multiplier_values=multiplier_values,
        multiplier_profiles=multiplier_profiles,
        strip_sets=strip_sets,
        implementation=implementation,
    )

    _validate_cross_references(config)
    return config


# ============================================================
# Precheck
# ============================================================

def _precheck_module(module: Any) -> None:
    _require_attr(module, "WAGER_MODE")
    _require_attr(module, "PAYTABLE")
    _require_attr(module, "MULTIPLIER_DATA")
    _require_attr(module, "STRIP_SETS")
    _require_attr(module, "IMPLEMENTATION_CONFIG")

    _require_dict(module.WAGER_MODE, "WAGER_MODE")
    _require_dict(module.PAYTABLE, "PAYTABLE")
    _require_dict(module.MULTIPLIER_DATA, "MULTIPLIER_DATA")
    _require_dict(module.STRIP_SETS, "STRIP_SETS")
    _require_dict(module.IMPLEMENTATION_CONFIG, "IMPLEMENTATION_CONFIG")


def _precheck_definition(definition: OlympusMiniDefinition) -> None:
    if definition.board_rows <= 0:
        raise ValueError("definition.board_rows must be > 0.")
    if definition.board_cols <= 0:
        raise ValueError("definition.board_cols must be > 0.")


# ============================================================
# Builders
# ============================================================

def _build_wager_modes(raw: dict[int, dict[str, Any]]) -> dict[int, WagerMode]:
    result: dict[int, WagerMode] = {}

    for mode_id, payload in raw.items():
        _require_dict(payload, f"WAGER_MODE[{mode_id}]")

        result[int(mode_id)] = WagerMode(
            mode_id=int(mode_id),
            mode_name=str(_require_key(payload, "mode_name", f"WAGER_MODE[{mode_id}]")),
            wager_cost_multiplier=float(
                _require_key(payload, "wager_cost_multiplier", f"WAGER_MODE[{mode_id}]")
            ),
        )

    if not result:
        raise ValueError("WAGER_MODE must not be empty.")

    return result


def _build_symbols(raw: dict[int, dict[str, Any]]) -> dict[int, SymbolDef]:
    result: dict[int, SymbolDef] = {}

    for symbol_id, payload in raw.items():
        _require_dict(payload, f"PAYTABLE[{symbol_id}]")

        payouts = payload.get("payouts", {})
        _require_dict(payouts, f"PAYTABLE[{symbol_id}].payouts")

        result[int(symbol_id)] = SymbolDef(
            symbol_id=int(symbol_id),
            symbol_name=str(_require_key(payload, "symbol_name", f"PAYTABLE[{symbol_id}]")),
            symbol_type=str(_require_key(payload, "symbol_type", f"PAYTABLE[{symbol_id}]")),
            payouts={int(k): float(v) for k, v in payouts.items()},
        )

    if not result:
        raise ValueError("PAYTABLE must not be empty.")

    return result


def _build_multiplier_data(
    raw: dict[str, Any],
) -> tuple[tuple[int, ...], dict[int, MultiplierProfile]]:
    _require_dict(raw, "MULTIPLIER_DATA")

    values_raw = _require_key(raw, "value", "MULTIPLIER_DATA")
    weights_raw = _require_key(raw, "weight", "MULTIPLIER_DATA")

    values = _as_int_tuple(values_raw, "MULTIPLIER_DATA['value']")
    _require_dict(weights_raw, "MULTIPLIER_DATA['weight']")

    profiles: dict[int, MultiplierProfile] = {}
    for profile_id, weights in weights_raw.items():
        weight_tuple = _as_int_tuple(
            weights,
            f"MULTIPLIER_DATA['weight'][{profile_id}]",
        )
        profiles[int(profile_id)] = MultiplierProfile(
            profile_id=int(profile_id),
            weights=weight_tuple,
        )

    if not values:
        raise ValueError("MULTIPLIER_DATA['value'] must not be empty.")
    if not profiles:
        raise ValueError("MULTIPLIER_DATA['weight'] must not be empty.")

    return values, profiles


def _build_strip_sets(
    raw: dict[int, dict[int, list[int]]],
) -> dict[int, dict[int, tuple[int, ...]]]:
    result: dict[int, dict[int, tuple[int, ...]]] = {}

    for strip_set_id, strips in raw.items():
        _require_dict(strips, f"STRIP_SETS[{strip_set_id}]")

        normalized_strips: dict[int, tuple[int, ...]] = {}
        for strip_id, strip_symbols in strips.items():
            normalized_strips[int(strip_id)] = _as_int_tuple(
                strip_symbols,
                f"STRIP_SETS[{strip_set_id}][{strip_id}]",
            )

        result[int(strip_set_id)] = normalized_strips

    if not result:
        raise ValueError("STRIP_SETS must not be empty.")

    return result


def _build_implementation(
    raw: dict[int, dict[str, dict[str, list[int]]]],
) -> dict[int, ModeImplementationConfig]:
    result: dict[int, ModeImplementationConfig] = {}

    for mode_id, payload in raw.items():
        _require_dict(payload, f"IMPLEMENTATION_CONFIG[{mode_id}]")

        basic_raw = _require_key(payload, "basic", f"IMPLEMENTATION_CONFIG[{mode_id}]")
        free_raw = _require_key(payload, "free", f"IMPLEMENTATION_CONFIG[{mode_id}]")

        _require_dict(basic_raw, f"IMPLEMENTATION_CONFIG[{mode_id}]['basic']")
        _require_dict(free_raw, f"IMPLEMENTATION_CONFIG[{mode_id}]['free']")

        result[int(mode_id)] = ModeImplementationConfig(
            basic=_build_round_flow_config(
                basic_raw,
                f"IMPLEMENTATION_CONFIG[{mode_id}]['basic']",
            ),
            free=_build_round_flow_config(
                free_raw,
                f"IMPLEMENTATION_CONFIG[{mode_id}]['free']",
            ),
        )

    if not result:
        raise ValueError("IMPLEMENTATION_CONFIG must not be empty.")

    return result


def _build_round_flow_config(raw: dict[str, Any], path: str) -> RoundFlowConfig:
    strip_set_weights = _as_int_tuple(
        _require_key(raw, "round_strip_set_weights", path),
        f"{path}['round_strip_set_weights']",
    )
    multiplier_profile_weights = _as_int_tuple(
        _require_key(raw, "round_multiplier_profile_weights", path),
        f"{path}['round_multiplier_profile_weights']",
    )

    return RoundFlowConfig(
        strip_set_weights=strip_set_weights,
        multiplier_profile_weights=multiplier_profile_weights,
    )


# ============================================================
# Cross-reference validation
# ============================================================

def _validate_cross_references(config: GameConfig) -> None:
    definition = config.definition

    # 1. implementation mode ids must exist in wager_modes
    for mode_id in config.implementation:
        if mode_id not in config.wager_modes:
            raise ValueError(
                f"IMPLEMENTATION_CONFIG mode_id {mode_id} not found in WAGER_MODE."
            )

    # 2. wager_modes should also all have implementation config
    for mode_id in config.wager_modes:
        if mode_id not in config.implementation:
            raise ValueError(
                f"WAGER_MODE mode_id {mode_id} not found in IMPLEMENTATION_CONFIG."
            )

    # 3. strip set weights length must match strip set count
    strip_set_count = len(config.strip_sets)
    multiplier_profile_count = len(config.multiplier_profiles)
    symbol_ids = set(config.symbols.keys())

    for mode_id, mode_impl in config.implementation.items():
        for state_name, flow in (("basic", mode_impl.basic), ("free", mode_impl.free)):
            if len(flow.strip_set_weights) != strip_set_count:
                raise ValueError(
                    f"IMPLEMENTATION_CONFIG[{mode_id}]['{state_name}'] "
                    f"round_strip_set_weights length must equal STRIP_SETS count "
                    f"({strip_set_count})."
                )

            if len(flow.multiplier_profile_weights) != multiplier_profile_count:
                raise ValueError(
                    f"IMPLEMENTATION_CONFIG[{mode_id}]['{state_name}'] "
                    f"round_multiplier_profile_weights length must equal "
                    f"multiplier profile count ({multiplier_profile_count})."
                )

            if sum(flow.strip_set_weights) <= 0:
                raise ValueError(
                    f"IMPLEMENTATION_CONFIG[{mode_id}]['{state_name}'] "
                    f"round_strip_set_weights total weight must be > 0."
                )

            if sum(flow.multiplier_profile_weights) <= 0:
                raise ValueError(
                    f"IMPLEMENTATION_CONFIG[{mode_id}]['{state_name}'] "
                    f"round_multiplier_profile_weights total weight must be > 0."
                )

    # 4. multiplier profile weights length must match multiplier value count
    multiplier_value_count = len(config.multiplier_values)
    for profile_id, profile in config.multiplier_profiles.items():
        if len(profile.weights) != multiplier_value_count:
            raise ValueError(
                f"MULTIPLIER_DATA['weight'][{profile_id}] length must equal "
                f"MULTIPLIER_DATA['value'] length ({multiplier_value_count})."
            )
        if sum(profile.weights) <= 0:
            raise ValueError(
                f"MULTIPLIER_DATA['weight'][{profile_id}] total weight must be > 0."
            )

    # 5. strip symbols must reference valid symbol ids
    for strip_set_id, strips in config.strip_sets.items():
        if len(strips) != definition.board_cols:
            raise ValueError(
                f"STRIP_SETS[{strip_set_id}] must contain exactly "
                f"{definition.board_cols} strips."
            )

        expected_strip_ids = set(range(1, definition.board_cols + 1))
        actual_strip_ids = set(strips.keys())
        if actual_strip_ids != expected_strip_ids:
            raise ValueError(
                f"STRIP_SETS[{strip_set_id}] strip ids must be "
                f"{sorted(expected_strip_ids)}, got {sorted(actual_strip_ids)}."
            )

        for strip_id, strip in strips.items():
            if not strip:
                raise ValueError(
                    f"STRIP_SETS[{strip_set_id}][{strip_id}] must not be empty."
                )
            for symbol_id in strip:
                if symbol_id not in symbol_ids:
                    raise ValueError(
                        f"STRIP_SETS[{strip_set_id}][{strip_id}] contains "
                        f"unknown symbol_id {symbol_id}."
                    )

    # 6. derived special symbol ids must still point to the correct types
    scatter_symbol = config.symbols[config.scatter_symbol_id]
    if scatter_symbol.symbol_type != "scatter":
        raise ValueError(
            f"PAYTABLE[{config.scatter_symbol_id}] must have symbol_type='scatter'."
        )

    multiplier_symbol = config.symbols[config.multiplier_symbol_id]
    if multiplier_symbol.symbol_type != "multiplier":
        raise ValueError(
            f"PAYTABLE[{config.multiplier_symbol_id}] must have "
            f"symbol_type='multiplier'."
        )


# ============================================================
# Helpers
# ============================================================

def _find_symbol_id_by_type(symbols: dict[int, SymbolDef], symbol_type: str) -> int:
    matched_ids = [
        symbol_id
        for symbol_id, symbol in symbols.items()
        if symbol.symbol_type == symbol_type
    ]

    if not matched_ids:
        raise ValueError(f"No symbol found with symbol_type='{symbol_type}'.")
    if len(matched_ids) > 1:
        raise ValueError(
            f"Expected exactly one symbol with symbol_type='{symbol_type}', "
            f"got {matched_ids}."
        )

    return matched_ids[0]


def _require_attr(obj: Any, attr_name: str) -> Any:
    if not hasattr(obj, attr_name):
        raise AttributeError(f"Missing required module attribute: {attr_name}")
    return getattr(obj, attr_name)


def _require_key(mapping: dict[str, Any], key: str, path: str) -> Any:
    if key not in mapping:
        raise KeyError(f"Missing required key {path}['{key}']")
    return mapping[key]


def _require_dict(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be dict, got {type(value).__name__}.")


def _as_int_tuple(value: Any, name: str) -> tuple[int, ...]:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{name} must be list or tuple.")

    result: list[int] = []
    for i, item in enumerate(value):
        if isinstance(item, bool):
            raise TypeError(f"{name}[{i}] must be int, got bool.")
        try:
            parsed = int(item)
        except (TypeError, ValueError) as exc:
            raise TypeError(f"{name}[{i}] must be int.") from exc

        if parsed < 0:
            raise ValueError(f"{name}[{i}] must be >= 0.")
        result.append(parsed)

    return tuple(result)