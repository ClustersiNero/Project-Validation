# Purpose

This specification defines a **validation-oriented slot math architecture contract** for reproducible and inspectable outcome processing.

The architecture is designed to make game behavior:

- reproducible
- inspectable
- measurable
- validation-ready

It is not a simulation-only or reporting-first document.

---

# Core Principle

> Outcomes must be generated first, then measured, then validated.

Pipeline:

config -> engine -> canonical result -> metrics -> validation -> optional export

---

# Naming Contract (Bet-Only, Hierarchical)

This specification enforces a **strict hierarchical naming system**:

**Bet → Round → Roll**

All naming MUST align with this hierarchy.

## 1. Bet Level (Top-Level Unit)

Required:

* unit name: `bet`
* collection: `bets`

* bet_amount = actual paid amount for this bet
* bet_level  = payout normalization base (used for paytable and win multiple)

Forbidden:

* any alternative concepts representing the same level, including:

  * `stake`
  * `wager`

### Amount System Invariant

The system uses a dual-base model:

- bet_amount:
  used for cost-based ratios (RTP, return)

- bet_level:
  used for all payout calculations (paytable, win multiple)

All payout generation MUST use bet_level.
All return-based metrics MUST use bet_amount.

These two MUST NEVER be mixed.

---

## 2. Round Level (Within Bet)

Definition:

* A `round` is a sub-unit within a `bet`

Forbidden:

* any naming that breaks hierarchy or reuses other layers, including:

  * `spin`
  * `bet`

---

## 3. Roll Level (Within Round)

Definition:

* A `roll` is a sub-unit within a `round`

Forbidden:

* any naming that overlaps with higher or ambiguous layers, including:

  * `round`
  * `step`

---

### Global Rule

* Naming MUST be **hierarchy-consistent and non-overlapping**
* Each layer represents a **unique semantic level**
* Parallel terminology across layers is strictly prohibited

---

# Layer Definitions

## 1. CLI / Runner

Input:
- runtime parameters

Output:
- pipeline execution trigger

Responsibilities:
- orchestrate full pipeline
- select config and mode

---

## 2. Config

Input:
- game parameters
- simulation parameters

Output:
- normalized config

Responsibilities:
- provide explicit, versionable inputs
- ensure reproducibility

---

## 3. Engine

Input:
- config
- RNG (seeded)

Output:
- raw execution results

Responsibilities:
- generate outcomes deterministically
- apply game logic and payout mapping

Rules:
- no reroll
- no filtering
- no runtime manipulation

---

## 4. Canonical Result

The canonical result is the **single source of truth** for downstream processing.

It must preserve both:
- final outcomes
- round / roll-level state transitions (if applicable)

Canonical MUST NOT contain interpretive metrics or validation outputs.
This file defines layer responsibilities and cross-layer contracts.
The exact CanonicalResult field schema is defined by canonical_spec.md.

### 4.1 Schema

#### 4.1.1 Simulation Metadata

- simulation_id
- config_id
- config_version
- engine_version
- schema_version
- mode
- seed
- bet_amount      (actual paid amount per bet)
- bet_level       (payout normalization base)
- total_bets
- timestamp

Each simulation contains one or more bets.
mode indicates the entry mode of the bet (e.g. normal, buy_free, chance_increase)

#### 4.1.2 Result Records

##### 4.1.2.1 Bet Records

###### 4.1.2.1.1 Field Name

- bet_id
- bet_win_amount
- basic_win_amount
- free_win_amount
- round_count
- bet_final_state
- rounds

###### 4.1.2.1.2 Structure

Each bet record contains one or more round records in `rounds`.

---

##### 4.1.2.2 Round Records

###### 4.1.2.2.1 Field Name

- round_id
- round_type
- round_win_amount

- base_symbol_win_amount
- carried_multiplier
- round_multiplier_increment
- round_total_multiplier

- round_scatter_increment
- award_free_rounds
- scatter_win_amount

- roll_count
- round_final_state
- rolls

###### 4.1.2.2.2 Structure

Each round record belongs to one bet record.
Each round record contains one or more roll records in `rolls`.
`round_total_multiplier` records the actual settlement multiplier factor applied to round-level `base_symbol_win_amount`.
It MUST be 1 when the current round generates no `round_multiplier_increment`.

---

##### 4.1.2.3 Roll Records

###### 4.1.2.3.1 Field Name

- roll_id
- roll_win_amount
- roll_type

- strip_set_id
- multiplier_profile_id

- roll_filled_state
- roll_final_state

- roll_multi_symbols_num
- roll_multi_symbols_carry

- roll_scatter_symbols_num

###### 4.1.2.3.2 Structure

Each roll record belongs to one round record.
Scatter and multiplier symbols may remain present across rolls, but round-level aggregation MUST count each symbol instance at most once within the same round. Counting is based on persisted board-state instances observed across rolls

**Symbol instance identity**: A symbol instance is uniquely identified by `(first_observed_roll_id, first_observed_row, first_observed_col)`. Gravity movement within subsequent cascades does not create a new instance.


### 4.2 Invariants

- deterministic
- complete
- neutral
- no validation or interpretive data

---

## 5. Metrics Layer

Input:
- CanonicalResult

Output:
- MetricsBundle

Responsibilities:
- compute descriptive statistics only

Core metrics:
- empirical RTP
- hit frequency
- payout distribution
- tail concentration
- optional feature metrics

Rule:
- Metrics MUST NOT modify canonical data
- no pass/fail logic here
- Metrics MUST compute all aggregates from raw canonical data

---

## 6. Validation

### 6.1 Structure

Validation MUST ensure schema compatibility before any evaluation.

#### 6.1.1 Structural Validation

Input:
- CanonicalResult
- Config

Responsibilities:
- verify structural correctness
- verify mapping consistency
- detect logical violations
- verify schema_version compatibility
- verify engine_version consistency
- verify config_version consistency

Examples:
- round_count must equal the number of recorded rounds
- payout aggregates must match the sum of their child records
- referenced IDs must exist in config

Output:
- spec validation report

---

#### 6.1.2 Statistical Validation

Input:
- MetricsBundle
- expected ranges / CI

Responsibilities:
- evaluate deviation from expected values
- apply confidence-based checks

Output:
- statistical validation report

---

#### 6.1.3 Baseline Regression Validation

Input:
- MetricsBundle
- baseline metrics

Responsibilities:
- detect drift across versions or configs
- ensure stability over iterations

Output:
- regression validation report

---

### 6.2 Output

All checks produce:

- observed value
- expected value / range
- deviation
- verdict
- notes

---


# Pipeline Interface & Artifact

This section defines both:
- the output structure of the pipeline
- the minimal callable interfaces

## Pipeline Artifact

```python
PipelineArtifact = {
    canonical_result,
    metrics_bundle,
    validation_report,
    optional_export_refs
}
```

Rule:
- simulation_metadata MUST be sourced from canonical_result

---

## Minimal Core Interfaces

```python
run_simulation(config, seed) -> CanonicalResult

compute_metrics(result) -> MetricsBundle

# Validation is composed of three independent categories:
validate_structure(canonical_result, config) -> StructuralValidationReport
validate_statistics(metrics, validation_rules) -> StatisticalValidationReport
validate_regression(metrics, baseline_metrics) -> RegressionValidationReport

# Full validation entry point aggregates all three:
run_validation(canonical_result, config, metrics, validation_rules, baseline_metrics) -> ValidationReport

run_pipeline(config, seed) -> PipelineArtifact
```

The three validation categories are independent. `validate_structure` consumes `CanonicalResult` and config only. `validate_statistics` consumes `MetricsBundle` and rules only. `validate_regression` consumes `MetricsBundle` and baseline metrics only. None of them modify upstream data.

---

# System Constraints

## Dependency Rules

- engine does not depend on metrics or validation
- metrics does not depend on validation
- validation does not modify upstream data
- export does not affect core logic

## Non-Goals

- no runtime control or adaptive outcome logic
- no mixing generation, measurement, and validation
- no fairness proof via simulation alone
- no live behavior prediction

## Special Notes

In buy_free mode:

- bet_amount = 80 × base bet
- bet_level = base bet

This ensures:

- cost-based metrics reflect actual payment
- payout-based metrics remain comparable across modes

---