# Copilot Working Charter For This Repository

This file defines persistent implementation rules for Copilot in this repository.

## 1. Authoritative Documents

Always treat the following files as the primary source of truth:

- docs/General Provisions/system_scope_spec.md
- docs/General Provisions/architecture_spec.md
- docs/General Provisions/canonical_spec.md
- docs/General Provisions/metrics_spec.md
- docs/General Provisions/validation_spec.md
- docs/General Provisions/artifact_metadata_spec.md
- docs/Component/Recommended Directory Structure.md
- docs/14_day_upgrade_schedule.md

When there is any conflict:

1. system_scope_spec.md
2. architecture_spec.md
3. canonical_spec.md
4. metrics_spec.md
5. validation_spec.md
6. artifact_metadata_spec.md
7. Recommended Directory Structure.md
8. 14_day_upgrade_schedule.md

## 2. Mandatory Architecture Discipline

Always keep layer order:

config -> engine -> canonical -> metrics -> validation -> optional export

Do not mix responsibilities:

- Engine must not depend on metrics or validation.
- Metrics must be descriptive only.
- Validation must not modify upstream data.

## 3. Canonical / Metrics / Validation Contracts

CanonicalResult must remain deterministic, neutral, and replayable.

Required canonical guarantees:

- run / wagers / summary structure
- wager -> round -> roll state path completeness
- no control semantics
- no statistical interpretation fields

MetricsBundle must include:

- meta
- core
- distribution
- tail
- optional

Metrics must not contain thresholds, verdicts, or correctness judgement.

ValidationReport must include:

- meta
- checks
- summary

Validation checks must be explicit, reproducible, and explainable.

## 4. Safety Boundaries

Never introduce runtime outcome steering behavior, including:

- reroll
- protect
- range filtering
- waterline / pool / control-level semantics
- player-history-based adjustment
- adaptive probability logic
- any runtime outcome shaping

## 5. Change Strategy

Prefer small, testable, deterministic changes.

Do not rebuild from scratch when the current repository already has a compatible structure.

Prefer:

- reading existing code first
- reusing current dataclasses, interfaces, and naming
- making minimal compatible changes
- preserving current layer boundaries

## 6. Legacy Reference Code Rules

A `legacy_reference/` directory may exist in this repository.

It is reference material only.

Use it to:

- understand real round / feature / cascade behavior
- identify payout timing, trigger timing, and state transitions
- recover valid predefined game logic

Do not treat it as:

- source of truth
- production-ready code
- code to copy directly
- naming authority

When using legacy code:

- reference, do not copy
- retain valid predefined game logic only
- actively identify and delete unsafe control logic
- rewrite retained logic into the current architecture

If legacy code mixes valid logic with unsafe logic:

- split them conceptually first
- keep only the valid predefined generation logic
- discard the control layer entirely

## 7. Naming Migration Rule

Migrate semantics, not naming.

Legacy naming may differ from current repository terminology.
For example:

- legacy `stake` may correspond to current `wager`
- legacy hierarchy names may not match current `wager -> round -> roll`

Therefore:

- do not preserve legacy names by default
- first identify actual meaning
- then map it into current repository terminology
- keep naming aligned with current files, not legacy files

Priority for naming decisions:

1. current repository schema and dataclass fields
2. current layer responsibility
3. actual semantic meaning
4. legacy naming only as historical reference

## 8. Current Priority

Current priority is not adding more scaffolding.

Current priority is:

- first make engine round / feature / cascade behavior real
- then let canonical naturally carry real wager -> round -> roll paths
- then strengthen metrics and validation on top of real execution behavior

## 9. Engine Responsibility Boundary

For current implementation work, keep this split:

- `engine/evaluator.py` = flow orchestration
- `engine/board.py` = clear / refill / cascade / state progression
- `engine/payout.py` = evaluation and settlement
- `engine/runner.py` = top-level wager / run aggregation only

## 10. Required Working Method

Before writing migration code:

1. read current repository files first
2. read corresponding files under `legacy_reference/`
3. identify:
   - valid logic to retain
   - unsafe logic to delete
   - naming mismatches to remap
4. state which current files will be modified
5. only then write code

Do not directly paste legacy code into current files.
Do not preserve unsafe logic.
Do not preserve legacy naming when it conflicts with current terminology.