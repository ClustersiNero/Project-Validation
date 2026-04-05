# statistical_validation.md

## 0. Purpose

This file defines the **statistical validation layer**.

It specifies:

- how metrics are evaluated against expectations
- how uncertainty is handled
- what constitutes acceptable deviation

This layer **interprets metrics**, but must not modify them.

---

## 1. Core Principle

> Validation evaluates, but does not generate or alter data.

Rules:

- input must be MetricsBundle
- output must be explicit and reproducible
- all decisions must be explainable

---

## 2. Input / Output

### Input

- MetricsBundle
- ValidationRules
- (optional) BaselineMetrics

### Output

ValidationReport = {
    "meta": ValidationMeta,
    "checks": list[CheckResult],
    "summary": ValidationSummary
}

---

## 3. ValidationMeta

ValidationMeta = {
    "run_id": str,
    "config_id": str,
    "validation_version": str,
    "timestamp": str
}

---

## 4. Core Concepts

### 4.1 Expected Value

Each metric may have:

- expected_value (if known)
- expected_range (if defined)

---

### 4.2 Variance & Uncertainty

We treat simulation output as a **sample estimate**.

Key idea:

- observed value ≠ true value
- must consider sampling error

---

## 5. Confidence Interval (CI)

For RTP-like metrics:

CI = mean ± z * (std / sqrt(n))

Where:

- mean = observed metric
- std = sample std deviation
- n = number of samples
- z = confidence factor (e.g. 1.96 for 95%)

---

## 6. Validation Rules

### 6.1 Range Check

Check if observed value falls within expected range:

within_range = (lower <= observed <= upper)

---

### 6.2 CI-Based Check

If expected value exists:

pass_if = expected_value ∈ CI

---

### 6.3 Deviation Check

deviation = observed - expected_value

relative_deviation = deviation / expected_value

---

## 7. Sample Size Rule

Validation must consider sample size:

- small n → high uncertainty
- large n → stable estimate

Rule:

- minimum wagers required for RTP validation
- warn if below threshold

---

## 8. Regression Check

Compare against baseline:

drift = observed - baseline

Used to detect:

- unintended changes
- instability across versions

---

## 9. CheckResult Structure

CheckResult = {
    "metric": str,
    "observed": float,
    "expected": float | None,
    "range": tuple | None,
    "ci": tuple | None,
    "deviation": float | None,
    "verdict": str,
    "notes": str
}

---

## 10. Verdict Types

- "pass"
- "fail"
- "warn"

Rules:

- must be deterministic
- must be rule-based, not subjective

---

## 11. Structural Rules

### Determinism

Metrics + rules → identical ValidationReport

---

### Transparency

All results must include:

- observed value
- expected / range
- reasoning (CI / deviation)

---

### Separation of Concerns

- validation must not recompute metrics
- validation must not depend on engine

---

## 12. Non-Goals

- no fairness proof
- no guarantee of real-world behavior
- no player experience judgement
- no adaptive logic

---

## Summary

Statistical validation:

- interprets metrics under uncertainty
- uses CI and deviation checks
- produces structured, explainable verdicts

It is the **decision layer**, built on top of metrics.
