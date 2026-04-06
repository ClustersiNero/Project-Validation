# Copilot Working Charter For This Repository

This file defines persistent implementation rules for Copilot in this repository.

## 1. Authoritative Documents

Always treat the following files as the primary source of truth:

- docs/General Provisions/system_scope_spec.md
- docs/General Provisions/architecture_spec.md
- docs/General Provisions/canonical_spec.md
- docs/General Provisions/metrics_spec.md
- docs/General Provisions/validation_spec.md
- docs/Component/Recommended Directory Structure.md
- docs/14_day_upgrade_schedule.md

When there is any conflict:

1. system_scope_spec.md
2. architecture_spec.md
3. canonical_spec.md
4. metrics_spec.md
5. validation_spec.md
6. Recommended Directory Structure.md
7. 14_day_upgrade_schedule.md

## 2. Mandatory Architecture Discipline

Always keep layer order:

config -> engine -> canonical -> metrics -> validation -> optional export

Do not mix responsibilities:

- Engine must not depend on metrics or validation.
- Metrics must not include pass or fail logic.
- Validation must not modify upstream data.

## 3. Canonical Contract

CanonicalResult must follow run/wagers/summary structure and remain deterministic and neutral.

Required guarantees:

- replay-oriented metadata in run
- wager -> round -> roll state path completeness
- no control semantics
- no statistical interpretation fields in canonical

## 4. Metrics Contract

MetricsBundle must be descriptive only and include:

- meta
- core
- distribution
- tail
- optional

No thresholds, no verdicts, no correctness judgement in metrics.

## 5. Validation Contract

ValidationReport must be explicit and reproducible, with:

- meta
- checks
- summary

Checks must include observed data, expected/range/CI context, verdict, and notes.

## 6. Schedule-Oriented Execution

When implementing schedule tasks, prioritize the next unfinished coding blocks in docs/14_day_upgrade_schedule.md.

Current priority window:

- Day 6 Block A and Block B
- Day 7 Block A

## 7. Safety Boundaries

Never introduce any runtime outcome steering behavior, including:

- reroll logic
- protect logic
- range filtering to force outcomes
- adaptive odds based on player history

## 8. Change Strategy

Prefer small, testable, deterministic changes.
Preserve existing project structure unless user explicitly asks for a structural migration.
