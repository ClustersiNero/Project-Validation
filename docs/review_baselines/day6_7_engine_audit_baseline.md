# DAY6~7 Engine Baseline (Short)

Read this together with `copilot-instructions.md`.

## Status

DAY6~7 engine work is **complete and accepted**.

Do not reopen this phase unless the current repository code shows a new concrete contradiction.

---

## Accepted Engine State

- config → engine handoff is established
- seeded deterministic RNG exists
- minimal wager → base/free round → cascade/refill → payout path exists
- `wager_cost_multiplier` already affects actual wager cost
- free-game global multiplier behavior is definition-driven
- `feature_buy` is accepted as entering through base-round flow
- current strip assignment / refill behavior is accepted as implemented
- current engine-internal recording cleanup is accepted

---

## Accepted Implementation Decisions

### Feature-buy
Accepted:
- does **not** skip base-round execution
- guarantee characteristics come from predefined config / strip behavior
- this is **not** runtime shortcut logic

### Strip assignment / refill
Accepted:
- round first selects a strip set
- strip ids inside that strip set are shuffled once at round start
- shuffled strip ids are assigned to columns in order
- refill reuses the same round-selected strip set
- refill reuses the same column-strip mapping inside the round

### Stake terminology
Accepted current engine meaning:
- `EngineRunResult.stake_amount` = raw stake input
- `EngineWagerRecord.bet` = actual wager amount after mode multiplier
- `total_bet` = accumulated real wager cost

This is accepted for now and should not trigger engine reopening by itself.

---

## Do Not Reopen as DAY6~7 Work

The following are **not** DAY6~7 leftovers:

- canonical schema expansion
- replay-oriented canonical cleanup
- metrics bundle work
- validation rule work
- downstream formatting cleanup driven by canonical / metrics / validation needs

---

## Hard Boundaries

### Engine must remain
- deterministic
- generation-only
- free of runtime control logic
- free of player-dependent logic

### Do not introduce
- reroll
- filter
- protect
- control_level
- pool
- runtime probability adjustment
- player-state-dependent outcome shaping

### Do not mix layers
- engine must not do canonical interpretation work
- engine must not do metrics work
- engine must not do validation work

---

## Usage Rule

When giving Copilot follow-up implementation tasks related to engine work, explicitly tell it to read:

- `copilot-instructions.md`
- `docs/review_baselines/day6_7_engine_audit_baseline.md`

and treat them as the accepted baseline.

If a new task would reopen an already accepted engine decision, Copilot must first show the concrete repository-backed contradiction.