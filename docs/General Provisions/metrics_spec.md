# Metrics Specification

## 0. Purpose

This document defines the metrics layer used by the current repository.

Metrics transform `CanonicalResult` into structured, reproducible, descriptive observations.

This layer is:

- descriptive only
- deterministic
- downstream of canonical
- upstream of validation

It is not a judgement layer.

---

## 1. Core Principle

> Metrics describe observed behavior from canonical records. They do not judge correctness.

Required rules:

- metrics are computed only from `CanonicalResult`
- metrics do not modify canonical data
- metrics do not infer hidden engine states
- metrics do not contain pass/fail logic

Pipeline position:

```text
config -> engine -> canonical -> metrics -> validation
```

---

## 2. Naming Contract

This repository uses the same hierarchy as the rest of the system:

```text
Bet -> Round -> Roll
```

Forbidden alternatives:

- `stake`
- `wager`
- `spin`
- `step`

---

## 3. StatisticalMetric

CI-eligible metrics use a unified leaf type:

```python
StatisticalMetric = {
    "observed": float | None,
    "standard_deviation": float | None,
    "sample_size": int,
}
```

Rules:

- `observed` is the point estimate
- `standard_deviation` is Bessel-corrected sample standard deviation when defined
- `sample_size` is explicit per metric

### Zero / Small Sample Contract

- `sample_size == 0`
  - `observed = null`
  - `standard_deviation = null`
- `sample_size == 1`
  - `observed` is defined
  - `standard_deviation = null`
- `sample_size >= 2`
  - both are computed normally

Only `StatisticalMetric` leaves are CI-eligible for statistical validation.

---

## 4. Input / Output

Input:

```python
CanonicalResult
```

Output:

```python
MetricsBundle = {
    "meta": MetricsMeta,
    "bet_metrics": BetMetrics,
    "round_metrics": RoundMetrics,
    "roll_metrics": RollMetrics,
}
```

`MetricsBundle` must be fully reproducible from canonical input alone.

---

## 5. MetricsMeta

`MetricsMeta` is a metadata projection plus whole-run totals.

```python
MetricsMeta = {
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
    "total_bet_amount": float,
    "total_bet_win_amount": float,
}
```

Rules:

- metadata fields are projected from canonical simulation metadata
- totals are recomputed from canonical records

---

## 6. General Calculation Rules

### 6.1 Amount Bases

- RTP-like return ratios use `bet_amount`
- payout normalization and win multiples use `bet_level`

### 6.2 Hit Definitions

- bet hit: `bet_win_amount > 0`
- round hit: `round_win_amount > 0`
- roll hit: `roll_win_amount > 0`

### 6.3 Round Partitions

Current round partitions:

- `basic_rounds`
- `free_rounds`

### 6.4 Roll Partitions

Current roll partitions:

- `initial`
- `cascade`

---

## 7. Metrics Groups

### 7.1 Bet Metrics

Current bet-level metrics include:

- `empirical_rtp`
- `basic_rtp`
- `free_rtp`
- `bet_hit_frequency`
- `avg_bet_win_amount`
- `free_containing_bet_frequency`
- `avg_rounds_per_bet`
- `avg_free_rounds_per_bet`
- `avg_rolls_per_bet`

### 7.2 Round Metrics

Current round-level metrics include:

- `round_count`
- `basic_round_count`
- `free_round_count`
- `round_hit_frequency`
- `avg_round_win_amount`
- `avg_free_rounds_awarded`

Partition metrics currently include:

- `basic.round_hit_frequency`
- `free.round_hit_frequency`
- `basic.avg_round_win_amount`
- `free.avg_round_win_amount`

### 7.3 Roll Metrics

Current roll-level metrics include:

- `roll_count`
- `initial_roll_count`
- `cascade_roll_count`
- `roll_hit_frequency`
- `avg_roll_win_amount`
- `roll_type_distribution.initial`
- `roll_type_distribution.cascade`

---

## 8. Current Practical Grouping

Within this repository, metrics are best understood in two practical groups.

### 8.1 Validation-Facing Metrics

These are the metrics typically used by default statistical rules:

- `empirical_rtp`
- `basic_rtp`
- `free_rtp`
- `bet_hit_frequency`
- `round_hit_frequency`
- `roll_hit_frequency`
- `free_containing_bet_frequency`
- `roll_type_distribution.initial`
- `roll_type_distribution.cascade`

### 8.2 Structure / Tuning-Facing Metrics

These are more useful for tuning and inspection:

- `avg_rounds_per_bet`
- `avg_free_rounds_per_bet`
- `avg_rolls_per_bet`
- `avg_free_rounds_awarded`
- partition-level round metrics

This grouping is semantic and organizational. It does not redefine the dataclass structure.

---

## 9. Structural Rules

Metrics computation must satisfy:

- determinism
- canonical-only sourcing
- no side effects
- no hidden reconstruction

Allowed operations:

- aggregate
- partition
- count
- sum
- normalize
- compute distributions

Forbidden:

- validation judgement
- upstream mutation
- inferred non-recorded canonical facts

---

## 10. Minimal API

```python
compute_metrics(result: CanonicalResult) -> MetricsBundle
```

---

## 11. Non-Goals

This file does not define:

- pass/fail rules
- acceptance thresholds
- statistical confidence levels
- regression drift tooling
- player-experience judgement

Those belong outside the metrics layer.
