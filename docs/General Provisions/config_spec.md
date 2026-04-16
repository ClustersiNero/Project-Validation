# Config Specification

## 0. Purpose

This document defines the **config contract** for the slot validation system.

It describes the required structure, field types, and constraints for all config objects consumed by the engine, canonical, and metrics layers.

This is a specification of the input interface — not an implementation document. It does not describe runtime behavior, engine logic, or statistical outcomes.

---

## 1. Core Principle

- Config defines the **possibility space**: the complete set of values the engine may legally sample from.
- The engine's responsibility is: **read → sample → use**. It must not modify, filter, augment, or reinterpret config values at runtime.
- Config must not embed runtime logic, conditional branching, or player-dependent state.
- All valid outcomes must be reachable purely from config data and a fixed RNG seed.

---

## 2. Global Rules

The following rules apply to all config objects:

1. **Determinism**: Given the same seed, any sequence of sampling operations on config data must produce identical results.
2. **Immutability at runtime**: Config must not be modified during a run. All reads are read-only.
3. **No player-dependent logic**: Config values must not depend on player history, session state, or accumulated results.
4. **Explicit rules only**: All valid combinations, weights, and mappings must be stated explicitly. No implicit defaults or inferred values are permitted.
5. **No runtime steering**: Config must not encode reroll logic, accept-reject filters, range filters, adaptive weights, or any form of outcome shaping.

---

## 3. Schema Definitions

### 3.1 SIMULATION_MODE

**Type**: `dict[int → dict]`

Top-level key is the **mode id** (`int`).

Each entry contains:

| Field | Type | Constraint |
|---|---|---|
| `mode_name` | `str` | Non-empty. Human-readable label for the mode. |
| `bet_cost_multiplier` | `float` | Must be > 0. Multiplies the base bet to compute the bet cost. |

**Derived relationships**:

- `bet_amount = base_bet × bet_cost_multiplier`
- `bet_level = base_bet` (unchanged regardless of multiplier)

**Constraint**: The set of mode ids in `SIMULATION_MODE` must exactly match the set of top-level keys in `IMPLEMENTATION_CONFIG`.

---

### 3.2 PAYTABLE

**Type**: `dict[int → dict]`

Top-level key is the **symbol id** (`int`).

Each entry contains:

| Field | Type | Constraint |
|---|---|---|
| `symbol_name` | `str` | Non-empty. Unique within the paytable. |
| `symbol_type` | `str` (enum) | Must be one of: `"regular"`, `"scatter"`, `"multiplier"`. |
| `payouts` | `dict[int → float]` | Required for `regular` and `scatter`. Must not be present for `multiplier`. |

**Payout rules by symbol type**:

- **regular**: Payout is awarded based on symbol count on the board. Keys in `payouts` are qualifying counts (`int`). Values are multipliers applied to `bet_level`.
- **scatter**: Payout is awarded independently of board position. Keys in `payouts` are qualifying scatter counts. Values are multipliers applied to `bet_level`.
- **multiplier**: Does not participate in direct payout calculation. `payouts` field must be absent.

---

### 3.3 MULTIPLIER_DATA

**Type**: `dict`

Contains two fields:

| Field | Type | Constraint |
|---|---|---|
| `value` | `list[int]` | Ordered list of discrete multiplier values. Length = N. |
| `weight` | `dict[int → list[int]]` | Keyed by **profile id** (`int`). Each value is a weight list of length N. |

**Alignment rule**:

- `value[i]` and `weight[profile_id][i]` must correspond to the same outcome at every index `i`.
- For every profile id `p`: `len(weight[p])` must equal `len(value)`.

**Weight rules**:

- Weights are discrete (non-cumulative) integers ≥ 0.
- For every profile id `p`: `sum(weight[p])` must be > 0.
- Individual weights may be 0 (indicating that value is unreachable under that profile).

**Profile id namespace**:

- Profile ids begin at 1.
- The set of profile ids in `MULTIPLIER_DATA["weight"]` defines the complete set of valid multiplier profile ids.

---

### 3.4 STRIP_SETS

**Type**: `dict[int → dict[int → list[int]]]`

Outer key is the **strip set id** (`int`).  
Inner key is the **strip id** within that set (`int`, 1-indexed, currently 1–6).  
Value is an ordered list of **symbol ids** (`list[int]`).

**Structure rules**:

- The number of strips per strip set is fixed. The current implementation uses 6 strips per set (corresponding to 6 board columns).
- All symbol ids within a strip must be valid keys in `PAYTABLE`.

**Sampling rules**:

- Strip order within a set is fixed in config. The engine shuffles strip ids at round start (Fisher-Yates) to assign strips to columns.
- The column-to-strip mapping is fixed once at round start and does not change during cascades or refills within the same round.
- Strip sampling is cyclic: a random start position is chosen, and a contiguous slice of the required length is taken, wrapping around if necessary.
- The engine does not re-select the strip set or re-shuffle strip order during cascades or refills within the same round. For each round, the candidate strip sequence of the selected strip set is constructed from the configured strip order, then shuffled once with Fisher-Yates at round start to assign strips to columns. The shuffled mapping may differ across rounds, but MUST be reproducible for a given (config, seed, engine_version).


**Cross-reference**:

- All strip set ids referenced in `IMPLEMENTATION_CONFIG` weights must exist in `STRIP_SETS`.

---

### 3.5 IMPLEMENTATION_CONFIG

**Round Type Domain Constraint**:

The set of valid round types is fixed:
round_type ∈ {"basic", "free"}
All keys under IMPLEMENTATION_CONFIG[mode] must belong to this set.

**Type**: `dict[int → dict[str → dict]]`

Outer key is the **mode id** (`int`), matching keys in `SIMULATION_MODE`.  
Second-level key is the **round type** (`str`). Valid round types are defined by the engine (e.g., `"basic"`, `"free"`).

Each round type entry contains:

| Field | Type | Constraint |
|---|---|---|
| `round_strip_set_weights` | `list[int]` | Weight list for strip set selection. |
| `round_multiplier_profile_weights` | `list[int]` | Weight list for multiplier profile selection. |

**Index-to-id mapping (mandatory)**:

All weight lists in `IMPLEMENTATION_CONFIG` use **0-based index → 1-based id** mapping:

```
id = index + 1
```

Specifically:

- `round_strip_set_weights[i]` is the weight for `strip_set_id = i + 1`.
- `round_multiplier_profile_weights[i]` is the weight for `multiplier_profile_id = i + 1`.

**Length constraints**:

- `len(round_strip_set_weights)` must equal the number of strip sets defined in `STRIP_SETS`.
- `len(round_multiplier_profile_weights)` must equal the number of profiles defined in `MULTIPLIER_DATA["weight"]`.

**Weight rules**:

- All weight values are integers ≥ 0.
- Individual weights may be 0 (the corresponding id is unreachable for that mode/round combination).
- For every `(mode, round_type)` pair: `sum(round_strip_set_weights)` must be > 0 and `sum(round_multiplier_profile_weights)` must be > 0.

---

## 4. Mapping Rules

The following mappings are canonical and must be applied consistently across all layers.

### 4.1 Index → Id

All weight lists in `IMPLEMENTATION_CONFIG` use 0-based indexing mapping to 1-based ids:

```
id = index + 1
```

| Index | Id |
|---|---|
| 0 | 1 |
| 1 | 2 |
| i | i + 1 |

### 4.2 Multiplier Value Sampling

Given multiplier profile id `p`:

- Sample index `i` using weighted discrete distribution over `MULTIPLIER_DATA["weight"][p]`.
- Result value = `MULTIPLIER_DATA["value"][i]`.
- `value[i]` and `weight[p][i]` are always index-aligned.

### 4.3 Strip Set Selection

Given `(mode, round_type)`:

- Sample index `i` from `IMPLEMENTATION_CONFIG[mode][round_type]["round_strip_set_weights"]`.
- Selected `strip_set_id = i + 1`.
- Use `STRIP_SETS[strip_set_id]` for the round.

### 4.4 Multiplier Profile Selection

Given `(mode, round_type)`:

- Sample index `i` from `IMPLEMENTATION_CONFIG[mode][round_type]["round_multiplier_profile_weights"]`.
- Selected `multiplier_profile_id = i + 1`.
- Use `MULTIPLIER_DATA["weight"][multiplier_profile_id]` for multiplier sampling in that round.

---

## 5. Determinism Requirements

All randomness in config-driven sampling must satisfy the following:

1. **Seeded RNG only**: All sampling must derive from a fixed seed. No external entropy sources are permitted.
2. **Fixed call order**: The order of RNG calls is fixed and must not vary based on intermediate outcomes. The engine defines and preserves this call order.
3. **Weighted discrete sampling**: Strip set selection, multiplier profile selection, and multiplier value sampling all use weighted discrete distributions (non-cumulative integer weights).
4. **Strip shuffle algorithm**: Strip id shuffling within a strip set uses Fisher-Yates with the seeded RNG. The algorithm and call order are fixed.
5. **Cyclic slice sampling**: Strip position sampling uses a single RNG call per strip to select the start index.
6. **Replayability**: A run produced from a given seed must be exactly reproducible across separate executions.

---

## 6. Board Representation

The board is a column-based matrix populated from strip data.

| Property | Definition |
|---|---|
| Column count | Fixed at 6 for this game implementation. A selected strip set MUST contain exactly 6 strips. |
| Row count | Fixed at 5 for this game implementation. It MUST remain invariant for a given (config_version, engine_version). |
| Column contents | Each column is populated from its assigned strip by cyclic slice sampling. |

**Determinism requirement**:

- Board shape (column count × row count) must be fully deterministic and invariant for a given (config_version, engine_version).
- Board shape must not change based on intermediate outcomes, cascade state, or any runtime condition.

**State Derivation**:

- Both states ultimately derive their symbol data from the selected strip set.
- `roll_filled_state` is directly generated from strip sampling using the fixed column-to-strip mapping.
- `roll_final_state` is derived from `roll_filled_state` through deterministic in-engine transformations (e.g. symbol clearing and gravity).

**Structural constraint**:

- if a referenced strip set contains fewer or more than 6 strips, config validation MUST fail

---

## 7. Non-Goals

The following are explicitly outside the scope of config:

- **Metrics**: Config does not define thresholds, expected values, RTP, or statistical properties.
- **Validation**: Config does not define correctness checks, pass/fail criteria, or audit rules.
- **Runtime decisions**: Config does not encode branching logic, player adaptation, or outcome steering.
- **Engine orchestration**: Config does not specify execution order, cascade termination conditions, or payout settlement logic.
