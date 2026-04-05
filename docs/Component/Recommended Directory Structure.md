project_validation/
├─ README.md
├─ pyproject.toml
├─ requirements.txt
├─ .gitignore
├─ .python-version
│
├─ docs/
│  ├─ system_scope_spec.md
│  ├─ architecture_spec.md
│  ├─ canonical_spec.md
│  ├─ metrics_spec.md
│  ├─ validation_spec.md
│  ├─ adr/
│  │  ├─ 001-canonical-as-single-source-of-truth.md
│  │  ├─ 002-no-runtime-control-semantics.md
│  │  └─ 003-metrics-validation-separation.md
│  └─ notes/
│     ├─ roadmap.md
│     ├─ naming_conventions.md
│     └─ backlog.md
│
├─ configs/
│  ├─ game/
│  │  ├─ olympus_base.yaml
│  │  ├─ olympus_feature.yaml
│  │  └─ olympus_variants/
│  │     ├─ v01.yaml
│  │     └─ v02.yaml
│  ├─ run/
│  │  ├─ smoke.yaml
│  │  ├─ benchmark.yaml
│  │  ├─ regression.yaml
│  │  └─ long_run.yaml
│  ├─ validation/
│  │  ├─ rtp_rules.yaml
│  │  ├─ distribution_rules.yaml
│  │  └─ regression_rules.yaml
│  └─ export/
│     ├─ json.yaml
│     ├─ csv.yaml
│     └─ report.yaml
│
├─ data/
│  ├─ baselines/
│  │  ├─ approved/
│  │  └─ snapshots/
│  ├─ fixtures/
│  │  ├─ canonical_samples/
│  │  └─ replay_cases/
│  └─ temp/
│
├─ outputs/
│  ├─ canonical/
│  ├─ metrics/
│  ├─ validation/
│  ├─ reports/
│  └─ logs/
│
├─ scripts/
│  ├─ run_pipeline.py
│  ├─ run_benchmark.py
│  ├─ run_regression.py
│  ├─ export_report.py
│  └─ replay_spin.py
│
├─ src/
│  └─ project_validation/
│     ├─ __init__.py
│     ├─ version.py
│     │
│     ├─ cli/
│     │  ├─ __init__.py
│     │  ├─ app.py
│     │  ├─ run.py
│     │  ├─ benchmark.py
│     │  ├─ regression.py
│     │  └─ replay.py
│     │
│     ├─ config/
│     │  ├─ __init__.py
│     │  ├─ loader.py
│     │  ├─ normalizer.py
│     │  ├─ resolver.py
│     │  └─ schema.py
│     │
│     ├─ domain/
│     │  ├─ __init__.py
│     │  ├─ enums.py
│     │  ├─ constants.py
│     │  ├─ ids.py
│     │  └─ rules.py
│     │
│     ├─ engine/
│     │  ├─ __init__.py
│     │  ├─ runner.py
│     │  ├─ rng/
│     │  │  ├─ __init__.py
│     │  │  ├─ interface.py
│     │  │  └─ seeded_rng.py
│     │  ├─ game/
│     │  │  ├─ __init__.py
│     │  │  ├─ state.py
│     │  │  ├─ state_transition.py
│     │  │  ├─ spin_executor.py
│     │  │  ├─ step_executor.py
│     │  │  ├─ payout_mapper.py
│     │  │  ├─ trigger_logic.py
│     │  │  ├─ feature_engine.py
│     │  │  └─ reel_selector.py
│     │  └─ builders/
│     │     ├─ __init__.py
│     │     └─ canonical_builder.py
│     │
│     ├─ canonical/
│     │  ├─ __init__.py
│     │  ├─ schema.py
│     │  ├─ models.py
│     │  ├─ serializer.py
│     │  ├─ replay.py
│     │  └─ checks.py
│     │
│     ├─ metrics/
│     │  ├─ __init__.py
│     │  ├─ pipeline.py
│     │  ├─ models.py
│     │  ├─ core.py
│     │  ├─ distribution.py
│     │  ├─ tail.py
│     │  ├─ streak.py
│     │  ├─ mode.py
│     │  └─ step_level.py
│     │
│     ├─ validation/
│     │  ├─ __init__.py
│     │  ├─ pipeline.py
│     │  ├─ models.py
│     │  ├─ structural/
│     │  │  ├─ __init__.py
│     │  │  ├─ canonical_integrity.py
│     │  │  ├─ mapping_consistency.py
│     │  │  └─ config_consistency.py
│     │  ├─ statistical/
│     │  │  ├─ __init__.py
│     │  │  ├─ ci.py
│     │  │  ├─ range_check.py
│     │  │  ├─ deviation_check.py
│     │  │  └─ sample_size.py
│     │  └─ regression/
│     │     ├─ __init__.py
│     │     ├─ baseline_loader.py
│     │     └─ drift_check.py
│     │
│     ├─ reporting/
│     │  ├─ __init__.py
│     │  ├─ models.py
│     │  ├─ json_exporter.py
│     │  ├─ csv_exporter.py
│     │  └─ markdown_report.py
│     │
│     ├─ pipeline/
│     │  ├─ __init__.py
│     │  ├─ artifact.py
│     │  ├─ run_context.py
│     │  └─ orchestrator.py
│     │
│     └─ shared/
│        ├─ __init__.py
│        ├─ paths.py
│        ├─ hashing.py
│        ├─ logging.py
│        ├─ timeutils.py
│        └─ exceptions.py
│
└─ tests/
   ├─ unit/
   │  ├─ config/
   │  ├─ engine/
   │  ├─ canonical/
   │  ├─ metrics/
   │  └─ validation/
   ├─ integration/
   │  ├─ test_run_pipeline.py
   │  ├─ test_replay_determinism.py
   │  ├─ test_metrics_from_canonical.py
   │  └─ test_validation_from_metrics.py
   └─ golden/
      ├─ canonical/
      ├─ metrics/
      └─ validation/