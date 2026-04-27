# Canonical Specification

## 0. Purpose

This document defines the canonical result schema used by downstream layers.

`CanonicalResult` is the single source of truth for:

- simulation metadata
- ordered bet records
- ordered round records
- ordered roll records
- board-state progression required for audit and reconstruction

It is not a metrics file.
It is not a validation file.

---

## 1. Top-Level Object

```python
CanonicalResult = {
    "simulation_metadata": SimulationMetadata,
    "bets": list[BetRecord],
}
```

---

## 2. Shared Types

```python
Cell = {
    "symbol_id": int,
    "multiplier_value": int | None,
}

BoardState = list[list[Cell | None]]
```

Rules:

- non-multiplier symbols MUST have `multiplier_value = null`
- multiplier symbols MUST have a non-null `multiplier_value`
- board orientation is `matrix[row][col]`
- row `0` is the bottom row; row index increases upward

---

## 3. SimulationMetadata

```python
SimulationMetadata = {
    "simulation_id": str,
    "config_id": str,
    "config_version": str,
    "engine_version": str,
    "schema_version": str,
    "mode": str,
    "seed": int,
    "bet_amount": float,
    "bet_level": float,
    "total_bets": int,
    "timestamp": str,
}
```

Notes:

- `bet_amount` records actual paid cost per bet
- `bet_level` records the payout normalization base used for paytable evaluation
- `timestamp` is audit metadata; presence is required, but it is not outcome-bearing

---

## 4. BetRecord

```python
BetRecord = {
    "bet_id": int,
    "bet_win_amount": float,
    "basic_win_amount": float,
    "free_win_amount": float,
    "round_count": int,
    "bet_final_state": BoardState | None,
    "rounds": list[RoundRecord],
}
```

Notes:

- one bet contains one or more rounds
- `bet_final_state` records the final board state after the bet is fully resolved
- `basic_win_amount` records the win from the initial basic flow
- `free_win_amount` records the aggregated win from free rounds

---

## 5. RoundRecord

```python
RoundRecord = {
    "round_id": int,
    "round_type": str,
    "round_win_amount": float,
    "base_symbol_win_amount": float,
    "carried_multiplier": float,
    "round_multiplier_increment": float,
    "round_total_multiplier": float,
    "round_scatter_increment": int,
    "award_free_rounds": int,
    "scatter_win_amount": float,
    "roll_count": int,
    "round_final_state": BoardState | None,
    "rolls": list[RollRecord],
}
```

Notes:

- `round_type` is either `basic` or `free`
- one round belongs to one bet
- one round contains one or more rolls
- `base_symbol_win_amount` is aggregated before round-level multiplier settlement
- `carried_multiplier` is the carried-in multiplier at round start
- `round_multiplier_increment` is the multiplier increment generated within the current round
- `round_total_multiplier` records the multiplier factor applied to `base_symbol_win_amount`
- `round_total_multiplier` MUST be `1` when `round_multiplier_increment == 0`
- `round_final_state` records the final board state after the round is fully resolved

### Carried Multiplier Semantics

- carried multiplier is updated across rounds at the bet level
- carry persists only across free rounds
- current-round settlement uses `carried_multiplier + round_multiplier_increment` only when the current round generates multiplier increment
- if `round_multiplier_increment == 0`, then `round_total_multiplier = 1` and no carry is applied to the current round

---

## 6. RollRecord

```python
RollRecord = {
    "roll_id": int,
    "roll_win_amount": float,
    "roll_type": str,
    "strip_set_id": int,
    "multiplier_profile_id": int,
    "column_strip_ids": list[int],
    "fill_start_indices": list[int],
    "fill_end_indices": list[int],
    "roll_pre_fill_state": BoardState,
    "roll_filled_state": BoardState,
    "roll_cleared_state": BoardState,
    "roll_gravity_state": BoardState,
    "roll_multi_symbols_num": int,
    "roll_multi_symbols_carry": list[int],
    "roll_scatter_symbols_num": int,
}
```

Notes:

- one roll belongs to one round
- rolls are ordered within a round
- `roll_type` is either `initial` or `cascade`
- `column_strip_ids` are fixed within a round and identify which strip is assigned to each column
- `fill_start_indices` and `fill_end_indices` record the actual strip index range used during the current roll fill
- `roll_pre_fill_state` is the board state before the current fill
- `roll_filled_state` is the filled board used for evaluation
- `roll_cleared_state` is the board after clearing winning regular symbols
- `roll_gravity_state` is the board after gravity; it is the terminal state of the roll
- `roll_win_amount` records base symbol win for the roll before round-level multiplier settlement

### Roll Execution Semantics

- a roll begins at `roll_pre_fill_state`
- empty positions are filled according to config
- multiplier values are assigned to generated multiplier symbols
- base symbol wins are evaluated
- winning regular symbols are cleared
- gravity is applied
- the resulting `roll_gravity_state` becomes the next roll's `roll_pre_fill_state` if cascade continues

Scatter and multiplier symbols may remain present across rolls, but round-level aggregation MUST count each symbol instance at most once within the same round.

Symbol instance identity is defined as:

```text
(first_observed_roll_id, first_observed_row, first_observed_col)
```

Gravity movement within subsequent cascades does not create a new instance.

---

## 7. Structural Rules

- `simulation_metadata` MUST be present
- `bets` MUST be present
- `simulation_metadata.total_bets == len(bets)`
- `bet.round_count == len(bet.rounds)`
- `round.roll_count == len(round.rolls)`
- records MUST preserve execution order at bet, round, and roll levels

---

## 8. Canonical Rules

CanonicalResult MUST be:

- deterministic
- complete
- neutral
- free of interpretive metrics
- free of validation verdicts

CanonicalResult MUST NOT include:

- RTP
- hit frequency
- pass/fail flags
- runtime control fields
- player-dependent logic markers

---

## 9. Determinism

The following must hold:

```python
(config, seed, engine_version) -> identical CanonicalResult
```

Deterministic replay equality applies to outcome-bearing canonical data and to metadata fields determined by explicit inputs.

---

## 10. Minimal API Contract

```python
run_simulation(config) -> CanonicalResult
```
