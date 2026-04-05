# canonical_result.md (execution spec)

## 0. Scope

This file defines the **exact schema and constraints** for CanonicalResult.

It is **not documentation**, it is a **build contract**.

---

## 1. Top-Level Object

```python
CanonicalResult = {
    "run": RunMeta,
    "wagers": list[WagerRecord],
    "summary": RunSummary
}
```

---

## 2. RunMeta (mandatory)

```python
RunMeta = {
    "run_id": str,
    "config_id": str,
    "config_version": str,
    "engine_version": str,
    "schema_version": str,

    "mode": str,
    "seed": int,
    "stake_amount": float,
    "total_wagers": int,

    "timestamp": str
}
```

### Rules

- MUST be present
- MUST be sufficient for replay
- MUST NOT rely on filename for metadata

---

## 3. WagerRecord (mandatory)

```python
WagerRecord = {
    "wager_id": int,

    "bet": float,
    "total_win": float,

    "is_hit": bool,
    "trigger_flags": list[str],

    "mode": str,

    "round_count": int,
    "rounds": list[RoundRecord],

    "final_state": GameState
}
RoundRecord = {
    "round_id": int,
    "round_type": str,   # "base" | "feature"

    "round_win": float,

    "roll_count": int,
    "rolls": list[RollRecord],

    "round_multiplier_total": float | None
}
```

### Rules

- 1 wager = 1 complete top-level outcome unit
- total_win MUST equal sum of round wins
- For each round: roll_count MUST match len(rolls)

---

## 4. RollRecord (core)

```python
RollRecord = {
    "roll_id": int,

    "state_type": str,

    "pre_state": GameState,
    "post_state": GameState,

    "roll_win": float,
    "accumulated_round_win": float,

    "events": list[str],

    "reel_set_id": str | None,
    "multiplier_profile_id": str | None
}
```

### Allowed state_type values

- "round_start"
- "initial_roll"
- "cascade_roll"
- "feature_trigger"
- "round_end"

### Rules

- roll_id MUST be ordered and continuous
- pre_state → post_state MUST form a valid transition
- accumulated_round_win MUST be monotonic

---

## 5. GameState (structure)

```python
GameState = {
    "board": list[list[int]],

    "pending_round_multiplier": float | None,

    "feature_state": FeatureState | None
}
```

---

## 6. FeatureState (optional but structured)

```python
FeatureState = {
    "feature_type": str,

    "remaining_rounds": int,
    "awarded_rounds": int,

    "is_active": bool
}
```

### Rules

- MUST be explicit if feature exists
- MUST NOT hide feature logic in other fields

---

## 7. RunSummary (optional but recommended)

```python
RunSummary = {
    "total_bet": float,
    "total_win": float,
    "wager_count": int
}
```

### Rules

- MUST be recomputable from wagers
- MUST NOT be primary source

---

## 8. Strict Constraints

### 8.1 No control semantics

The following are FORBIDDEN in canonical:

- waterline
- control_level
- protect / reroll / range filter
- any runtime adjustment fields

---

### 8.2 No interpretation

Canonical MUST NOT include:

- RTP
- hit rate
- statistical metrics
- pass/fail flags

---

### 8.3 Determinism

The following must hold:

```
(config, seed, engine_version) → identical CanonicalResult
```

---

### 8.4 Completeness

Canonical MUST allow:

- replay any wager
- replay any round
- replay any roll
- reconstruct full state path

---

## 9. Serialization Rules

- Internal: structured object (dict / dataclass)
- Export: JSON (preferred) or table (derived)

### DO NOT

- store complex objects as string repr
- rely on implicit structure

---

## 10. Minimal API Contract

```python
run_simulation(config, seed) -> CanonicalResult
```

---

## 11. Implementation Checklist

Before accepting a CanonicalResult:

- [ ] run meta complete
- [ ] wagers count matches total_wagers
- [ ] round_id continuous per wager
- [ ] roll_id continuous per round
- [ ] accumulated_round_win correct
- [ ] no forbidden fields
- [ ] replay produces identical result

---

## Summary

CanonicalResult is:

- structured
- deterministic
- neutral
- complete

It is the **only valid input** for metrics and validation.
