
# 0. Purpose

This file defines the **metrics layer specification** for the validation-first slot math system.

Metrics transform `CanonicalResult` into structured, reproducible, descriptive observations.

This file specifies:

- what is measured
- how metrics are grouped
- which canonical fields metrics may use
- how each metric is calculated
- which layer each metric belongs to

This is a **descriptive computation layer** only.

Metrics MUST NOT:

- perform pass / fail judgement
- apply thresholds
- include validation verdicts
- modify canonical data
- infer hidden engine states that are not recorded in canonical

---

# 1. Core Principle

> Metrics describe observed behavior from canonical records. They do not judge correctness.

Required rules:

- metrics are descriptive only
- metrics are computed only from `CanonicalResult`
- metrics must remain deterministic
- metrics must not introduce new upstream schema fields
- metrics must not mix validation logic into metric definitions
- core metrics must be computed on all rounds only (no basic / free partition)

Pipeline position:

```text
config -> engine -> canonical -> metrics -> validation
```

---

# 2. Naming Contract

This specification uses the same hierarchical naming contract as the architecture and canonical specifications:

**Bet -> Round -> Roll**

Required:

- top-level sample unit: `bet`
- sub-levels: `round`, `roll`

Forbidden:

- `wager`
- `stake`
- `spin`
- `step`

---

# 3. StatisticalMetric Schema

CI-eligible metrics MUST use the following unified output type instead of a plain `float`:

```python
StatisticalMetric = {
    "observed": float,            # the computed metric value (mean / frequency)
    "standard_deviation": float,  # sample std (Bessel-corrected, denominator n - 1)
    "sample_size": int,           # number of observations in the underlying series
}
```

Rules:

- `observed` is the point estimate (mean or frequency) computed from the underlying sample series
- `standard_deviation` is computed from the same underlying sample series using Bessel correction (denominator `sample_size - 1`)
- `sample_size` is explicit per metric and must match the metric's sample space:
  - bet-level metrics → `sample_size = total_bets`
  - round-level metrics (all rounds) → `sample_size = total_rounds`
  - round-level metrics (basic rounds) → `sample_size = basic_round_count`
  - round-level metrics (free rounds) → `sample_size = free_round_count`
  - roll-level metrics → `sample_size = total_rolls`
- `standard_deviation` and `sample_size` MUST NOT be moved to `MetricsMeta`; they are per-metric fields
- The metrics layer MUST NOT compute CI; it only exposes `observed`, `standard_deviation`, and `sample_size` for downstream use

## Zero-Division and Small-Sample Contract

The following rules MUST be applied deterministically; behavior MUST NOT be left to implementation convention:

| Condition | `observed` | `standard_deviation` | `sample_size` |
|---|---|---|---|
| `sample_size == 0` | `null` | `null` | `0` |
| `sample_size == 1` | computed normally | `null` | `1` |
| `sample_size >= 2` | computed normally | computed (Bessel-corrected) | as counted |

Rules:

- `null` is a first-class value in this schema; it means "undefined", not "zero"
- `standard_deviation` is `null` whenever Bessel-corrected std is undefined (i.e. `sample_size < 2`)
- `observed` is `null` only when there are no observations (`sample_size == 0`); a single observation is a valid point estimate
- The validation layer MUST treat `null` `standard_deviation` as a non-computable CI and MUST NOT substitute a default, a zero, or an epsilon
- Filtered/conditional scalars (non-`StatisticalMetric` fields) MUST return `null` when their filtered sample is empty

## CI Eligibility Boundary

**Only metrics whose leaf type is `StatisticalMetric` are CI-eligible.**

CI-eligible metrics are mean-like over a uniform sample space:

- mean values
- frequency values (0/1 mean over a fixed population)
- average-per-unit values
- contribution averages

NOT CI-eligible (remain scalar or raw list):

- `max` values
- quantile values
- distributions (raw lists)
- tail metrics
- filtered / conditional aggregates (e.g. average when hit, average over a non-uniform subset)

Scalar metrics and distribution metrics MUST NOT be used in CI computation by the validation layer.

## Path Contract

`MetricsBundle` exposes metrics at nested paths:

```
MetricsBundle.<group>.<subgroup>.<metric_name>
```

Examples:

```
MetricsBundle.bet_metrics.core.avg_bet_win_amount
MetricsBundle.round_metrics.core.avg_round_win_amount
MetricsBundle.roll_metrics.core.avg_roll_win_amount
```

Rules:

- `ValidationRules` MUST reference metrics using identical nested paths
- No flat metric naming is permitted in `ValidationRules`
- The group / subgroup hierarchy mirrors the `BetMetrics`, `RoundMetrics`, `RollMetrics` structures defined in this file

## StatisticalMetric Semantics

All CI-eligible metrics follow a common template. Each metric MUST provide an explicit series expression in its formula block. Fields are always derived as:

- `observed` — mean of the series (or equivalent `sum(...) / len(...)` expression)
- `standard_deviation` — `sample_std(series)`, Bessel-corrected
- `sample_size` — `len(series)`

**Frequency metrics** use an indicator series: `[1 if <condition> else 0 for item in population]`. Each frequency metric states only the condition; the indicator construction is implied by this template.

**Distribution metrics** return the raw series as a list. They do not aggregate, provide no `standard_deviation` or `sample_size`, and are non-CI. And must return the full underlying series without aggregation or normalization.

## Partition Rule for Round Metrics

Round-level populations are defined once and used throughout §7:

```python
all_rounds   = [r for b in bets for r in b.rounds]
basic_rounds = [r for r in all_rounds if r.round_type == "basic"]
free_rounds  = [r for r in all_rounds if r.round_type == "free"]
```

Corresponding `sample_size` values:

- `all_rounds` metrics → `sample_size = total_rounds`
- `basic_rounds` metrics → `sample_size = basic_round_count = len(basic_rounds)`
- `free_rounds` metrics → `sample_size = free_round_count = len(free_rounds)`

Metric formulas across partitions are identical except for the input set. Section headers state which partition applies.

Roll-level population: `all_rolls = [roll for b in bets for r in b.rounds for roll in r.rolls]`, `sample_size = total_rolls`.

All CI-eligible metrics MUST be fully interpretable using this section alone.
Per-metric definitions MUST NOT redefine sample unit, series, or aggregation semantics.

Partition-specific metric groups (basic / free) MUST NOT redefine formulas; only input populations differ.

---

# 4. Input / Output

## 4.1 Input

```python
CanonicalResult = {
    "simulation_metadata": SimulationMetadata,
    "bets": list[BetRecord],
}
```

## 3.2 Output

```python
MetricsBundle = {
    "meta": MetricsMeta,
    "bet_metrics": BetMetrics,
    "round_metrics": RoundMetrics,
    "roll_metrics": RollMetrics,
}
```

Rules:

- `MetricsBundle` is a computed projection of canonical data
- `MetricsBundle` must be fully reproducible from the same canonical input
- no field in `MetricsBundle` may require data outside canonical

---

# 4. MetricsMeta

`MetricsMeta` carries simulation-level metadata projection and recomputed run totals.

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

## 4.1 Source Rules

Direct projection from `simulation_metadata`:

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

bet_amount already reflects the actual paid cost per bet under the current mode (including buy_free or other modes).

bet_level is required for all normalization-based metrics, including win multiple and distribution normalization.
bet_level MUST NOT be used for return-based metrics.

Recomputed run-level aggregates from canonical records:

- `total_bet_amount = total_bets * bet_amount`
- `total_bet_win_amount = sum(bet.bet_win_amount for bet in bets)`

Rules:

- recomputed totals are allowed as convenience outputs
- canonical records remain the source of truth
- metadata must not redefine upstream semantics

---

# 5. General Calculation Rules

## 5.1 Bet Amount Basis

`bet_amount` is the per-bet amount stored in `simulation_metadata.bet_amount`.

Unless otherwise stated:

- any RTP-like return ratio uses `bet_amount`
- any win multiple is calculated against `bet_level`

## 5.2 Record Counting Basis

```python
total_bets = len(bets)
total_rounds = sum(bet.round_count for bet in bets)
total_rolls = sum(round.roll_count for bet in bets for round in bet.rounds)
```

## 5.3 Hit Definition

For metrics purposes, a hit is defined by recorded win amount only.

```python
bet_hit = (bet_win_amount > 0)
round_hit = (round_win_amount > 0)
roll_hit = (roll_win_amount > 0)
```

This is a metric computation rule only.
It does not introduce new canonical fields.

## 5.4 Basic / Free Partition

Basic and free partitions use `round_type` from `RoundRecord`.

```python
basic_rounds = [round for bet in bets for round in bet.rounds if round.round_type == "basic"]
free_rounds  = [round for bet in bets for round in bet.rounds if round.round_type == "free"]
```

## 5.5 Zero-Division Rule

Zero-division behavior MUST follow the "Zero-Division and Small-Sample Contract" defined in Section 3.

No alternative implementation-specific handling is allowed.

---

# 6. Bet-Level Metrics

Bet-level metrics use `BetRecord` as the primary observation unit.

```python
BetMetrics = {
    "core": BetCoreMetrics,
    "distribution": BetDistributionMetrics,
    "tail": BetTailMetrics,
    "structure": BetStructureMetrics,
}
```

## 6.1 Bet Core Metrics

### 6.1.1 Empirical RTP

```python
empirical_rtp = StatisticalMetric(
    observed           = sum(b.bet_win_amount for b in bets) / total_bets / bet_amount,
    standard_deviation = sample_std([b.bet_win_amount / bet_amount for b in bets]),
    sample_size        = total_bets,
)
```

Where:

```python
total_bet_win_amount = sum(bet.bet_win_amount for bet in bets)
total_bet_amount = total_bets * bet_amount
```

### 6.1.2 Basic RTP Contribution

```python
basic_rtp = sum(bet.basic_win_amount for bet in bets) / total_bet_amount
```

### 6.1.3 Free RTP Contribution

```python
free_rtp = sum(bet.free_win_amount for bet in bets) / total_bet_amount
```

### 6.1.4 Bet Hit Frequency

```python
bet_hit_frequency = StatisticalMetric(
    observed           = len([b for b in bets if b.bet_win_amount > 0]) / total_bets,
    standard_deviation = sample_std([1 if b.bet_win_amount > 0 else 0 for b in bets]),
    sample_size        = total_bets,
)
```

### 6.1.5 Average Bet Win

```python
avg_bet_win_amount = StatisticalMetric(
    observed           = sum(b.bet_win_amount for b in bets) / total_bets,
    standard_deviation = sample_std([b.bet_win_amount for b in bets]),
    sample_size        = total_bets,
)
```

### 6.1.6 Average Bet Win When Hit

```python
hit_bets = [b for b in bets if b.bet_win_amount > 0]
avg_bet_win_amount_when_hit = sum(b.bet_win_amount for b in hit_bets) / len(hit_bets)
```

Scalar. Filtered sample (hit bets only) — NOT CI-eligible.

### 6.1.7 Basic Win Share of Total Bet Win

```python
basic_win_share =
    sum(bet.basic_win_amount for bet in bets)
    / sum(bet.bet_win_amount for bet in bets)
```

### 6.1.8 Free Win Share of Total Bet Win

```python
free_win_share =
    sum(bet.free_win_amount for bet in bets)
    / sum(bet.bet_win_amount for bet in bets)
```

## 6.2 Bet Distribution Metrics

### 6.2.1 Bet Win Amount Distribution

```python
bet_win_amount_distribution = 
    [bet.bet_win_amount for bet in bets]
```

### 6.2.2 Bet Win Multiple Distribution

```python
bet_win_multiple_distribution =
    [bet.bet_win_amount / bet_level for bet in bets]
```

`bet_win_multiple = bet_win_amount / bet_level` — normalized payout relative to `bet_level`.

### 6.2.3 Bet Win Multiple Quantiles

Typical outputs may include:

```python
p50, p90, p95, p99
```

Computed from:

```python
bet_win_multiple_quantiles =
    [bet.bet_win_amount / bet_level for bet in bets]
```

### 6.2.4 Maximum Bet Win Amount

```python
max_bet_win_amount = max(bet.bet_win_amount for bet in bets)
```

### 6.2.5 Maximum Bet Win Multiple

```python
max_bet_win_multiple = max(bet.bet_win_amount / bet_level for bet in bets)
```

## 6.3 Bet Tail Metrics

### 6.3.1 Top-p Bet Win Share

For a selected top fraction `p` of winning bets:

```python
top_p_bet_win_share =
    sum(bet.bet_win_amount for bet in top_p_winning_bets)
    / sum(bet.bet_win_amount for bet in bets)
```

Examples of `p` may include:

- top 1%
- top 0.1%

The selected reporting set must be explicitly named in implementation output.

### 6.3.2 Bet Win Multiple Tail Quantiles

Reported from the upper tail of:

```python
bet_win_multiple_tail_quantiles = 
    [bet.bet_win_amount / bet_level for bet in bets]
```

Examples:

- p99
- p99.9

These are descriptive tail location metrics.

## 6.4 Bet Structure Metrics

### 6.4.1 Average Rounds per Bet

```python
avg_round_count_per_bet = StatisticalMetric(
    observed           = sum(b.round_count for b in bets) / total_bets,
    standard_deviation = sample_std([b.round_count for b in bets]),
    sample_size        = total_bets,
)
```

### 6.4.2 Round Count Distribution per Bet

```python
round_count_distribution_per_bet =
    [bet.round_count for bet in bets]
```

### 6.4.3 Free-Containing Bet Frequency

Condition: `any(r.round_type == "free" for r in b.rounds)`

```python
free_containing_bet_frequency = StatisticalMetric(
    observed           = len([b for b in bets
                              if any(r.round_type == "free" for r in b.rounds)]) / total_bets,
    standard_deviation = sample_std([1 if any(r.round_type == "free" for r in b.rounds) else 0
                                     for b in bets]),
    sample_size        = total_bets,
)
```

### 6.4.4 Average Basic Rounds per Bet

```python
avg_basic_rounds_per_bet = StatisticalMetric(
    observed           = sum(sum(1 for r in b.rounds if r.round_type == "basic")
                             for b in bets) / total_bets,
    standard_deviation = sample_std([sum(1 for r in b.rounds if r.round_type == "basic")
                                     for b in bets]),
    sample_size        = total_bets,
)
```

### 6.4.5 Average Free Rounds per Bet

```python
avg_free_rounds_per_bet = StatisticalMetric(
    observed           = sum(sum(1 for r in b.rounds if r.round_type == "free")
                             for b in bets) / total_bets,
    standard_deviation = sample_std([sum(1 for r in b.rounds if r.round_type == "free")
                                     for b in bets]),
    sample_size        = total_bets,
)
```

### 6.4.6 Average Rolls per Bet

```python
avg_rolls_per_bet = StatisticalMetric(
    observed           = total_rolls / total_bets,
    standard_deviation = sample_std([sum(r.roll_count for r in b.rounds) for b in bets]),
    sample_size        = total_bets,
)
```

## 6.5 Bet Volatility-Oriented Descriptive Metrics

These metrics describe spread and concentration only.

### 6.5.1 Bet Win Multiple Mean

```python
mean_bet_win_multiple = StatisticalMetric(
    observed           = sum(b.bet_win_amount / bet_level for b in bets) / total_bets,
    standard_deviation = sample_std([b.bet_win_amount / bet_level for b in bets]),
    sample_size        = total_bets,
)
```

### 6.5.2 Bet Win Multiple Variance

```python
bet_win_multiple_variance = sample_var([b.bet_win_amount / bet_level for b in bets])
```

Optional. Scalar. Computed from the same series as `mean_bet_win_multiple`.

---

# 7. Round-Level Metrics

Round-level metrics use `RoundRecord` as the primary observation unit.

```python
RoundMetrics = {
    "core": RoundCoreMetrics,
    "basic": BasicRoundMetrics,
    "free": FreeRoundMetrics,
    "multiplier": RoundMultiplierMetrics,
    "scatter": RoundScatterMetrics,
    "distribution": RoundDistributionMetrics,
    "structure": RoundStructureMetrics,
}
```

**Partition structure:** `basic` and `free` are partitions over the same metric definitions. For any metric that appears in both `basic` and `free` sections, the formula pattern is identical — only the input population differs (`basic_rounds` vs `free_rounds`, `basic_round_count` vs `free_round_count`). Formulas are shown explicitly in each section for implementation completeness.

Partition populations are defined in §3 Partition Rule.

## 7.1 Round Core Metrics

### 7.1.1 Average Round Win Amount

```python
avg_round_win_amount = StatisticalMetric(
    observed           = sum(r.round_win_amount for r in all_rounds) / total_rounds,
    standard_deviation = sample_std([r.round_win_amount for r in all_rounds]),
    sample_size        = total_rounds,
)
```

### 7.1.2 Round Hit Frequency

```python
round_hit_frequency = StatisticalMetric(
    observed           = len([r for r in all_rounds if r.round_win_amount > 0]) / total_rounds,
    standard_deviation = sample_std([1 if r.round_win_amount > 0 else 0 for r in all_rounds]),
    sample_size        = total_rounds,
)
```

### 7.1.3 Base Symbol Win Amount

```python
avg_base_symbol_win_amount_per_round = StatisticalMetric(
    observed           = sum(r.base_symbol_win_amount for r in all_rounds) / total_rounds,
    standard_deviation = sample_std([r.base_symbol_win_amount for r in all_rounds]),
    sample_size        = total_rounds,
)
```

## 7.2 Basic Round Metrics

Partition: `basic_rounds`. `sample_size = basic_round_count`. Canonical formula variant for `round_type == "basic"`.

### 7.2.1 Basic Round Count

```python
basic_round_count = len(basic_rounds)
```

### 7.2.2 Average Basic Round Win Amount

```python
avg_basic_round_win_amount = StatisticalMetric(
    observed           = sum(r.round_win_amount for r in basic_rounds) / basic_round_count,
    standard_deviation = sample_std([r.round_win_amount for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

### 7.2.3 Basic Round Hit Frequency

```python
basic_round_hit_frequency = StatisticalMetric(
    observed           = len([r for r in basic_rounds if r.round_win_amount > 0]) / basic_round_count,
    standard_deviation = sample_std([1 if r.round_win_amount > 0 else 0 for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

### 7.2.4 Average Free Rounds Awarded (Basic Rounds)

```python
avg_award_free_rounds_from_basic_round = StatisticalMetric(
    observed           = sum(r.award_free_rounds for r in basic_rounds) / basic_round_count,
    standard_deviation = sample_std([r.award_free_rounds for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

## 7.3 Free Round Metrics

Partition: `free_rounds`. `sample_size = free_round_count`. Same formula pattern as §7.2, applied to `free_rounds` / `free_round_count`.

### 7.3.1 Free Round Count

```python
free_round_count = len(free_rounds)
```

### 7.3.2 Average Free Round Win Amount

`avg_free_round_win_amount` — same formula as `avg_basic_round_win_amount` (§7.2.2) with `free_rounds` / `free_round_count`.

### 7.3.3 Free Round Hit Frequency

`free_round_hit_frequency` — same formula as `basic_round_hit_frequency` (§7.2.3) with `free_rounds` / `free_round_count`.

### 7.3.4 Average Free Rounds Awarded (Free Rounds)

`avg_award_free_rounds_from_free_round` — same formula as `avg_award_free_rounds_from_basic_round` (§7.2.4) with `free_rounds` / `free_round_count`.

## 7.4 Round Multiplier Metrics

All metrics are partitioned by `round_type`. For each pair, the basic variant is shown with its canonical formula; the free variant uses the same formula with `free_rounds` / `free_round_count`.

### 7.4.1 Multiplier Increment Frequency (Basic Rounds)

```python
basic_round_multiplier_increment_frequency = StatisticalMetric(
    observed           = len([r for r in basic_rounds if r.round_multiplier_increment > 0]) / basic_round_count,
    standard_deviation = sample_std([1 if r.round_multiplier_increment > 0 else 0 for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

### 7.4.2 Multiplier Increment Frequency (Free Rounds)

`free_round_multiplier_increment_frequency` — same formula as `basic_round_multiplier_increment_frequency` (§7.4.1) with `free_rounds` / `free_round_count`.

### 7.4.3 Average Multiplier Increment (Basic Rounds)

```python
avg_basic_round_multiplier_increment = StatisticalMetric(
    observed           = sum(r.round_multiplier_increment for r in basic_rounds) / basic_round_count,
    standard_deviation = sample_std([r.round_multiplier_increment for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

### 7.4.4 Average Multiplier Increment (Free Rounds)

`avg_free_round_multiplier_increment` — same formula as `avg_basic_round_multiplier_increment` (§7.4.3) with `free_rounds` / `free_round_count`.

### 7.4.5 Maximum Multiplier Increment

```python
max_round_multiplier_increment =
    max(r.round_multiplier_increment for r in all_rounds)
```

### 7.4.6 Average Round Total Multiplier (Basic Rounds)

```python
avg_basic_round_total_multiplier = StatisticalMetric(
    observed           = sum(r.round_total_multiplier for r in basic_rounds) / basic_round_count,
    standard_deviation = sample_std([r.round_total_multiplier for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

### 7.4.7 Average Round Total Multiplier (Free Rounds)

`avg_free_round_total_multiplier` — same formula as `avg_basic_round_total_multiplier` (§7.4.6) with `free_rounds` / `free_round_count`.

### 7.4.8 Maximum Round Total Multiplier

```python
max_round_total_multiplier =
    max(r.round_total_multiplier for r in all_rounds)
```

### 7.4.9 Average Carried Multiplier at Free Round Start

Carried multiplier is only meaningful in free rounds.

```python
avg_carried_multiplier_at_free_round_start = StatisticalMetric(
    observed           = sum(r.carried_multiplier for r in free_rounds) / free_round_count,
    standard_deviation = sample_std([r.carried_multiplier for r in free_rounds]),
    sample_size        = free_round_count,
)
```

### 7.4.10 Maximum Carried Multiplier

```python
max_carried_multiplier =
    max(r.carried_multiplier for r in all_rounds)
```

### 7.4.11 Multiplier Contribution (Basic Rounds)

```python
avg_multiplier_contribution_per_round_basic_rounds = StatisticalMetric(
    observed           = sum(
                             r.base_symbol_win_amount * (r.round_total_multiplier - 1)
                             for r in basic_rounds
                         ) / basic_round_count,
    standard_deviation = sample_std([
                             r.base_symbol_win_amount * (r.round_total_multiplier - 1)
                             for r in basic_rounds
                         ]),
    sample_size        = basic_round_count,
)
```

### 7.4.12 Multiplier Contribution (Free Rounds)

`avg_multiplier_contribution_per_round_free_rounds` — same formula as `avg_multiplier_contribution_per_round_basic_rounds` (§7.4.11) with `free_rounds` / `free_round_count`.

## 7.5 Round Scatter Metrics

All metrics follow the same partition pattern as §7.4. Basic-partition formula shown first; free-partition variant uses the same formula with `free_rounds` / `free_round_count`.

### 7.5.1 Average Scatter Increment (Basic Rounds)

```python
avg_round_scatter_increment_basic_rounds = StatisticalMetric(
    observed           = sum(r.round_scatter_increment for r in basic_rounds) / basic_round_count,
    standard_deviation = sample_std([r.round_scatter_increment for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

### 7.5.2 Average Scatter Increment (Free Rounds)

`avg_round_scatter_increment_free_rounds` — same formula as `avg_round_scatter_increment_basic_rounds` (§7.5.1) with `free_rounds` / `free_round_count`.

### 7.5.3 Scatter Win Frequency (Basic Rounds)

```python
scatter_win_frequency_basic_rounds = StatisticalMetric(
    observed           = len([r for r in basic_rounds if r.scatter_win_amount > 0]) / basic_round_count,
    standard_deviation = sample_std([1 if r.scatter_win_amount > 0 else 0 for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

### 7.5.4 Scatter Win Frequency (Free Rounds)

`scatter_win_frequency_free_rounds` — same formula as `scatter_win_frequency_basic_rounds` (§7.5.3) with `free_rounds` / `free_round_count`.

### 7.5.5 Average Scatter Win Amount (Basic Rounds)

```python
avg_scatter_win_amount_basic_rounds = StatisticalMetric(
    observed           = sum(r.scatter_win_amount for r in basic_rounds) / basic_round_count,
    standard_deviation = sample_std([r.scatter_win_amount for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

### 7.5.6 Average Scatter Win Amount (Free Rounds)

`avg_scatter_win_amount_free_rounds` — same formula as `avg_scatter_win_amount_basic_rounds` (§7.5.5) with `free_rounds` / `free_round_count`.

### 7.5.7 Free-Round Award Frequency (Basic Rounds)

```python
award_free_round_frequency_basic_rounds = StatisticalMetric(
    observed           = len([r for r in basic_rounds if r.award_free_rounds > 0]) / basic_round_count,
    standard_deviation = sample_std([1 if r.award_free_rounds > 0 else 0 for r in basic_rounds]),
    sample_size        = basic_round_count,
)
```

### 7.5.8 Free-Round Award Frequency (Free Rounds)

`award_free_round_frequency_free_rounds` — same formula as `award_free_round_frequency_basic_rounds` (§7.5.7) with `free_rounds` / `free_round_count`.

## 7.6 Round Distribution Metrics

### 7.6.1 Round Win Amount Distribution (All Rounds)

```python
round_win_amount_distribution_all_rounds =
    [r.round_win_amount for r in all_rounds]
```

### 7.6.2 Round Win Amount Distribution (Basic Rounds)

```python
round_win_amount_distribution_basic_rounds =
    [r.round_win_amount for r in basic_rounds]
```

### 7.6.3 Round Win Amount Distribution (Free Rounds)

```python
round_win_amount_distribution_free_rounds =
    [r.round_win_amount for r in free_rounds]
```

### 7.6.4 Base Symbol Win Amount Distribution (All Rounds)

```python
base_symbol_win_amount_distribution_all_rounds =
    [r.base_symbol_win_amount for r in all_rounds]
```

### 7.6.5 Base Symbol Win Amount Distribution (Basic Rounds)

```python
base_symbol_win_amount_distribution_basic_rounds =
    [r.base_symbol_win_amount for r in basic_rounds]
```

### 7.6.6 Base Symbol Win Amount Distribution (Free Rounds)

```python
base_symbol_win_amount_distribution_free_rounds =
    [r.base_symbol_win_amount for r in free_rounds]
```

### 7.6.7 Multiplier Contribution Distribution (Basic Rounds)

```python
multiplier_contribution_distribution_basic_rounds =
    [
        r.base_symbol_win_amount * (r.round_total_multiplier - 1)
        for r in basic_rounds
    ]
```

### 7.6.8 Multiplier Contribution Distribution (Free Rounds)

```python
multiplier_contribution_distribution_free_rounds =
    [
        r.base_symbol_win_amount * (r.round_total_multiplier - 1)
        for r in free_rounds
    ]
```

### 7.6.9 Scatter Win Amount Distribution (All Rounds)

```python
scatter_win_amount_distribution_all_rounds =
    [r.scatter_win_amount for r in all_rounds]
```

### 7.6.10 Scatter Win Amount Distribution (Basic Rounds)

```python
scatter_win_amount_distribution_basic_rounds =
    [r.scatter_win_amount for r in basic_rounds]
```

### 7.6.11 Scatter Win Amount Distribution (Free Rounds)

```python
scatter_win_amount_distribution_free_rounds =
    [r.scatter_win_amount for r in free_rounds]
```

### 7.6.12 Round Total Multiplier Distribution (Basic Rounds)

```python
round_total_multiplier_distribution_basic_rounds =
    [r.round_total_multiplier for r in basic_rounds]
```

### 7.6.13 Round Total Multiplier Distribution (Free Rounds)

```python
round_total_multiplier_distribution_free_rounds =
    [r.round_total_multiplier for r in free_rounds]
```

## 7.7 Round Structure Metrics

structure metrics are mechanism-independent and must not be partitioned by round_type

### 7.7.1 Average Rolls per Round

```python
avg_roll_count_per_round = StatisticalMetric(
    observed           = sum(r.roll_count for r in all_rounds) / total_rounds,
    standard_deviation = sample_std([r.roll_count for r in all_rounds]),
    sample_size        = total_rounds,
)
```

### 7.7.2 Roll Count Distribution per Round

```python
roll_count_distribution =
    [r.roll_count for r in all_rounds]
```

---

# 8. Roll-Level Metrics

Roll-level metrics use `RollRecord` as the primary observation unit.

```python
RollMetrics = {
    "core": RollCoreMetrics,
    "multiplier": RollMultiplierMetrics,
    "scatter": RollScatterMetrics,
    "distribution": RollDistributionMetrics,
}
```

## 8.1 Roll Core Metrics

### 8.1.1 Average Roll Win Amount

```python
avg_roll_win_amount = StatisticalMetric(
    observed           = sum(roll.roll_win_amount for roll in all_rolls) / total_rolls,
    standard_deviation = sample_std([roll.roll_win_amount for roll in all_rolls]),
    sample_size        = total_rolls,
)
```

### 8.1.2 Roll Hit Frequency

```python
roll_hit_frequency = StatisticalMetric(
    observed           = len([roll for roll in all_rolls if roll.roll_win_amount > 0]) / total_rolls,
    standard_deviation = sample_std([1 if roll.roll_win_amount > 0 else 0 for roll in all_rolls]),
    sample_size        = total_rolls,
)
```

### 8.1.3 Roll Type Distribution

```python
roll_type_distribution =
    {
        "initial": len([roll for roll in all_rolls if roll.roll_type == "initial"]) / total_rolls,
        "cascade": len([roll for roll in all_rolls if roll.roll_type == "cascade"]) / total_rolls,
    }
```

## 8.2 Roll Multiplier Metrics

### 8.2.1 Average Multiplier Symbols per Roll

```python
avg_roll_multi_symbols_num = StatisticalMetric(
    observed           = sum(roll.roll_multi_symbols_num for roll in all_rolls) / total_rolls,
    standard_deviation = sample_std([roll.roll_multi_symbols_num for roll in all_rolls]),
    sample_size        = total_rolls,
)
```

### 8.2.2 Multiplier-Symbol Roll Frequency

```python
roll_with_multiplier_symbol_frequency = StatisticalMetric(
    observed           = len([roll for roll in all_rolls if roll.roll_multi_symbols_num > 0]) / total_rolls,
    standard_deviation = sample_std([1 if roll.roll_multi_symbols_num > 0 else 0 for roll in all_rolls]),
    sample_size        = total_rolls,
)
```

### 8.2.3 Total Multiplier Symbols

```python
total_roll_multi_symbols_num =
    sum(roll.roll_multi_symbols_num for roll in all_rolls)
```

### 8.2.4 Multiplier Carry Value Distribution

```python
multiplier_carry_value_distribution =
    [v for roll in all_rolls for v in roll.roll_multi_symbols_carry]
```

### 8.2.5 Average Multiplier Carry Value

```python
carry_values = [v for roll in all_rolls for v in roll.roll_multi_symbols_carry]
avg_multiplier_carry_value = sum(carry_values) / len(carry_values)
```

Scalar. Filtered to rolls with multiplier symbols — NOT CI-eligible.

### 8.2.6 Maximum Multiplier Carry Value

```python
max_multiplier_carry_value =
    max(v for roll in all_rolls for v in roll.roll_multi_symbols_carry)
```

## 8.3 Roll Scatter Metrics

### 8.3.1 Average Scatter Symbols per Roll

```python
avg_roll_scatter_symbols_num = StatisticalMetric(
    observed           = sum(roll.roll_scatter_symbols_num for roll in all_rolls) / total_rolls,
    standard_deviation = sample_std([roll.roll_scatter_symbols_num for roll in all_rolls]),
    sample_size        = total_rolls,
)
```

### 8.3.2 Scatter-Containing Roll Frequency

```python
roll_with_scatter_symbol_frequency = StatisticalMetric(
    observed           = len([roll for roll in all_rolls if roll.roll_scatter_symbols_num > 0]) / total_rolls,
    standard_deviation = sample_std([1 if roll.roll_scatter_symbols_num > 0 else 0 for roll in all_rolls]),
    sample_size        = total_rolls,
)
```

### 8.3.3 Scatter Symbol Count Distribution per Roll

```python
scatter_symbol_count_distribution_per_roll =
    [roll.roll_scatter_symbols_num for roll in all_rolls]
```

## 8.4 Roll Distribution Metrics

### 8.4.1 Roll Win Amount Distribution

```python
roll_win_amount_distribution =
    [roll.roll_win_amount for roll in all_rolls]
```

### 8.4.2 Roll Win Amount Quantiles

Typical outputs may include:

```python
p50, p90, p95, p99
```

Computed from:

```python
roll_win_amount_quantiles =
    [roll.roll_win_amount for roll in all_rolls]
```

---

# 9. Structural Rules For Metrics

## 9.1 Determinism

```python
CanonicalResult -> identical MetricsBundle
```

Metrics computation must be deterministic.

## 9.2 Allowed Data Sources

Metrics may use only:

- `simulation_metadata`
- `BetRecord`
- `RoundRecord`
- `RollRecord`

Metrics must not use:

- validation outputs
- expected values
- confidence intervals
- hidden engine state
- external reference data

## 9.3 No Side Effects

Metrics computation must not:

- modify canonical records
- reorder canonical records
- add interpretation back into canonical

## 9.4 No Hidden Reconstruction

Metrics must not invent non-recorded states.

Allowed:

- aggregate
- partition
- count
- sum
- normalize
- quantify distributions

Not allowed:

- infer missing control logic
- reconstruct non-recorded trigger states
- create new canonical facts

---

# 10. Minimal API

```python
compute_metrics(result: CanonicalResult) -> MetricsBundle
```

---

# 11. Non-Goals

This file does not define:

- pass / fail rules
- RTP acceptance ranges
- statistical confidence intervals
- regression drift thresholds
- fairness claims
- player-experience judgement

Those belong to the validation layer, not the metrics layer.

---

# 12. Summary

The metrics layer provides:

- bet-level descriptive metrics
- round-level descriptive metrics
- roll-level descriptive metrics
- basic vs free split metrics
- multiplier statistics
- scatter and awarded free-round statistics
- distribution and tail descriptions
- volatility-oriented descriptive spread metrics

It remains strictly downstream of canonical and strictly upstream of validation.
