# Architecture Specification

## 0. Purpose

This document defines the current architecture contract for this repository.

This repository is a **Gate of Olympus-anchored, validation-first slot math prototype**. The architecture is designed to make game behavior:

- deterministic
- inspectable
- measurable
- validation-ready

It is not a simulation-only or reporting-first document.

---

## 1. Core Principle

> Outcomes must be generated first, then recorded, then measured, then validated.

Pipeline:

```text
config -> engine -> canonical result -> metrics -> validation -> optional export
```

---

## 2. Naming Contract

This repository uses a strict hierarchical naming system:

```text
Bet -> Round -> Roll
```

Required:

- top-level unit: `bet`
- nested unit: `round`
- nested unit within round: `roll`

Forbidden alternatives:

- `stake`
- `wager`
- `spin`
- `step`

### Amount System Invariant

The system uses a dual-base model:

- `bet_amount`
  - actual paid cost per bet
  - used for return-based ratios such as RTP
- `bet_level`
  - payout normalization base
  - used for paytable evaluation and win multiples

All payout generation MUST use `bet_level`.
All return-based metrics MUST use `bet_amount`.

These two MUST NEVER be mixed.

---

## 3. Layer Definitions

### 3.1 CLI / Runner

Responsibilities:

- accept runtime parameters
- trigger the full pipeline
- optionally write exports

### 3.2 Config

Responsibilities:

- provide explicit, versionable inputs
- define the possibility space for simulation
- ensure reproducibility through fixed config + fixed seed

### 3.3 Engine

Responsibilities:

- generate outcomes deterministically
- apply the current game logic
- produce raw execution results

Rules:

- no reroll
- no filtering
- no runtime manipulation
- no player-dependent logic

### 3.4 Canonical Result

The canonical result is the single source of truth for downstream processing.

It preserves:

- simulation metadata
- final economic outcomes
- round / roll execution structure
- board-state progression required for audit and reconstruction

Canonical MUST NOT contain:

- interpretive metrics
- pass/fail judgements
- validation outputs

### 3.5 Metrics

Responsibilities:

- compute descriptive statistics only
- read canonical data only

Metrics MUST NOT:

- modify canonical data
- perform validation judgement
- infer hidden engine state

### 3.6 Validation

Responsibilities:

- validate canonical structure and gameplay contract
- validate metric sanity
- validate statistical expectations against explicit rules

Validation MUST NOT:

- mutate upstream data
- recompute engine outcomes
- redefine metric values

### 3.7 Export

Responsibilities:

- provide inspection-oriented outputs
- provide tuning-oriented outputs

Export MUST be read-only relative to canonical and metrics data.

---

## 4. Canonical Result Schema Summary

### 4.1 Simulation Metadata

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

### 4.2 Bet Record

- `bet_id`
- `bet_win_amount`
- `basic_win_amount`
- `free_win_amount`
- `round_count`
- `bet_final_state`
- `rounds`

### 4.3 Round Record

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
- `round_final_state`
- `rolls`

### 4.4 Roll Record

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

---

## 5. Validation Model

The current repository implements three validation categories:

### 5.1 Canonical Validation

Input:

- `CanonicalResult`
- config

Responsibilities:

- structural consistency
- aggregation consistency
- gameplay-contract checks

### 5.2 Metrics Validation

Input:

- `MetricsBundle`

Responsibilities:

- sanity checks on metric shape and basic validity

### 5.3 Statistical Validation

Input:

- `MetricsBundle`
- `ValidationRules`

Responsibilities:

- evaluate deviation from explicit targets
- apply confidence-based checks

### 5.4 Not Implemented Here

Baseline regression validation is intentionally not part of the current implementation in this repository.

---

## 6. Pipeline Artifact

```python
PipelineResult = {
    canonical_result,
    metrics_bundle,
    canonical_validation,
    metrics_validation,
    statistical_validation,   # optional when rules are not supplied
}
```

---

## 7. Minimal Interfaces

```python
run_simulation(config) -> CanonicalResult
compute_metrics(result) -> MetricsBundle
validate_canonical(canonical_result, config) -> ValidationReport
validate_metrics(metrics) -> ValidationReport
validate_statistics(metrics, validation_rules) -> StatisticalValidationReport
run_pipeline(config, validation_rules=None) -> PipelineResult
```

---

## 8. System Constraints

### Dependency Rules

- engine does not depend on metrics or validation
- metrics does not depend on validation
- validation does not modify upstream data
- export does not affect core logic

### Non-Goals

- no runtime control or adaptive outcome logic
- no player behavior prediction
- no fairness proof via simulation alone
- no generic multi-game engine/plugin framework

### Mode Notes

In `buy_free` mode:

- `bet_amount = 80 * base bet`
- `bet_level = base bet`

This keeps:

- cost-based metrics grounded in actual payment
- payout-based metrics comparable across modes
