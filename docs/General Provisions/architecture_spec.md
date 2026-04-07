# Architecture Specification

## Purpose

This specification defines a **validation-oriented slot math architecture contract** for reproducible and inspectable outcome processing.

The architecture is designed to make game behavior:

- reproducible
- inspectable
- measurable
- validation-ready

It is not a simulation-only or reporting-first document.

---

## Core Principle

> Outcomes must be generated first, then measured, then validated.

Pipeline:

config -> engine -> canonical result -> metrics -> validation -> optional export

---

## Naming Contract (Bet-Only)

This specification is Bet-only for top-level event naming.

Required naming:
- top-level unit: bet
- hierarchy: Bet -> Round -> Roll
- canonical top-level collection: bets
- metrics sample unit: bet
- validation sample unit: bet
- amount field naming uses bet terms (for example: bet_amount)

### Forbidden Parallel Terminology (Formal Terms)

The following formal terms are forbidden in this specification:
- wager
- wagers
- wager_id
- wager_amount
- total_wagers
- stake
- stakes
- stake_amount

---

## High-Level Architecture

```
CLI
  ↓
Config
  ↓
Engine
  ↓
Canonical Result
  ↓
Metrics
  ↓
Validation
  ↓
Optional Export
```

---

## Layer Definitions

### 1. CLI / Runner

Input:
- runtime parameters

Output:
- pipeline execution trigger

Responsibilities:
- orchestrate full pipeline
- select config and mode

---

### 2. Config

Input:
- game parameters
- simulation parameters

Output:
- normalized config

Responsibilities:
- provide explicit, versionable inputs
- ensure reproducibility

---

### 3. Engine

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

## Canonical Result Schema

The canonical result is the **single source of truth** for downstream processing.

It must preserve both:
- final outcomes
- round / roll-level state transitions (if applicable)

### Structure

#### 1. Run Metadata

- run_id
- config_id
- config_version
- engine_version
- mode
- seed
- bet_amount
- total_bets
- timestamp

#### 2. Bet Records

For each bet:
- bet_id
- total_bet
- total_win
- trigger_flags
- summary result

#### 3. Round / Roll State Transitions

Each bet contains one or more rounds.
Each round contains ordered rolls.

For each round:
- round_id
- round_type
- round_total_win
- roll_count
- rolls

For each roll:
- roll_id
- board / symbols
- roll_win
- cascade / refill result
- feature-related events
- reel_set_id
- multiplier_profile_id

#### 4. Aggregated Summary (optional)

- total_bet
- total_win
- bet_count

---

## Metrics Layer

CanonicalResult uses a bet -> rounds -> rolls hierarchy.

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
- no pass/fail logic here
---

## Validation Structure

### 1. Structural Validation

Input:
- CanonicalResult
- Config

Responsibilities:
- verify structural correctness
- verify mapping consistency
- detect logical violations

Output:
- spec validation report

---

### 2. Statistical Validation

Input:
- MetricsBundle
- expected ranges / CI

Responsibilities:
- evaluate deviation from expected values
- apply confidence-based checks

Output:
- statistical validation report

---

### 3. Baseline Regression Validation

Input:
- MetricsBundle
- baseline metrics

Responsibilities:
- detect drift across versions or configs
- ensure stability over iterations

Output:
- regression validation report

---

## Validation Output

All checks produce:

- observed value
- expected value / range
- deviation
- verdict
- notes

---

## Pipeline Artifact

```python
PipelineArtifact = {
    canonical_result,
    metrics_bundle,
    validation_report,
    run_metadata,
    optional_export_refs
}
```

---

## Minimal Core Interfaces

```python
run_simulation(config) -> CanonicalResult

compute_metrics(result) -> MetricsBundle

validate_metrics(metrics, rules) -> ValidationReport

run_pipeline(config) -> PipelineArtifact
```

---

## Dependency Rules

- engine does not depend on metrics or validation
- metrics does not depend on validation
- validation does not modify upstream data
- export does not affect core logic

---

## Non-Goals

- no runtime control or adaptive outcome logic
- no mixing generation, measurement, and validation
- no fairness proof via simulation alone
- no live behavior prediction

---

## Summary

Core flow:

config -> engine -> canonical result -> metrics -> validation
