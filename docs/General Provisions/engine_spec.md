
# 1. Scope

This file defines the **execution flow of a single bet**.

* deterministic only
* covers full lifecycle of one bet
* no batch / simulation logic

---

# 2. Inputs

Engine receives:
- normalized config
- RNG (seeded)
- bet_amount   (actual paid amount)
- bet_level    (payout normalization base)

All required game rules MUST be fully defined in normalized config.

## Payout Contract (Critical)

All payout evaluation MUST:

- use bet_level as the normalization base
- never use bet_amount in payout calculation

bet_amount is strictly forbidden in:
- paytable evaluation
- symbol win calculation
- multiplier application

---


# 3. Execution Flow (Single Bet)

## 3.1 Bet Execution

1. Initialize bet:
   - read simulation_mode (normal / buy_free / chance_increase)
   - set:
     - round_type = basic
     - global_multiplier = 0
     - remaining_rounds = 1

2. Execute rounds while remaining_rounds > 0:
   - determine round_type:
     - first round → basic
     - subsequent rounds → free

   - execute round

   - accumulate multiplier:
     - if round_type = free and base symbol win > 0:
         global_multiplier += sum(multiplier from current round)

   - update remaining_rounds:
     - remaining_rounds -= 1
     - if free rounds awarded → remaining_rounds += awarded rounds

3. Aggregate results:
   - compute basic_win_amount
   - compute free_win_amount

---

## 3.2 Round Execution

1. Initialize round:
   - read round_type
   - read global_multiplier

   - read round-level selection weights from config:
     - round_strip_set_weights
     - round_multiplier_profile_weights

   - perform weighted random selection:
     - determine strip_set_id
     - determine multiplier_profile_id

   - establish column-to-strip mapping:
     - shuffle strips within selected strip set
     - assign strips to columns
     - mapping MUST remain fixed throughout the round

   - initialize empty symbol matrix

2. Execute rolls until no further cascade:
   - perform roll
   - continue while new winning combinations are generated

3. Compute base symbol win:
   - sum of base wins from all rolls (before multiplier)

4. Compute multiplier effect:
   - sum_multiplier = sum(multiplier from all multiplier symbols in this round)

   - if sum_multiplier > 0:
     - total_symbol_win = base_symbol_win * (sum_multiplier + global_multiplier)
   - else:
     - total_symbol_win = base_symbol_win

5. Compute scatter win

6. Compute round total win:
   - round_win = total_symbol_win + scatter_win

7. Determine free rounds:
   - if round_type = basic and scatter >= 4:
     - award 15 free rounds
   - if round_type = free and scatter >= 3:
     - award 5 free rounds

---

## 3.3 Roll Execution

1. Read current symbol matrix

2. Fill empty positions:
   - use the round-selected strip_set_id and fixed column-to-strip mapping

   - for each column:
     - sample symbol positions from the assigned strip
     - generate symbols to fill empty positions

   - produce new symbol matrix

   - if multiplier symbols exist:
     - for each multiplier symbol:
       - sample multiplier value from the round-selected multiplier_profile_id
       - assign exactly one value per symbol

3. Evaluate base symbol wins

### Base Symbol Win Evaluation

Base-symbol win evaluation applies only to symbols where:

- `symbol_type == "regular"`

Winning rule:

- all symbols are evaluated by type (symbol_id)
- for each regular symbol type:
  - count the total number of occurrences on the board

Payout rule:

- the symbol count determines the payout lookup key
- payout is read from `PAYTABLE[symbol_id]["payouts"]`
- if the exact count is not defined:
  - the highest defined threshold not exceeding the count is used

Settlement rule:

- each symbol type is evaluated independently
- multiple symbol types may generate wins in the same roll
- total roll base win is the sum of all symbol-type payouts evaluated on `bet_level`

Non-regular symbols:

- `scatter` symbols do not participate in base-symbol payout evaluation
- `multiplier` symbols do not participate in base-symbol payout evaluation

4. Clear winning symbols:
   - calculate base win

5. Apply gravity:
   - remaining symbols fall
   - produce updated symbol matrix

---

# 4. Config-to-Engine Mapping

This section defines how the engine reads and uses configuration data.

The goal is to ensure that:

- all runtime behavior is fully determined by config
- all config usage is explicit and deterministic
- no implicit or hidden logic is introduced in implementation

This section is normative unless explicitly stated otherwise.

---

## 4.1 Simulation Mode Resolution

The engine reads from:

```python
SIMULATION_MODE
```

For the selected mode:

* resolve:

  * `mode_name`
  * `bet_cost_multiplier`

The engine MUST compute:

* `bet_amount = base_bet * bet_cost_multiplier`
* `bet_level = base_bet`

Rules:

* `bet_amount` is used for cost-based calculations only
* `bet_level` is used for all payout evaluation
* these two must not be mixed

---

## 4.2 Round Initialization Inputs

At the start of each round, the engine reads:

```python
IMPLEMENTATION_CONFIG[mode][round_type]
```

The engine reads:

- `round_strip_set_weights`
- `round_multiplier_profile_weights`

These define:

- the selection distributions for strip set selection
- the selection distributions for multiplier profile selection

Rules:

- these fields provide weight distributions only, not final selections
- engine MUST perform a weighted random selection to determine:
  - `strip_set_id`
  - `multiplier_profile_id`

- selection must be:
  - RNG-driven
  - performed once per round
  - independent across rounds
  - deterministic given seed

---

## 4.3 Strip Set Selection and Usage

The engine selects a `strip_set_id` based on:

```python
round_strip_set_weights
```

Selection rules:

* exactly one strip set is selected per round
* selection occurs once at round start

Usage rules:

* within the same round:

  * strip set MUST NOT change
  * column-to-strip mapping MUST NOT change during cascades:

  * refill MUST reuse the same strip set
  * refill MUST NOT reshuffle strip order

This ensures that:

* all rolls within a round share the same strip context
* cascade behavior is reproducible and bounded

---

## 4.4 Multiplier Profile Selection

The engine selects a `multiplier_profile_id` based on:

```python
round_multiplier_profile_weights
```

Mapping:

```python
multiplier_profile_id -> MULTIPLIER_DATA['weight'][id]
```

Rules:

* exactly one multiplier profile is selected per round
* the selected profile is fixed for the entire round
* multiplier values in rolls must be sampled from this profile

No runtime switching of multiplier profiles is allowed within a round.

---

## 4.5 Symbol Identity and Type Resolution

Symbol identity and behavior MUST be derived from:

```python
PAYTABLE
```

Specifically:

* `symbol_type` defines behavior:

  * regular
  * scatter
  * multiplier

Rules:

* engine MUST NOT redefine symbol categories elsewhere
* all behavior branching must be based on `symbol_type`

---

## 4.6 Multiplier Value Assignment

Multiplier symbols are identified via:

```python
symbol_type == "multiplier"
```

For each multiplier symbol:

* a value must be sampled from the selected multiplier profile

Rules:

* values must come from `MULTIPLIER_DATA['value']`
* weights must come from the selected profile
* each multiplier symbol generates exactly one value

---

## 4.7 Scatter Evaluation and Free Round Trigger

Scatter symbols are identified via:

```python
symbol_type == "scatter"
```

Rules for free round triggers:

* if `round_type == basic` and scatter count ≥ 4:

  * award 15 free rounds

* if `round_type == free` and scatter count ≥ 3:

  * award 5 free rounds

Rules:

* thresholds must not be configurable at runtime
* trigger logic must not depend on previous outcomes beyond canonical state

---

## 4.8 Invariants

The following must hold:

* all selections are:

  * RNG-driven
  * deterministic given seed
  * independent of outcome

* no configuration field may be:

  * conditionally switched at runtime based on results
  * dynamically adjusted based on player behavior

* config defines:

  * possibility space

* engine defines:

  * execution path within that space

---

## 4.9 Example (Non-Normative)

Example:

If:

* `mode = 2`
* `round_type = basic`

Then engine reads:

```python
IMPLEMENTATION_CONFIG[2]["basic"]
```

From which it:

* performs weighted random selection using `round_strip_set_weights`
  - determines `strip_set_id`

* performs weighted random selection using `round_multiplier_profile_weights`
  - determines `multiplier_profile_id`

This example is illustrative only and does not define additional rules.

---

# 5. State Progression

* each roll produces a new state
* cascade uses previous roll result as next input
* round state is updated incrementally
* bet state accumulates round results

---

# 6. Output Boundary

After execution, engine MUST produce:

* bet-level outcome
* ordered round sequence
* ordered roll sequence within each round
* state progression across rolls
* all payout sources required to reconstruct outcomes

Output MUST be sufficient for:

* deterministic replay
* canonical recording

---

# 7. Determinism

The following must hold:

(config, seed) -> identical execution result

Payout normalization MUST be based on bet_level.
Return-based metrics MUST be based on bet_amount.

---

# 8. Forbidden Patterns

The following are NOT allowed:

* reroll
* result filtering
* runtime probability adjustment
* player-dependent logic
* hidden state mutation outside defined flow

---

# Summary

Engine executes a bet as:

* deterministic
* state-driven
* round-based
* roll-resolved

It produces a complete, ordered execution path for canonical recording.







