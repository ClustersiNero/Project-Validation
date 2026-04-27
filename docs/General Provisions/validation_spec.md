# Validation Specification

## 0. Purpose

This document defines the validation layer for the current repository.

Pipeline position:

```text
config -> engine -> canonical -> metrics -> validation
```

Validation:

- MUST evaluate only
- MUST NOT modify upstream data
- MUST NOT recompute engine outcomes
- MUST NOT rewrite metric values

---

## 1. Implemented Validation Categories

The current repository implements exactly three validation categories:

| Category | Input | Purpose |
|---|---|---|
| Canonical validation | `CanonicalResult`, config | Structural and gameplay-contract checks |
| Metrics validation | `MetricsBundle` | Basic metrics sanity checks |
| Statistical validation | `MetricsBundle`, `ValidationRules` | Expectation and CI-based checks |

Baseline regression validation is not implemented in this repository.

---

## 2. Core Report Types

### 2.1 Canonical / Metrics Validation Report

```python
ValidationReport = {
    "is_valid": bool,
    "issues": list[str],
}
```

### 2.2 Statistical Check Result

```python
StatisticalCheckResult = {
    "metric_path": str,
    "check_type": str,
    "verdict": str,              # "pass" or "fail"
    "observed": float | None,
    "expected_value": float | None,
    "expected_range": tuple[float, float] | None,
    "deviation": float | None,
    "notes": str,
}
```

### 2.3 Statistical Validation Report

```python
StatisticalValidationReport = {
    "is_valid": bool,
    "statistical_checks": list[StatisticalCheckResult],
}
```

---

## 3. Canonical Validation

Canonical validation consumes only:

- `CanonicalResult`
- config

It checks:

- required field presence
- count consistency
- config-to-canonical id validity
- payout aggregation consistency
- ordering invariants
- `round_type` / `roll_type` validity
- carried-multiplier continuity
- board-state continuity across cascades

### Required Canonical Fields

Simulation metadata:

- `simulation_id`
- `config_id`
- `config_version`
- `engine_version`
- `schema_version`
- `mode`
- `seed`
- `bet_amount`
- `bet_level`
- `total_bets`
- `timestamp`

Bet record:

- `bet_id`
- `bet_win_amount`
- `basic_win_amount`
- `free_win_amount`
- `round_count`
- `rounds`
- `bet_final_state`

Round record:

- `round_id`
- `round_type`
- `round_win_amount`
- `base_symbol_win_amount`
- `carried_multiplier`
- `round_multiplier_increment`
- `round_total_multiplier`
- `round_scatter_increment`
- `award_free_rounds`
- `scatter_win_amount`
- `roll_count`
- `rolls`
- `round_final_state`

Roll record:

- `roll_id`
- `roll_win_amount`
- `roll_type`
- `strip_set_id`
- `multiplier_profile_id`
- `column_strip_ids`
- `fill_start_indices`
- `fill_end_indices`
- `roll_pre_fill_state`
- `roll_filled_state`
- `roll_cleared_state`
- `roll_gravity_state`
- `roll_multi_symbols_num`
- `roll_multi_symbols_carry`
- `roll_scatter_symbols_num`

### Core Invariants

- `simulation_metadata.total_bets == len(bets)`
- `bet.round_count == len(bet.rounds)`
- `round.roll_count == len(round.rolls)`
- round ids are strictly ascending within a bet
- roll ids are strictly ascending within a round
- `round_type` is exactly `basic` or `free`
- first roll of a round is `initial`; later rolls are `cascade`
- `round_total_multiplier == 1` when `round_multiplier_increment == 0`
- if a round is `basic`, `carried_multiplier == 0`
- free-round carried multiplier must match prior free carry state
- within a round:
  - `current_roll.column_strip_ids == previous_roll.column_strip_ids`
  - `current_roll.roll_pre_fill_state == previous_roll.roll_gravity_state`

### Aggregation Rules

For each round:

```text
round_win_amount == base_symbol_win_amount * round_total_multiplier + scatter_win_amount
```

For each bet:

```text
bet_win_amount == sum(round.round_win_amount for round in rounds)
bet_win_amount == basic_win_amount + free_win_amount
```

---

## 4. Metrics Validation

Metrics validation consumes only:

- `MetricsBundle`

It checks:

- required metric presence
- valid sample sizes
- valid standard-deviation/null handling
- non-negative and bounded frequency-style metrics where applicable

It is a sanity layer, not a target-comparison layer.

---

## 5. ValidationRules

`ValidationRules` are externally supplied.

```python
MetricRule = {
    "expected_value": float | None,
    "expected_range": tuple[float, float] | None,
    "z_value": float | None,
}

ValidationRules = {
    "metrics": dict[str, MetricRule],
    "metrics_by_mode": dict[str, dict[str, MetricRule]],
}
```

Rules:

- metric paths MUST use full nested `MetricsBundle...` paths
- flat metric names are forbidden
- `metrics_by_mode` overrides are mode-scoped statistical targets
- thresholds MUST come from rules, not from validation logic

---

## 6. Statistical Validation

Statistical validation consumes only:

- `MetricsBundle`
- `ValidationRules`

It supports:

### 6.1 Expected Value Check

For CI-eligible `StatisticalMetric` leaves:

```text
pass if abs(observed - expected_value) <= z * (standard_deviation / sqrt(sample_size))
```

### 6.2 Range Check

```text
pass if lower <= observed <= upper
```

### 6.3 Invalid Rule Handling

Validation MUST fail a statistical check if:

- `z_value` is supplied for a non-`StatisticalMetric` leaf
- `standard_deviation` is `null`
- `sample_size < 2`

No default epsilon, zero, or fallback CI behavior is permitted.

---

## 7. Global Rules

- canonical validation MUST NOT consume `MetricsBundle`
- metrics validation MUST NOT consume `CanonicalResult`
- statistical validation MUST NOT consume `CanonicalResult`
- validation MUST NOT call engine logic
- validation MUST be deterministic for fixed inputs
- no `"warn"` verdict state is permitted for statistical checks

---

## 8. Non-Goals

This layer does not:

- define game rules
- generate canonical data
- compute metrics
- prove fairness
- model player behavior
- implement baseline regression tooling
