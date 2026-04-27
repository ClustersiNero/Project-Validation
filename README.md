# Project Validation

This repository is a **Gate of Olympus-anchored, validation-first slot math prototype**.

It demonstrates:

- deterministic, config-driven simulation
- canonical audit recording
- descriptive metrics
- explicit validation
- trace and tuning visibility for math iteration

It is intentionally scoped to **one gameplay model**. It is not trying to be a generic multi-game slot framework.

## What the project is

The project treats slot math work as a pipeline:

```text
config -> engine -> canonical result -> metrics -> validation -> optional export
```

The core idea is:

1. generate outcomes deterministically
2. record them in a stable canonical shape
3. compute metrics from canonical data only
4. validate structural and statistical expectations explicitly

## Current gameplay scope

The current implementation is intentionally tied to a Gate of Olympus-style prototype with:

- `bet -> round -> roll` hierarchy
- cascade / refill flow
- scatter-triggered free games
- carried multipliers in free games
- mode-specific basic-strip behavior

The three implemented modes are:

- `mode_id = 1`: `normal`
- `mode_id = 2`: `buy_free`
- `mode_id = 3`: `chance_increase`

## What is implemented

### Core pipeline

- validated simulation config input
- deterministic engine execution
- canonical result recording
- metrics bundle computation
- canonical validation
- metrics sanity validation
- statistical validation with mode-scoped default rules

### Inspection and demo surface

- CLI entry point: `validation-demo`
- compact console summary
- JSON summary export
- Markdown trace export for `bet / round / roll` inspection
- tuning CSV export for `bet` and `round` level review
- progress reporting for simulation, post-processing, and trace writing

### Testing

The repository includes automated tests for:

- config validation
- RNG determinism
- engine flow and settlement behavior
- canonical contracts
- metrics computation
- statistical validation behavior
- pipeline reproducibility and smoke coverage

## Repository structure

```text
configs/
  game/                 game config and current Olympus-like prototype inputs
  validation/           default statistical validation targets

src/validation/
  config/               config normalization and validation
  engine/               deterministic simulation logic
  canonical/            canonical schema and recording
  metrics/              descriptive metrics from canonical data
  validation/           canonical / metrics / statistical validation
  export/               trace and tuning exports
  core/                 pipeline orchestration
  api/                  thin callable entry point
  cli.py                CLI runner

tests/                  unit and integration coverage
docs/General Provisions formal specs and architecture notes
docs/working_notes/     working notes and schedule artifacts
```

## Running the project

### Main demo command

```powershell
.\.venv\Scripts\validation-demo.exe `
  --config-module configs.game.olympus_mini `
  --seed 42 `
  --mode-id 1 `
  --bet-count 100000 `
  --with-default-rules `
  --progress `
  --output-json runs\demo_summary.json `
  --output-trace runs\demo_trace.md `
  --output-tuning-prefix runs\demo_tuning
```

This command will:

- run the full pipeline
- show progress for simulation, post-processing, and trace writing
- write:
  - `runs/demo_summary.json`
  - `runs/demo_trace.md`
  - `runs/demo_tuning_bets.csv`
  - `runs/demo_tuning_rounds.csv`

### Typical mode switches

- normal:
  - `--mode-id 1 --bet-count 100000`
- buy free:
  - `--mode-id 2 --bet-count 10000`
- chance increase:
  - `--mode-id 3 --bet-count 100000`

Outputs:

- `demo_summary.json`: top-level RTP, hit-rate, and validation summary
- `demo_trace.md`: detailed `bet / round / roll` execution trace
- `demo_tuning_bets.csv` / `demo_tuning_rounds.csv`: flat tables for tuning review

## Demo walkthrough

A minimal walkthrough for this repository is:

1. Run one mode through the full pipeline with `validation-demo`
2. Check `demo_summary.json` for top-level RTP, hit-rate, and validation status
3. Open `demo_trace.md` to inspect `bet / round / roll` behavior and board transitions
4. Open `demo_tuning_bets.csv` and `demo_tuning_rounds.csv` to review tuning-facing outcome shape
5. Compare the observed summary against `configs/validation/default_rules.py`

For a short external explanation, the repository demonstrates:

- how a deterministic slot math simulation is executed
- how outcomes are recorded in canonical form
- how metrics are derived from canonical data
- how structural and statistical checks are applied explicitly

## Specs and reference docs

Formal project specs live under `docs/General Provisions/`:

- `system_scope_spec.md`
- `architecture_spec.md`
- `config_spec.md`
- `engine_spec.md`
- `canonical_spec.md`
- `metrics_spec.md`
- `validation_spec.md`

Those files define the intended contracts in more detail than the README.

## Out of scope

This repository does **not** attempt to be:

- a production slot engine
- a regulatory certification tool
- a runtime balancing or adaptive control system
- a player behavior model
- a monetization or retention model
- a generic multi-game engine/plugin framework
- a high-performance C++ simulation core

It also does **not** include:

- reroll or outcome filtering logic
- runtime manipulation or steering
- player-dependent probability changes
- UI-heavy visualization tooling

Current prototype limitations:

- one gameplay implementation only
- tuned validation targets are maintained manually
- export formatting is functional, not product-polished
- the engine is optimized for clarity and inspectability, not maximum throughput

## Why this repo exists

This repository exists to make the following claim concrete:

> slot math work can be simulated, recorded, measured, and validated in a way that is deterministic, inspectable, and discussion-ready.

That is the main scope of the project.
