# Engine Specification

## 0. Purpose

This document defines the engine contract for the current repository.

The engine in this repository is intentionally **Gate of Olympus-style and gameplay-bound**. It is not a generic slot engine.

Its job is to:

- read config
- consume seeded RNG in a deterministic order
- execute gameplay rules
- produce raw execution results for canonical recording

---

## 1. Core Principle

> The engine generates outcomes. It does not measure them, validate them, or reinterpret them.

Pipeline position:

```text
config -> engine -> canonical -> metrics -> validation
```

The engine must remain:

- deterministic
- config-driven
- free of runtime manipulation
- free of player-dependent logic

---

## 2. Input Contract

The engine consumes:

- normalized simulation config
- seeded RNG

Config provides:

- mode selection
- paytable
- multiplier values and weight profiles
- strip sets
- mode/round-type implementation weights

The engine must treat config as read-only.

---

## 3. Mode and Amount Semantics

The current repository supports three modes:

- `normal`
- `buy_free`
- `chance_increase`

Amount semantics:

- `bet_amount` = actual paid amount for the bet
- `bet_level` = payout normalization base

Rules:

- all payout generation uses `bet_level`
- return-based metrics later use `bet_amount`
- the engine must not mix these two concepts

In `buy_free` mode:

- `bet_amount = 80 * base bet`
- `bet_level = base bet`

---

## 4. Execution Hierarchy

The engine executes using the current repository hierarchy:

```text
bet -> round -> roll
```

### 4.1 Bet

A bet is the top-level simulated unit.

One bet always begins with one `basic` round.

If free rounds are awarded, they are executed within the same bet.

### 4.2 Round

A round is either:

- `basic`
- `free`

A round contains one or more rolls.

### 4.3 Roll

A roll is either:

- `initial`
- `cascade`

A roll terminates at the **gravity-resolved board state**.

The engine does not treat refill-completed next state as part of the current roll terminal state.

---

## 5. Round Flow

### 5.1 Basic Round

For a basic round, the engine:

1. selects a strip set using `round_strip_set_weights`
2. selects a multiplier profile using `round_multiplier_profile_weights`
3. shuffles strip ids inside the selected strip set once
4. binds the shuffled strip ids to the 6 columns for the round
5. runs the initial roll
6. continues cascades until no further regular-symbol clear occurs
7. settles scatter payout and free-round award

### 5.2 Free Round

Free rounds follow the same roll lifecycle, but use the `free` implementation weights for the current mode.

Free rounds may award additional free rounds.

### 5.3 Free Queue

The engine maintains a free-round queue at the bet level.

Rules:

- a triggering basic round can award free rounds
- free rounds can retrigger additional free rounds
- the queue is consumed until empty

---

## 6. Roll Flow

The current roll lifecycle is:

```text
pre_fill -> filled -> cleared -> gravity
```

### 6.1 `roll_pre_fill_state`

- initial roll: empty 5x6 board
- cascade roll: previous roll's `roll_gravity_state`

### 6.2 `roll_filled_state`

Board after filling all empty positions for the current roll.

### 6.3 `roll_cleared_state`

Board after clearing winning regular symbols.

### 6.4 `roll_gravity_state`

Board after gravity resolution.

This is the terminal board state of the current roll.

---

## 7. Strip and Fill Semantics

### 7.1 Strip Set Selection

At round start, the engine selects one `strip_set_id`.

### 7.2 Column Strip Binding

Within a round:

- strip ids are shuffled once
- the resulting `column_strip_ids` remain fixed for the round

### 7.3 Fill Range Recording

Each roll records:

- `fill_start_indices`
- `fill_end_indices`

Semantics:

- `fill_start_indices` = actual start positions used by this roll's fill
- `fill_end_indices` = actual last-used positions of this roll's fill

These are human-readable fill ranges, not "next pointer" positions.

---

## 8. Regular Win Evaluation

Regular-symbol payout evaluation:

- uses `bet_level`
- is based on the current filled board
- contributes to `roll_win_amount`

The engine then:

- clears winning regular symbols
- keeps scatter and multiplier symbols on the board
- applies gravity
- continues cascade if another roll is warranted

---

## 9. Scatter and Multiplier Semantics

### 9.1 Scatter

Scatter:

- has independent payout mapping from the paytable
- can award free rounds
- is aggregated at round level

### 9.2 Multiplier Symbols

Multiplier symbols:

- sample values from the selected multiplier profile
- contribute to `round_multiplier_increment`
- are recorded roll-by-roll through `roll_multi_symbols_carry`

### 9.3 Carried Multiplier

`carried_multiplier` is a free-game carry concept.

Rules in the current implementation:

- carry starts at `0`
- basic rounds do not carry multiplier into subsequent rounds
- free rounds may accumulate carry across rounds
- current-round settlement uses:
  - `carried_multiplier + round_multiplier_increment`
  - only when the current round generated multiplier increment
- if no multiplier increment is generated in the round:
  - `round_total_multiplier = 1`

---

## 10. Determinism Rules

The engine must satisfy:

```text
(config, seed, engine_version) -> identical execution result
```

This requires:

- seeded RNG only
- fixed RNG call order
- no hidden entropy
- no environment-dependent branching

Weighted selection is treated as distribution-driven, not absolute-weight-driven:

- one-hot weights do not consume extra RNG
- proportionally equivalent integer weights are normalized before selection

---

## 11. Non-Goals

The engine does not:

- compute metrics
- perform validation
- export reports
- adapt probabilities at runtime
- model player behavior
- try to be reusable across unrelated game families

Its scope is the current gameplay prototype only.
