# Validation Specification

## 0. Purpose

This file defines the **validation layer** for the slot math system.

The validation layer evaluates canonical results and computed metrics against declared rules. It produces an explicit, reproducible, and explainable report.

Pipeline position:

```
config → engine → canonical → metrics → validation
```

The validation layer:

- MUST ONLY evaluate
- MUST NOT modify any upstream data
- MUST NOT recompute metrics
- MUST NOT depend on engine logic

---

## 1. Core Principle

> Validation evaluates, but does not generate or alter data.

Rules:

- all inputs must be read-only
- all outputs must be fully reproducible
- all decisions must be explicit and rule-driven
- verdicts must be deterministic given fixed inputs and rules

---

## 2. Validation Categories

Validation is split into exactly three independent categories:

| Category | Input | Purpose |
|---|---|---|
| A. Structural Validation | CanonicalResult, config | Schema and consistency checks |
| B. Statistical Validation | MetricsBundle, ValidationRules | Expectation and CI-based checks |
| C. Regression Validation | MetricsBundle, BaselineMetrics | Drift detection against a known baseline |

All three categories are required. No category may be merged or omitted.

---

## 3. Input / Output

### 3.1 Inputs

```python
# Required for structural validation
CanonicalResult  # canonical_spec.md
config           # config_spec.md

# Required for statistical validation
MetricsBundle    # metrics_spec.md
ValidationRules  # defined below in §6

# Required for regression validation
MetricsBundle    # metrics_spec.md
BaselineMetrics  # dict[str → float], externally supplied
```

### 3.2 Output

```python
ValidationReport = {
    "meta": ValidationMeta,
    "structural_checks": list[CheckResult],
    "statistical_checks": list[CheckResult],
    "regression_checks": list[CheckResult],
    "summary": ValidationSummary,
}
```

---

## 4. Schema Definitions

### 4.1 ValidationMeta

```python
ValidationMeta = {
    "simulation_id": str,
    "config_id": str,
    "config_version": str,
    "schema_version": str,
    "engine_version": str,
    "validation_version": str,
    "timestamp": str,
}
```

Field sources:

- `simulation_id`, `config_id`, `config_version`, `schema_version`, `engine_version`, `timestamp` are projected from `CanonicalResult.simulation_metadata`. The validation layer MUST NOT recompute or alter these fields.
- `validation_version` is provided by the validation layer itself as validation artifact metadata. It identifies the version of the validation logic applied, and is not sourced from `CanonicalResult`.

The validation layer MUST NOT recompute or alter any upstream business data.

---

### 4.2 CheckResult

```python
CheckResult = {
    "metric_path": str,         # full nested MetricsBundle path, e.g. "MetricsBundle.round_metrics.core.avg_round_win_amount"
    "observed": float | None,
    "expected": float | None,
    "range": tuple[float, float] | None,
    "deviation": float | None,
    "verdict": str,             # "pass" or "fail" only
    "notes": str,
}
```

Rules:

- `verdict` MUST be exactly `"pass"` or `"fail"`. No `"warn"` state.
- `observed` is the value read from upstream. It MUST NOT be recomputed.
- `expected`, `range`, `deviation` are populated only when applicable to the check type.
- `metric_path` MUST store the full nested `MetricsBundle.<group>.<subgroup>.<metric_name>` path, or the invariant identifier for structural checks.
- `notes` is a human-readable explanation of the verdict. It must not encode logic.

---

### 4.3 ValidationSummary

```python
ValidationSummary = {
    "total_checks": int,
    "passed": int,
    "failed": int,
    "structural_passed": int,
    "structural_failed": int,
    "statistical_passed": int,
    "statistical_failed": int,
    "regression_passed": int,
    "regression_failed": int,
    "overall_verdict": str,  # "pass" if all checks pass, otherwise "fail"
}
```

`overall_verdict` is `"pass"` if and only if `failed == 0`.

---

## 5. Structural Validation

### 5.1 Purpose

Structural validation checks that `CanonicalResult` is schema-correct, internally consistent, and consistent with the config that produced it.

Structural validation MUST NOT use `MetricsBundle`.

### 5.2 Required Checks

#### 5.2.1 Schema Presence

For each required top-level field in `CanonicalResult`:

- `simulation_metadata` must be present and non-null
- `bets` must be present and non-empty

`bets` must be non-empty for this validation spec. The zero-sample / null handling in `MetricsBundle` (`sample_size == 0` → null fields) is a generic metric-schema contract governing how metrics represent empty populations. It does not imply that a canonical simulation with no bets is valid input for validation.

For `SimulationMetadata`, all of the following fields must be present and non-null:

- `simulation_id`, `config_id`, `config_version`, `engine_version`, `schema_version`, `mode`, `seed`, `bet_amount`, `bet_level`, `total_bets`, `timestamp`

Verdict: `"fail"` if any required field is absent or null.

`timestamp` is a structural audit metadata field. Structural validation MUST verify presence and non-nullness. It MUST NOT use timestamp value differences alone as evidence of outcome non-reproducibility. If timestamp format validation is required, the accepted format MUST be declared explicitly.

For each `BetRecord`:

- `bet_id`, `bet_win_amount`, `basic_win_amount`, `free_win_amount`, `round_count`, `rounds`, `bet_final_state` must be present

For each `RoundRecord`:

- `round_id`, `round_type`, `round_win_amount`, `base_symbol_win_amount`, `carried_multiplier`, `round_multiplier_increment`, `round_total_multiplier`, `round_scatter_increment`, `award_free_rounds`, `scatter_win_amount`, `roll_count`, `rolls`, `round_final_state` must be present

For each `RollRecord`:

- `roll_id`, `roll_win_amount`, `roll_type`, `strip_set_id`, `multiplier_profile_id`, `roll_filled_state`, `roll_final_state`, `roll_multi_symbols_num`, `roll_multi_symbols_carry`, `roll_scatter_symbols_num` must be present

Verdict: `"fail"` if any required field is absent or null.

#### 5.2.2 Top-Level Count Consistency

```
simulation_metadata.total_bets == len(bets)
```

Verdict: `"fail"` if the declared count does not match the actual number of `BetRecord` entries.

#### 5.2.3 Record Count Consistency

For each `BetRecord`:

```
round_count == len(rounds)
```

For each `RoundRecord`:

```
roll_count == len(rolls)
```

Verdict: `"fail"` if any mismatch is detected.

#### 5.2.4 Config-to-Canonical ID Validity

For each `RollRecord`:

- `strip_set_id` must exist as a key in `STRIP_SETS` (config)
- `multiplier_profile_id` must exist as a key in `MULTIPLIER_DATA["weight"]` (config)

Verdict: `"fail"` if any referenced id does not exist in config.

#### 5.2.5 Payout Aggregation Correctness

For each `RoundRecord`:

```
round_win_amount == base_symbol_win_amount * round_total_multiplier + scatter_win_amount
```

For each `BetRecord`:

```
bet_win_amount == sum(round.round_win_amount for round in rounds)
basic_win_amount == sum(round.round_win_amount for round in rounds if round.round_type == "basic")
free_win_amount == sum(round.round_win_amount for round in rounds if round.round_type == "free")
bet_win_amount == basic_win_amount + free_win_amount
```

Verdict: `"fail"` if any aggregation does not hold within floating-point tolerance (≤ 1e-9 relative difference).

#### 5.2.6 Version Consistency

- `simulation_metadata.config_version` must match the version of the config loaded for validation. Verdict: `"fail"` if they differ.
- `simulation_metadata.schema_version` must be a version supported by the validation layer. Verdict: `"fail"` if unsupported.
- `simulation_metadata.engine_version` must be consistent with the engine artifact or execution context supplied to validation. Verdict: `"fail"` if the declared version is not recognized.

These checks are structural. They do not apply statistical tolerances and do not move to statistical or regression categories.

#### 5.2.7 Ordering Invariant

Within each `BetRecord`:

- `round_id` values must be strictly ascending

Within each `RoundRecord`:

- `roll_id` values must be strictly ascending

Verdict: `"fail"` if any ordering is violated.

#### 5.2.8 round_type Validity

For each `RoundRecord`:

- `round_type` must be exactly `"basic"` or `"free"`

Verdict: `"fail"` if any other value is present.

#### 5.2.9 roll_type Validity

For each `RollRecord`:

- `roll_type` must be exactly `"initial"` or `"cascade"`
- The first roll of each round must have `roll_type == "initial"`
- Subsequent rolls within the same round must have `roll_type == "cascade"`

Verdict: `"fail"` if any condition is violated.

#### 5.2.10 round_total_multiplier Invariant

For each `RoundRecord`:

- if `round_multiplier_increment == 0`: `round_total_multiplier` must equal `1`
- if `round_multiplier_increment > 0`: `round_total_multiplier` must equal `carried_multiplier + round_multiplier_increment`

Verdict: `"fail"` if any condition is violated.

---

## 6. ValidationRules

`ValidationRules` provides the thresholds and parameters used by statistical validation. It is externally supplied and must not be defined or overridden inside validation logic.

```python
ValidationRules = {
    "metrics": {
        metric_path: {          # full MetricsBundle path, e.g. "MetricsBundle.round_metrics.core.avg_round_win_amount"
            "expected_value": float | None,
            "expected_range": tuple[float, float] | None,
            "z_value": float | None,
        }
    }
}
```

Rules:

- `metric_path` MUST match a full nested path from the Path Contract defined in `metrics_spec.md §3`. Flat metric names are forbidden.
- `expected_value` and `expected_range` are independent checks; both may be present.
- `z_value` is the operative CI multiplier. The validation layer MUST NOT default or infer it.
- A key with both `expected_value = null`, `expected_range = null`, and `z_value = null` produces no statistical check.
- If `z_value` is provided for a metric whose leaf type is not `StatisticalMetric`, validation MUST produce a `"fail"` verdict with `notes` indicating invalid configuration.
- If `z_value` is provided but the metric's `standard_deviation` is `null` or `sample_size < 2`, CI is non-computable; validation MUST produce a `"fail"` verdict and MUST NOT substitute `0`, epsilon, or any default.

---

## 7. Statistical Validation

### 7.1 Purpose

Statistical validation evaluates `MetricsBundle` against declared expectations using confidence intervals and range checks.

Statistical validation MUST NOT access `CanonicalResult` directly. It operates only on `MetricsBundle` and `ValidationRules`.

### 7.2 CI Eligibility and Check Direction

**Only metrics whose leaf type in `MetricsBundle` is `StatisticalMetric` are CI-eligible** (see `metrics_spec.md §3 CI Eligibility Boundary`). If `z_value` is declared for any other metric type, validation MUST fail that rule as invalid configuration.

For a CI-eligible metric, the check is:

```
pass_if: abs(observed - expected_value) <= z * (standard_deviation / sqrt(sample_size))
```

Where:

- `observed` = `MetricsBundle.<path>.observed`
- `standard_deviation` = `MetricsBundle.<path>.standard_deviation`
- `sample_size` = `MetricsBundle.<path>.sample_size`
- `z` = `ValidationRules.metrics[metric_path].z_value`

The validation layer MUST NOT:

- recompute `standard_deviation` or `sample_size`
- infer `sample_size` globally from `simulation_metadata`
- substitute any default when `standard_deviation` is `null` or `sample_size < 2`

If `standard_deviation` is `null` or `sample_size < 2`, the CI check MUST produce verdict `"fail"` with a note that CI is non-computable.

### 7.3 Check Types

#### 7.3.1 Expected Value Check (CI-Based)

Applicable when `expected_value` and `z_value` are both defined in `ValidationRules`, and the metric is CI-eligible.

```
pass_if: abs(observed - expected_value) <= z * (standard_deviation / sqrt(sample_size))
```

Verdict: `"pass"` if condition holds, `"fail"` otherwise.

#### 7.3.2 Range Check

Applicable when `expected_range` is defined in `ValidationRules`.

```
pass_if: lower <= observed <= upper
```

Verdict: `"pass"` if condition holds, `"fail"` otherwise.

#### 7.3.3 Metrics with Neither Check

If a metric has both `expected_value = null` and `expected_range = null`, no statistical check is generated for that metric. The metric is not included in `statistical_checks`.

### 7.4 Statistical Check Execution Rules

- One `CheckResult` is produced per applicable metric per check type (a metric may produce both a range check and a CI check if both are defined)
- `observed` must be read directly from `MetricsBundle` without transformation
- `deviation` is computed as `observed - expected_value` when `expected_value` is defined; otherwise `null`
- Thresholds MUST NOT be defined inside validation logic; they must come from `ValidationRules` only

---

## 8. Regression Validation

### 8.1 Purpose

Regression validation compares the current `MetricsBundle` against a previously captured `BaselineMetrics` to detect unintended drift.

Regression validation MUST NOT interpret business meaning. It MUST ONLY report deviation.

### 8.2 BaselineMetrics

```python
BaselineMetrics = {
    metric_path: {              # full MetricsBundle path
        "expected_value": float,
        "tolerance": float,     # MUST be externally supplied; MUST NOT be defaulted or inferred
    }
}
```

- Keys are full metric paths matching the Path Contract from `metrics_spec.md §3`
- `expected_value` is the baseline observed value from a reference run
- `tolerance` is the maximum acceptable absolute deviation; it MUST be explicitly declared
- `BaselineMetrics` is externally supplied and read-only

### 8.3 Drift Computation

For each metric path present in `BaselineMetrics`:

```
deviation = observed - expected_value
pass_if: abs(deviation) <= tolerance
```

Where:

- `observed`: `MetricsBundle.<path>.observed` (for `StatisticalMetric` leaf) or the scalar value
- `expected_value`: baseline reference value from `BaselineMetrics`
- `tolerance`: from `BaselineMetrics[metric_path].tolerance`

### 8.4 Regression Check Rules

- One `CheckResult` is produced per metric path present in `BaselineMetrics`
- `observed` = current metric value from `MetricsBundle`
- `expected` = `expected_value` from `BaselineMetrics`
- `deviation` = `observed - expected_value`
- `verdict`: `"pass"` if `abs(deviation) <= tolerance`, `"fail"` otherwise
- Validation MUST NOT invent a default `tolerance`; if `tolerance` is absent the rule MUST be treated as misconfigured and produce `"fail"`
- Regression validation MUST NOT assign meaning to the sign or magnitude of drift

---

## 9. Global Rules

### 9.1 Determinism

Given identical inputs (`CanonicalResult`, `MetricsBundle`, `ValidationRules`, `BaselineMetrics`), the `ValidationReport` MUST be identical across executions.

### 9.2 Separation of Concerns

- Structural validation MUST NOT use `MetricsBundle`
- Statistical validation MUST NOT access `CanonicalResult` directly
- Regression validation MUST NOT access `CanonicalResult` directly
- Validation MUST NOT recompute metrics
- Validation MUST NOT call engine logic

### 9.3 Forbidden

- No minimum bet threshold gating
- No adaptive logic
- No runtime condition branching on player state
- No player-dependent logic
- No mixing of metric computation into validation checks
- No `"warn"` verdict state

---

## 10. Non-Goals

The following are explicitly outside the scope of this layer:

- Defining what constitutes a correct RTP (that is a config / design concern)
- Generating or transforming canonical records
- Modifying metrics values
- Defining game rules or engine behavior
- Fairness proof or guarantee of real-world behavior
- Player experience judgement or adaptive logic

---

## 11. Summary

Statistical validation:

- interprets metrics under uncertainty
- uses CI deviation checks (`abs(observed - expected) <= z * std / sqrt(n)`) and range checks
- produces structured, explainable verdicts

It is the **decision layer**, built on top of metrics.
