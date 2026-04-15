
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

# 3. Input / Output

## 3.1 Input

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

Whenever a denominator is zero, the metric implementation must return a deterministic empty or null-equivalent value according to implementation convention.

This specification defines formulas only.
It does not define validation or fallback policy.

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
empirical_rtp = total_bet_win_amount / total_bet_amount
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
bet_hit_frequency = count(bet.bet_win_amount > 0) / total_bets
```

### 6.1.5 Average Bet Win

```python
avg_bet_win_amount = sum(bet.bet_win_amount for bet in bets) / total_bets
```

### 6.1.6 Average Bet Win When Hit

```python
avg_bet_win_amount_when_hit =
    sum(bet.bet_win_amount for bet in bets if bet.bet_win_amount > 0)
    / count(bet.bet_win_amount > 0)
```

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

Distribution input:

```python
bet_win_amount_distribution = 
    [bet.bet_win_amount for bet in bets]
```

This distribution is expressed on absolute win amount.

### 6.2.2 Bet Win Multiple Distribution

```python
bet_win_multiple = bet.bet_win_amount / bet_level
```

This represents normalized payout multiple relative to bet_level.

Distribution input:

```python
bet_win_multiple_distribution =
    [bet.bet_win_amount / bet_level for bet in bets]
```

This distribution is the preferred normalized bet-level distribution basis.

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

Tail metrics remain descriptive and distribution-based.

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
avg_round_count_per_bet = sum(bet.round_count for bet in bets) / total_bets
```

### 6.4.2 Round Count Distribution per Bet

Distribution input:

```python
round_count_distribution_per_bet =
    [bet.round_count for bet in bets]
```

### 6.4.3 Free-Containing Bet Frequency

A bet contains free rounds if at least one round in rounds has round_type == "free"

Metric formula:

```python
free_containing_bet_frequency =
    count(bet where any(round.round_type == "free")) / total_bets
```

This remains descriptive only.

## 6.5 Bet Volatility-Oriented Descriptive Metrics

These metrics describe spread and concentration only.

### 6.5.1 Bet Win Multiple Mean

```python
mean_bet_win_multiple =
    sum(bet.bet_win_amount / bet_level for bet in bets) / total_bets
```

### 6.5.2 Bet Win Multiple Variance

Computed from:

```python
bet_win_multipler_variance =
    [bet.bet_win_amount / bet_level for bet in bets]
```

### 6.5.3 Bet Win Multiple Standard Deviation

Computed from:

```python
bet_win_multiple_standard_deviation =
    [bet.bet_win_amount / bet_level for bet in bets]
```

These are descriptive volatility-related metrics only.

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

## 7.1 Round Core Metrics

### 7.1.1 Average Round Win Amount

```python
avg_round_win_amount =
    sum(round.round_win_amount for all rounds)
    / total_rounds
```

### 7.1.2 Round Hit Frequency

```python
round_hit_frequency =
    count(round.round_win_amount > 0)
    / total_rounds
```

### 7.1.3 Base Symbol Win Amount

```python
avg_base_symbol_win_amount_per_round =
    sum(round.base_symbol_win_amount for all rounds)
    / total_rounds
```

### 7.1.4 Multiplier Contribution

```python
avg_multiplier_contribution_per_round =
    sum(
        round.base_symbol_win_amount * (round.round_total_multiplier - 1)
        for all rounds
    )
    / total_rounds
```

### 7.1.5 Average Scatter Win Amount per Round

```python
avg_scatter_win_amount_per_round =
    sum(round.scatter_win_amount for all rounds)
    / total_rounds
```

## 7.2 Basic Round Metrics

Basic round metrics are computed from rounds where:

```python
round.round_type == "basic"
```

### 7.2.1 Basic Round Count

```python
basic_round_count = count(round.round_type == "basic")
```

### 7.2.2 Average Basic Round Win Amount

```python
avg_basic_round_win_amount =
    sum(round.round_win_amount for basic rounds)
    / basic_round_count
```

### 7.2.3 Basic Round Hit Frequency

```python
basic_round_hit_frequency =
    count(round.round_win_amount > 0 for basic rounds)
    / basic_round_count
```

### 7.2.4 Average Basic Scatter Increment

```python
avg_basic_round_scatter_increment =
    sum(round.round_scatter_increment for basic rounds)
    / basic_round_count
```

### 7.2.5 Average Awarded Free Rounds from Basic Rounds

```python
avg_award_free_rounds_from_basic_round =
    sum(round.award_free_rounds for basic rounds)
    / basic_round_count
```

## 7.3 Free Round Metrics

Free round metrics are computed from rounds where:

```python
round.round_type == "free"
```

### 7.3.1 Free Round Count

```python
free_round_count = count(round.round_type == "free")
```

### 7.3.2 Average Free Round Win Amount

```python
avg_free_round_win_amount =
    sum(round.round_win_amount for free rounds)
    / free_round_count
```

### 7.3.3 Free Round Hit Frequency

```python
free_round_hit_frequency =
    count(round.round_win_amount > 0 for free rounds)
    / free_round_count
```

### 7.3.4 Average Free Scatter Increment

```python
avg_free_round_scatter_increment =
    sum(round.round_scatter_increment for free rounds)
    / free_round_count
```

### 7.3.5 Average Awarded Free Rounds from Free Rounds

```python
avg_award_free_rounds_from_free_round =
    sum(round.award_free_rounds for free rounds)
    / free_round_count
```


## 7.4 Round Multiplier Metrics

These metrics describe multiplier behavior strictly based on recorded fields in `RoundRecord`.

All metrics are partitioned by `round_type` where relevant, to reflect distinct multiplier dynamics in `basic` and `free` rounds.

### 7.4.1 Multiplier Increment Frequency (All Rounds)

```python
multiplier_increment_frequency =
    count(round.round_multiplier_increment > 0)
    / total_rounds
```

### 7.4.2 Multiplier Increment Frequency (Basic Rounds)

```python
basic_round_multiplier_increment_frequency =
    count(round.round_multiplier_increment > 0 for basic rounds)
    / basic_round_count
```

### 7.4.3 Multiplier Increment Frequency (Free Rounds)

```python
free_round_multiplier_increment_frequency =
    count(round.round_multiplier_increment > 0 for free rounds)
    / free_round_count
```

### 7.4.4 Average Multiplier Increment (All Rounds)

```python
avg_round_multiplier_increment =
    sum(round.round_multiplier_increment for all rounds)
    / total_rounds
```

### 7.4.5 Average Multiplier Increment (Basic Rounds)

```python
avg_basic_round_multiplier_increment =
    sum(round.round_multiplier_increment for basic rounds)
    / basic_round_count
```

### 7.4.6 Average Multiplier Increment (Free Rounds)

```python
avg_free_round_multiplier_increment =
    sum(round.round_multiplier_increment for free rounds)
    / free_round_count
```

### 7.4.7 Maximum Multiplier Increment

```python
max_round_multiplier_increment =
    max(round.round_multiplier_increment for all rounds)
```

### 7.4.8 Average Round Total Multiplier (All Rounds)

```python
avg_round_total_multiplier =
    sum(round.round_total_multiplier for all rounds)
    / total_rounds
```

### 7.4.9 Average Round Total Multiplier (Basic Rounds)

```python
avg_basic_round_total_multiplier =
    sum(round.round_total_multiplier for basic rounds)
    / basic_round_count
```

### 7.4.10 Average Round Total Multiplier (Free Rounds)

```python
avg_free_round_total_multiplier =
    sum(round.round_total_multiplier for free rounds)
    / free_round_count
```

### 7.4.11 Maximum Round Total Multiplier

```python
max_round_total_multiplier =
    max(round.round_total_multiplier for all rounds)
```

### 7.4.12 Average Global Multiplier at Free Round Start

Global multiplier accumulation is only meaningful in free rounds.

```python
avg_global_multiplier_at_free_round_start =
    sum(round.global_multiplier for free rounds)
    / free_round_count
```

### 7.4.13 Maximum Global Multiplier

```python
max_global_multiplier =
    max(round.global_multiplier for all rounds)
```

### 7.4.14 Round Total Multiplier Distribution (All Rounds)

```python
round_total_multiplier_distribution_all_rounds =
    [round.round_total_multiplier for round in all_rounds]
```

### 7.4.15 Round Total Multiplier Distribution (Basic Rounds)

```python
round_total_multiplier_distribution_basic_rounds =
    [round.round_total_multiplier for round in basic_rounds]
```

### 7.4.16 Round Total Multiplier Distribution (Free Rounds)

```python
round_total_multiplier_distribution_free_rounds =
    [round.round_total_multiplier for round in free_rounds]
```

---


## 7.5 Round Scatter Metrics

### 7.5.1 Average Scatter Increment (All Rounds)

```python
avg_round_scatter_increment_all_rounds =
    sum(round.round_scatter_increment for all rounds)
    / total_rounds
```



### 7.5.2 Average Scatter Increment (Basic Rounds)

```python
avg_round_scatter_increment_basic_rounds =
    sum(round.round_scatter_increment for basic rounds)
    / basic_round_count
```

### 7.5.3 Average Scatter Increment (Free Rounds)

```python
avg_round_scatter_increment_free_rounds =
    sum(round.round_scatter_increment for free rounds)
    / free_round_count
```

### 7.5.4 Scatter Win Frequency (All Rounds)

```python
scatter_win_frequency_all_rounds =
    count(round.scatter_win_amount > 0)
    / total_rounds
```

### 7.5.5 Scatter Win Frequency (Basic Rounds)

```python
scatter_win_frequency_basic_rounds =
    count(round.scatter_win_amount > 0 for basic rounds)
    / basic_round_count
```

### 7.5.6 Scatter Win Frequency (Free Rounds)

```python
scatter_win_frequency_free_rounds =
    count(round.scatter_win_amount > 0 for free rounds)
    / free_round_count
```

### 7.5.7 Average Scatter Win Amount (All Rounds)

```python
avg_scatter_win_amount_all_rounds =
    sum(round.scatter_win_amount for all rounds)
    / total_rounds
```

### 7.5.8 Average Scatter Win Amount (Basic Rounds)

```python
avg_scatter_win_amount_basic_rounds =
    sum(round.scatter_win_amount for basic rounds)
    / basic_round_count
```

### 7.5.9 Average Scatter Win Amount (Free Rounds)

```python
avg_scatter_win_amount_free_rounds =
    sum(round.scatter_win_amount for free rounds)
    / free_round_count
```

### 7.5.10 Free-Round Award Frequency (All Rounds)

```python
award_free_round_frequency_all_rounds =
    count(round.award_free_rounds > 0)
    / total_rounds
```

### 7.5.11 Free-Round Award Frequency (Basic Rounds)

```python
award_free_round_frequency_basic_rounds =
    count(round.award_free_rounds > 0 for basic rounds)
    / basic_round_count
```

### 7.5.12 Free-Round Award Frequency (Free Rounds)

```python
award_free_round_frequency_free_rounds =
    count(round.award_free_rounds > 0 for free rounds)
    / free_round_count
```

### 7.5.13 Free-Round Award Frequency (All Rounds)

```python
award_free_round_frequency_all_rounds =
    count(round.award_free_rounds > 0 for all rounds)
    / total_rounds
```

---

## 7.6 Round Distribution Metrics

### 7.6.1 Round Win Amount Distribution (All Rounds)

```python
round_win_amount_distribution_all_rounds =
    [round.round_win_amount for all rounds]
```

### 7.6.2 Round Win Amount Distribution (Basic Rounds)

```python
round_win_amount_distribution_basic_rounds =
    [round.round_win_amount for basic rounds]
```

### 7.6.3 Round Win Amount Distribution (Free Rounds)

```python
round_win_amount_distribution_free_rounds =
    [round.round_win_amount for free rounds]
```

### 7.6.4 Base Symbol Win Amount Distribution (All Rounds)

```python
base_symbol_win_amount_distribution_all_rounds =
    [round.base_symbol_win_amount for all rounds]
```

### 7.6.5 Base Symbol Win Amount Distribution (Basic Rounds)

```python
base_symbol_win_amount_distribution_basic_rounds =
    [round.base_symbol_win_amount for basic rounds]
```

### 7.6.6 Base Symbol Win Amount Distribution (Free Rounds)

```python
base_symbol_win_amount_distribution_free_rounds =
    [round.base_symbol_win_amount for free rounds]
```

### 7.6.7 Multiplier Contribution Distribution (All Rounds)

```python
multiplier_contribution_distribution_all_rounds =
    [
        round.base_symbol_win_amount * (round.round_total_multiplier - 1)
        for all rounds
    ]
```

### 7.6.8 Multiplier Contribution Distribution (Basic Rounds)

```python
multiplier_contribution_distribution_basic_rounds =
    [
        round.base_symbol_win_amount * (round.round_total_multiplier - 1)
        for basic rounds
    ]
```

### 7.6.9 Multiplier Contribution Distribution (Free Rounds)

```python
multiplier_contribution_distribution_free_rounds =
    [
        round.base_symbol_win_amount * (round.round_total_multiplier - 1)
        for free rounds
    ]
```

### 7.6.10 Scatter Win Amount Distribution (All Rounds)

```python
scatter_win_amount_distribution_all_rounds =
    [round.scatter_win_amount for all rounds]
```

### 7.6.11 Scatter Win Amount Distribution (Basic Rounds)

```python
scatter_win_amount_distribution_basic_rounds =
    [round.scatter_win_amount for basic rounds]
```

### 7.6.12 Scatter Win Amount Distribution (Free Rounds)

```python
scatter_win_amount_distribution_free_rounds =
    [round.scatter_win_amount for free rounds]
```

### 7.6.13 Round Total Multiplier Distribution (All Rounds)

```python
round_total_multiplier_distribution_all_rounds =
    [round.round_total_multiplier for all rounds]
```

### 7.6.14 Round Total Multiplier Distribution (Basic Rounds)

```python
round_total_multiplier_distribution_basic_rounds =
    [round.round_total_multiplier for basic rounds]
```

### 7.6.15 Round Total Multiplier Distribution (Free Rounds)

```python
round_total_multiplier_distribution_free_rounds =
    [round.round_total_multiplier for free rounds]
```

## 7.7 Round Structure Metrics

### 7.7.1 Average Rolls per Round (All Rounds)

```python
avg_roll_count_per_round_all_rounds =
    sum(round.roll_count for all rounds)
    / total_rounds
```

### 7.7.2 Average Rolls per Round (Basic Rounds)

```python
avg_roll_count_per_round_basic_rounds =
    sum(round.roll_count for basic rounds)
    / basic_round_count
```

### 7.7.3 Average Rolls per Round (Free Rounds)

```python
avg_roll_count_per_round_free_rounds =
    sum(round.roll_count for free rounds)
    / free_round_count
```

### 7.7.4 Roll Count Distribution per Round (All Rounds)

Distribution input:

```python
roll_count_distribution_all_rounds =
    [round.roll_count for all rounds]
```

### 7.7.5 Roll Count Distribution per Round (Basic Rounds)

Distribution input:

```python
roll_count_distribution_basic_rounds =
    [round.roll_count for basic rounds]
```

### 7.7.6 Roll Count Distribution per Round (Free Rounds)

Distribution input:

```python
roll_count_distribution_free_rounds =
    [round.roll_count for free rounds]
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
avg_roll_win_amount =
    sum(roll.roll_win_amount for all rolls)
    / total_rolls
```

### 8.1.2 Roll Hit Frequency

```python
roll_hit_frequency =
    count(roll.roll_win_amount > 0)
    / total_rolls
```

### 8.1.3 Roll Type Distribution

Distribution input:

```python
roll_type_distribution =
    [roll.roll_type for all rolls]
```

This metric is descriptive only.
It does not interpret engine semantics beyond the recorded field.

## 8.2 Roll Multiplier Metrics

### 8.2.1 Average Multiplier Symbols per Roll

```python
avg_roll_multi_symbols_num =
    sum(roll.roll_multi_symbols_num for all rolls)
    / total_rolls
```

### 8.2.2 Multiplier-Symbol Roll Frequency

```python
roll_with_multiplier_symbol_frequency =
    count(roll.roll_multi_symbols_num > 0)
    / total_rolls
```

### 8.2.3 Total Multiplier Symbols

```python
total_roll_multi_symbols_num =
    sum(roll.roll_multi_symbols_num for all rolls)
```

### 8.2.4 Multiplier Carry Value Distribution

Distribution input:

```python
multiplier_carry_varry_distribution =
    [value for all rools for value in roll.rool_multi_symbols_carry]
```

### 8.2.5 Average Multiplier Carry Value

```python
avg_multiplier_carry_value =
    sum(all values in all roll.roll_multi_symbols_carry)
    / count(all values in all roll.roll_multi_symbols_carry)
```

### 8.2.6 Maximum Multiplier Carry Value

```python
max_multiplier_carry_value =
    max(value for all rolls for value in roll.roll_multi_symbols_carry)
```

## 8.3 Roll Scatter Metrics

### 8.3.1 Average Scatter Symbols per Roll

```python
avg_roll_scatter_symbols_num =
    sum(roll.roll_scatter_symbols_num for all rolls)
    / total_rolls
```

### 8.3.2 Scatter-Containing Roll Frequency

```python
roll_with_scatter_symbol_frequency =
    count(roll.roll_scatter_symbols_num > 0)
    / total_rolls
```

### 8.3.3 Scatter Symbol Count Distribution per Roll

Distribution input:

```python
scatter_symbol_count_distribution_per_roll =
    [roll.roll_scatter_symbols_num for all rolls]
```

## 8.4 Roll Distribution Metrics

### 8.4.1 Roll Win Amount Distribution

Distribution input:

```python
roll_win_amount_distribution =
    [roll.roll_win_amount for all rolls]
```

### 8.4.2 Roll Win Amount Quantiles

Typical outputs may include:

```python
p50, p90, p95, p99
```

Computed from:

```python
roll_win_amount_quantiles =
    [roll.roll_win_amount for all rolls]
```

---

# 9. Cross-Level Consistency Metrics

These metrics remain descriptive summaries derived from canonical hierarchy.

## 9.1 Average Free Rounds per Bet

Computed from round partition:

```python
avg_free_rounds_per_bet =
    count(free rounds) / total_bets
```

## 9.2 Average Basic Rounds per Bet

```python
avg_basic_rounds_per_bet =
    count(basic rounds) / total_bets
```

In the current engine flow, this is expected to reflect one initial basic round per bet, but metrics only report the observed value.

## 9.3 Average Rolls per Bet

```python
avg_rolls_per_bet = total_rolls / total_bets
```

---

# 10. Structural Rules For Metrics

## 10.1 Determinism

```python
CanonicalResult -> identical MetricsBundle
```

Metrics computation must be deterministic.

## 10.2 Allowed Data Sources

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

## 10.3 No Side Effects

Metrics computation must not:

- modify canonical records
- reorder canonical records
- add interpretation back into canonical

## 10.4 No Hidden Reconstruction

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

# 11. Minimal API

```python
compute_metrics(result: CanonicalResult) -> MetricsBundle
```

---

# 12. Non-Goals

This file does not define:

- pass / fail rules
- RTP acceptance ranges
- statistical confidence intervals
- regression drift thresholds
- fairness claims
- player-experience judgement

Those belong to the validation layer, not the metrics layer.

---

# 13. Summary

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
