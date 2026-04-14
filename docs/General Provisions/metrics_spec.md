# metrics_spec.md

## 0. Purpose

This file defines the **metrics layer specification** for the validation system.

It specifies:

* what to measure
* how to structure metrics
* what metrics are allowed to express
* what metrics must NOT do

This is a **computation layer**, not a validation layer.

---

## 1. Core Principle

> Metrics describe behavior. They do not judge it.

Rules:

* metrics = descriptive only
* no pass / fail logic
* no thresholds
* no interpretation of correctness

---

## 2. Naming Contract (Bet-Only)

This specification is Bet-only for top-level event naming.

Required naming:

* top-level unit: bet
* hierarchy: Bet -> Round -> Roll
* canonical top-level collection: bets
* metrics sample unit: bet
* amount field naming uses bet terms where top-level event amount is referenced

### Forbidden Parallel Terminology (Formal Terms)

The following formal terms are forbidden in this specification:

* wager
* wagers
* wager_id
* wager_amount
* total_wagers
* stake
* stakes
* stake_amount

---

## 3. Input / Output

### Input

CanonicalResult

### Output

```python
MetricsBundle = {
    "meta": MetricsMeta,
    "core": CoreMetrics,
    "distribution": DistributionMetrics,
    "tail": TailMetrics,
    "optional": OptionalMetrics
}
```

---

## 4. MetricsMeta

```python
MetricsMeta = {
    "run_id": str,
    "config_id": str,
    "config_version": str,
    "engine_version": str,
    "schema_version": str,

    "mode": str,
    "seed": int,
    "bet_amount": float,
    "total_bets": int,
    "timestamp": str,

    "total_bet": float,
    "total_win": float
}
```

Rules:

* MUST be a direct projection from CanonicalResult.run and CanonicalResult.summary
* MUST NOT redefine metadata semantics
* MUST NOT introduce metadata fields with no canonical source
* Recomputable run-level summary fields are allowed as metadata convenience projection only.
* Raw canonical records remain the primary source for downstream computation.

Field semantics:

* bet_amount = per-bet amount from CanonicalResult.run
* total_bet = total bet amount across the full run

---

## 5. Core Metrics

### 5.1 Empirical RTP

```python
empirical_rtp = total_win / total_bet
```

---

### 5.2 Hit Frequency

```python
hit_frequency = number_of_hit_bets / total_bets
```

Definition:

* hit = total_win > 0
* hit status MUST align with BetRecord.is_hit where BetRecord.is_hit = (total_win > 0)

---

### 5.3 Average Win (per bet)

```python
avg_win = total_win / total_bets
```

Definition:

* avg_win means average win per bet

---

### 5.4 Average Win (conditional)

```python
avg_win_when_hit = total_win / number_of_hit_bets
```

---

## 6. Distribution Metrics

### 6.1 Win Distribution (binned)

```python
win_distribution = {
    "0": count,
    "(0,1]": count,
    "(1,5]": count,
}
```

Rules:

* bins MUST be predefined
* bins MUST be explicit (no dynamic grouping)
* bin basis MUST be win multiple per bet: win_multiple = bet.total_win / bet.bet_amount
* bin intervals MUST be applied to win_multiple values using the fixed interval labels shown above

---

### 6.2 Quantiles

```python
quantiles = {
    "p50": float,
    "p90": float,
    "p95": float,
    "p99": float
}
```

---

### 6.3 Max Win

```python
max_win = max(bet.total_win for bet in bets)
```

---

## 7. Tail Metrics

### 7.1 Top-p Win Contribution

```python
top_1pct_win_share = sum(win for win in top_1pct_winning_bets) / total_win
```

---

### 7.2 Extreme Win Frequency

```python
extreme_win_freq_p99 = count(bets where win >= p99) / total_bets
```

---

## 8. Optional Metrics (Non-Core)

### 8.1 Streak Metrics

* max_losing_streak
* avg_losing_streak

---

### 8.2 Mode-Level Metrics

* base_rtp
* feature_rtp
* feature_trigger_rate

---

### 8.3 Round / Roll Metrics

* avg_rounds_per_bet

* avg_rolls_per_round

* avg_rolls_per_bet

* avg_rounds_per_feature
  - definition: total_feature_rounds / number_of_feature_triggers

* avg_rolls_per_feature
  - definition: total_feature_rolls / number_of_feature_triggers

#### Definitions

* bet = top-level event unit
* round = one independently settled round within a bet or feature
* roll = one board resolution / refill progression inside a round
* feature trigger source = RollRecord.state_type == "feature_trigger"

---

### 8.4 Round-Level Metrics

* avg_round_win
* avg_multiplier_per_feature_round
  - computed from RoundRecord.round_multiplier_total over feature rounds only
* max_round_multiplier

---

## 9. Metric Categories

### Descriptive Metrics (this file)

* RTP
* hit frequency
* distribution
* tail metrics

### Validation Metrics (NOT here)

Examples:

* RTP deviation vs expected
* CI checks
* pass/fail

---

## 10. Structural Rules

### Determinism

CanonicalResult -> MetricsBundle must be deterministic

---

### Completeness

Metrics must allow:

* high-level understanding
* distribution inspection
* tail inspection

But NOT:

* correctness judgement

---

### No Hidden Logic

Metrics MUST NOT:

* infer hidden states
* reconstruct missing data
* depend on external context

---

### No Side Effects

* must not modify canonical
* must not depend on validation

---

## 11. Minimal API

```python
compute_metrics(result: CanonicalResult) -> MetricsBundle
```

---

## 12. Implementation Checklist

* [ ] RTP consistent with recomputed totals
* [ ] hit frequency correct
* [ ] quantiles reproducible
* [ ] distribution bins fixed
* [ ] tail metrics consistent
* [ ] no validation logic included
* [ ] no forbidden top-level terminology remains

---

## 13. Non-Goals

* no fairness judgement
* no RTP correctness claim
* no player experience prediction
* no adaptive interpretation

---

## Summary

Metrics layer:

* transforms CanonicalResult into structured observations
* exposes distribution and tail behavior
* remains strictly neutral

It is a required quantitative input to statistical and baseline regression validation, but never performs validation itself.
