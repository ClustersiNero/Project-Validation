# Config Specification

## 0. Purpose

This document defines the config contract consumed by the current repository.

Config describes the possibility space available to the engine. It is an input contract, not an implementation document.

---

## 1. Core Principle

- config defines the complete set of legal values the engine may sample from
- the engine must only read, sample, and use config
- config must not embed runtime steering or player-dependent logic
- all valid outcomes must be reachable from config + fixed seed alone

---

## 2. Global Rules

1. Determinism: identical seed + identical config must produce identical sampling behavior
2. Immutability at runtime: config is read-only during execution
3. No player-dependent logic
4. Explicit rules only; no hidden defaults
5. No reroll, filtering, adaptive weights, or outcome shaping

---

## 3. Schema Definitions

### 3.1 `SIMULATION_MODE`

Type:

```python
dict[int, dict]
```

Each mode entry contains:

- `mode_name: str`
- `bet_cost_multiplier: float`

Derived relationships:

- `bet_amount = base_bet * bet_cost_multiplier`
- `bet_level = base_bet`

Current modes:

- `1 -> normal`
- `2 -> buy_free`
- `3 -> chance_increase`

---

### 3.2 `PAYTABLE`

Type:

```python
dict[int, dict]
```

Each symbol entry contains:

- `symbol_name: str`
- `symbol_type: "regular" | "scatter" | "multiplier"`
- `payouts: dict[int, float]` for `regular` and `scatter`

Rules:

- regular payouts are count-based and normalized by `bet_level`
- scatter payouts are count-based and normalized by `bet_level`
- multiplier symbols do not have direct payouts

---

### 3.3 `MULTIPLIER_DATA`

Type:

```python
{
    "value": list[int],
    "weight": dict[int, list[int]],
}
```

Rules:

- `value[i]` aligns with `weight[profile_id][i]`
- each profile weight list must match the length of `value`
- weights are discrete non-negative integers
- each profile must have positive total reachable weight

---

### 3.4 `STRIP_SETS`

Type:

```python
dict[int, dict[int, list[int]]]
```

Outer key:

- `strip_set_id`

Inner key:

- `strip_id`

Rules:

- each strip set used by this implementation must contain exactly 6 strips
- each strip is an ordered cyclic list of valid paytable symbol ids
- strip ids are shuffled once at round start to assign strips to the 6 columns
- the column-to-strip mapping remains fixed within the round
- cascades and refills within the same round reuse the same strip set and the same column-to-strip mapping

---

### 3.5 `IMPLEMENTATION_CONFIG`

Type:

```python
dict[int, dict[str, dict]]
```

Outer key:

- `mode_id`

Second-level key:

- `round_type`
- current valid values: `basic`, `free`

Each round-type entry contains:

- `round_strip_set_weights`
- `round_multiplier_profile_weights`

Index-to-id mapping is always:

```text
id = index + 1
```

So:

- `round_strip_set_weights[i]` maps to `strip_set_id = i + 1`
- `round_multiplier_profile_weights[i]` maps to `multiplier_profile_id = i + 1`

Rules:

- list lengths must match the current number of strip sets / multiplier profiles
- all weights are non-negative integers
- each weight list must have positive total reachable weight

---

## 4. Mapping Rules

### 4.1 Strip Set Selection

Given `(mode, round_type)`:

- sample an index from `round_strip_set_weights`
- selected `strip_set_id = index + 1`

### 4.2 Multiplier Profile Selection

Given `(mode, round_type)`:

- sample an index from `round_multiplier_profile_weights`
- selected `multiplier_profile_id = index + 1`

### 4.3 Multiplier Value Sampling

Given `multiplier_profile_id = p`:

- sample an index from `MULTIPLIER_DATA["weight"][p]`
- selected value = `MULTIPLIER_DATA["value"][index]`

---

## 5. Determinism Requirements

- seeded RNG only
- fixed call order
- weighted discrete sampling for strip set, multiplier profile, and multiplier value selection
- Fisher-Yates shuffle for strip-id shuffling within a strip set
- cyclic strip sampling for board fill

---

## 6. Board Representation Constraints

For the current implementation:

- column count is fixed at `6`
- row count is fixed at `5`

State derivation:

- `roll_pre_fill_state` is the board before the current fill
- `roll_filled_state` is directly generated from strip sampling and refill
- `roll_cleared_state` is produced by clearing winning regular symbols
- `roll_gravity_state` is produced by applying gravity after clearing

---

## 7. Non-Goals

Config does not define:

- metrics
- validation thresholds
- runtime branching logic
- player adaptation
- payout settlement orchestration
