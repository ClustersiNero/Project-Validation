# metrics_design.md

## 0. Purpose

This file defines the **metrics layer design** for the validation system.

It specifies:

- what to measure
- how to structure metrics
- what metrics are allowed to express
- what metrics must NOT do

This is a **computation layer**, not a validation layer.

---

## 1. Core Principle

> Metrics describe behavior. They do not judge it.

Rules:

- metrics = descriptive only
- no pass / fail logic
- no thresholds
- no interpretation of correctness

---

## 2. Input / Output

### Input

CanonicalResult

### Output

MetricsBundle = {
    "meta": MetricsMeta,
    "core": CoreMetrics,
    "distribution": DistributionMetrics,
    "tail": TailMetrics,
    "optional": OptionalMetrics
}

---

## 3. MetricsMeta

MetricsMeta = {
    "run_id": str,
    "config_id": str,
    "engine_version": str,
    "metric_version": str,

    "total_wagers": int,
    "total_bet": float,
    "total_win": float
}

Rules:

- MUST match CanonicalResult
- MUST NOT introduce new semantics

---

## 4. Core Metrics

### 4.1 Empirical RTP

empirical_rtp = total_win / total_bet

---

### 4.2 Hit Frequency

hit_frequency = number_of_hit_wagers / total_wagers

Definition:

- hit = total_win > 0

---

### 4.3 Average Win (per wager)

avg_win = total_win / total_wagers

---

### 4.4 Average Win (conditional)

avg_win_when_hit = total_win / number_of_hit_wagers

---

## 5. Distribution Metrics

### 5.1 Win Distribution (binned)

win_distribution = {
    "0": count,
    "(0,1]": count,
    "(1,5]": count,
}

Rules:

- bins MUST be predefined
- bins MUST be explicit (no dynamic grouping)

---

### 5.2 Quantiles

quantiles = {
    "p50": float,
    "p90": float,
    "p95": float,
    "p99": float
}

---

### 5.3 Max Win

max_win = max(wager.total_win)

---

## 6. Tail Metrics

### 6.1 Top-p win Contribution

top_1pct_win_share = sum(top_1pct_win_contribution) / total_win

---

### 6.2 Extreme Win Frequency

extreme_win_freq_p99 = count(wagers where win >= p99) / total_wagers

---

## 7. Optional Metrics (Non-Core)

### 7.1 Streak Metrics

max_losing_streak  
avg_losing_streak

---

### 7.2 Mode-Level Metrics

base_rtp  
feature_rtp  
feature_trigger_rate

---

### 7.3 Round / Roll Metrics

avg_rounds_per_wager
avg_rolls_per_round
avg_rolls_per_wager

avg_rounds_per_feature
avg_rolls_per_feature

#### Definitions:
wager = top-level bet event
round = one independently settled round within a wager or feature
roll = one board resolution / refill progression inside a round

---

### 7.4 Round-Level Metrics

avg_round_win
avg_multiplier_per_feature_round
max_round_multiplier

---

## 8. Metric Categories

### Descriptive Metrics (this file)

- RTP
- hit frequency
- distribution
- tail metrics

### Validation Metrics (NOT here)

Examples:

- RTP deviation vs expected
- CI checks
- pass/fail

---

## 9. Structural Rules

### Determinism

CanonicalResult → MetricsBundle must be deterministic

---

### Completeness

Metrics must allow:

- high-level understanding
- distribution inspection
- tail inspection

But NOT:

- correctness judgement

---

### No Hidden Logic

Metrics MUST NOT:

- infer hidden states
- reconstruct missing data
- depend on external context

---

### No Side Effects

- must not modify canonical
- must not depend on validation

---

## 10. Minimal API

compute_metrics(result: CanonicalResult) -> MetricsBundle

---

## 11. Implementation Checklist

- [ ] RTP matches summary
- [ ] hit frequency correct
- [ ] quantiles reproducible
- [ ] distribution bins fixed
- [ ] tail metrics consistent
- [ ] no validation logic included

---

## 12. Non-Goals

- no fairness judgement
- no RTP correctness claim
- no player experience prediction
- no adaptive interpretation

---

## Summary

Metrics layer:

- transforms CanonicalResult into structured observations
- exposes distribution and tail behavior
- remains strictly neutral

It is the **only input** to validation, but never performs validation itself.
