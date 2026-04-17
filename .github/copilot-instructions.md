# Copilot Working Charter — Validation Project

This file defines **strict implementation rules** for Copilot in this repository.

---

## 1. Single Source of Truth (MANDATORY)

The ONLY authoritative documents are:

* system_scope_spec.md
* architecture_spec.md
* config_spec.md
* engine_spec.md
* canonical_spec.md
* metrics_spec.md
* validation_spec.md

### Authority rule

* All implementation MUST follow these specs
* If any conflict exists → specs override all other files
* No file may redefine semantics defined in specs

### Non-authoritative files

The following are reference only (NOT sources of truth):

* directory structure suggestions
* ADR / notes / roadmap
* scripts / CLI / pipeline helpers
* legacy_reference/

They MUST NOT:

* define new rules
* override spec semantics
* introduce parallel concepts

---

## 2. Mandatory Layering (CANNOT BE BROKEN)

Strict architecture:

config → engine → canonical → metrics → validation

### Responsibilities

* config
  defines possibility space only

* engine
  deterministic result generation only

* canonical
  full record only (no interpretation)

* metrics
  descriptive computation only (no judgement)

* validation
  judgement only (no data modification)

### Forbidden

* cross-layer logic
* hidden dependencies
* upstream data mutation

---

## 3. Naming Contract (STRICT)

Only allowed hierarchy:

Bet → Round → Roll

### Forbidden terms

* wager
* stake
* spin
* step

### Rules

* naming must match specs exactly
* no parallel terminology
* no legacy naming carry-over

---

## 4. Determinism & Reproducibility

The system MUST be:

* deterministic under fixed seed + config
* fully reproducible
* audit-ready

### Forbidden

* hidden randomness
* environment-dependent behavior
* uncontrolled state mutation

---

## 5. Safety Boundaries (HARD BLOCK)

NEVER introduce:

* reroll
* filter / accept-reject
* runtime probability adjustment
* player-dependent logic
* adaptive behavior
* outcome steering
* control-level / pool / protection logic

This system is:

* validation system
  NOT:
* runtime control system

---

## 6. Canonical / Metrics / Validation Contracts

### Canonical

MUST be:

* deterministic
* neutral
* complete
* replayable

MUST NOT contain:

* metrics
* RTP
* judgement
* inferred states

---

### Metrics

MUST:

* be computed from CanonicalResult only
* be deterministic
* be descriptive only

MUST NOT:

* include thresholds
* include pass/fail
* include validation logic

---

### Validation

MUST:

* consume MetricsBundle
* produce ValidationReport

MUST NOT:

* modify canonical
* modify metrics
* recompute upstream logic

---

## 7. Implementation Strategy

### General rule

* prefer minimal changes
* reuse existing structures
* do not introduce parallel systems

### Current priority

ONLY focus on:

1. engine correctness
2. canonical completeness
3. metrics correctness
4. validation correctness

DO NOT prioritize:

* CLI
* reporting
* export
* pipeline orchestration
* performance optimization

---

## 8. Directory Usage Constraint (IMPORTANT)

Even if directories exist, DO NOT expand:

* configs/run
* configs/export
* scripts/
* reporting/
* pipeline/
* CLI tools

UNLESS explicitly required.

Focus only on core layers.

---

## 9. Legacy Reference Rule

If `legacy_reference/` exists:

Allowed:

* understand valid predefined logic
* extract deterministic behavior

Forbidden:

* copying code directly
* keeping control logic
* keeping legacy naming

Process:

1. identify valid logic
2. discard unsafe logic
3. remap into current architecture

---

## 10. Required Working Method

Before implementing:

1. read relevant spec sections
2. locate corresponding code files
3. confirm layer responsibility
4. list files to modify
5. implement minimal change
6. When a legacy pattern conflicts with current specs, discard the legacy pattern immediately and follow the specs.

---

## 11. Self-Check Checklist (REQUIRED)

After implementation, ALWAYS output:

1. Files modified
2. Why each file changed
3. Behavior change (before vs after)
4. Which spec rules were applied
5. What was NOT changed
6. Confirm NO forbidden logic introduced:

   * reroll
   * filtering
   * runtime manipulation
   * player-dependent logic
7. Reviewer checkpoints:

   * key functions
   * key variables
   * critical branches

---

## 12. Core Principle

This is a validation-first system.

Goal:

* correctness
* reproducibility
* statistical consistency

NOT:

* game tuning
* player modeling
* commercial optimization

---

## 13. Legacy Reference Rule

`legacy_reference/` is reference-only.

It is NOT source of truth.

Current implementation MUST follow the current spec files, not legacy files.

Code from `legacy_reference/` MUST NOT be copied directly into the current implementation.

Allowed reference scope:
- deterministic RNG ideas
- roll-level board progression
- clear / gravity / refill order
- other predefined deterministic behavior that does not conflict with current specs
- reference must not introduce new implicit rules not defined in specs

Forbidden legacy concepts:
- pool
- waterline
- control_level
- protect
- reroll
- odds_range gating
- player/state-dependent adjustment
- runtime probability adjustment
- outcome steering

Also forbidden:
- inheriting legacy naming directly
- inheriting legacy config keys directly
- inheriting legacy interfaces directly

Use legacy files only to understand old behavior, then remap valid parts into the current architecture and naming.