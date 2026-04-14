
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
   - generate symbols based on configuration
   - produce new symbol matrix

   - if multiplier symbols exist:
     - assign multiplier values based on configuration

3. Evaluate base symbol wins and determine whether a win occurs

4. Clear winning symbols:
   - calculate base win

5. Apply gravity:
   - remaining symbols fall
   - produce updated symbol matrix

---

# 4. State Progression

* each roll produces a new state
* cascade uses previous roll result as next input
* round state is updated incrementally
* bet state accumulates round results

---

# 5. Output Boundary

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

# 6. Determinism

The following must hold:

(config, seed) -> identical execution result

Payout normalization MUST be based on bet_level.
Return-based metrics MUST be based on bet_amount.

---

# 7. Forbidden Patterns

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







