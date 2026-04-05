from pathlib import Path
import zipfile
import os

root = Path("slot_validation_project_skeleton")
if root.exists():
    import shutil
    shutil.rmtree(root)

# Directory and file structure
files = {
    "README.md": "# Slot Validation Project Skeleton\n",
    "pyproject.toml": "",
    ".gitignore": "runs/\n__pycache__/\n*.pyc\n",
    
    "configs/game/olympus_mini.py": "",
    "configs/sim/quick_test.py": "",
    "configs/validation/default_rules.py": "",
    
    "src/slot_validation/__init__.py": "",
    
    "src/slot_validation/api/__init__.py": "",
    "src/slot_validation/api/simulation.py": "",
    "src/slot_validation/api/metrics.py": "",
    "src/slot_validation/api/validation.py": "",
    "src/slot_validation/api/pipeline.py": "",
    
    "src/slot_validation/config/__init__.py": "",
    "src/slot_validation/config/game_config.py": "",
    "src/slot_validation/config/sim_config.py": "",
    "src/slot_validation/config/validation_rules.py": "",
    
    "src/slot_validation/engine/__init__.py": "",
    "src/slot_validation/engine/rng.py": "",
    "src/slot_validation/engine/board.py": "",
    "src/slot_validation/engine/symbols.py": "",
    "src/slot_validation/engine/paylines.py": "",
    "src/slot_validation/engine/payout.py": "",
    "src/slot_validation/engine/evaluator.py": "",
    "src/slot_validation/engine/state.py": "",
    "src/slot_validation/engine/runner.py": "",
    
    "src/slot_validation/canonical/__init__.py": "",
    "src/slot_validation/canonical/schema.py": "",
    "src/slot_validation/canonical/builders.py": "",
    "src/slot_validation/canonical/summary.py": "",
    
    "src/slot_validation/metrics/__init__.py": "",
    "src/slot_validation/metrics/schema.py": "",
    "src/slot_validation/metrics/core.py": "",
    "src/slot_validation/metrics/distribution.py": "",
    "src/slot_validation/metrics/tail.py": "",
    "src/slot_validation/metrics/bundle.py": "",
    
    "src/slot_validation/validation/__init__.py": "",
    "src/slot_validation/validation/schema.py": "",
    "src/slot_validation/validation/checks.py": "",
    "src/slot_validation/validation/ci.py": "",
    "src/slot_validation/validation/regression.py": "",
    "src/slot_validation/validation/report.py": "",
    
    "src/slot_validation/cli/__init__.py": "",
    "src/slot_validation/cli/main.py": "",
    
    "src/slot_validation/utils/__init__.py": "",
    "src/slot_validation/utils/ids.py": "",
    "src/slot_validation/utils/time.py": "",
    "src/slot_validation/utils/math_utils.py": "",
    
    "tests/test_rng.py": "",
    "tests/test_payout.py": "",
    "tests/test_engine_runner.py": "",
    "tests/test_canonical_builder.py": "",
    "tests/test_metrics_core.py": "",
    "tests/test_validation_checks.py": "",
    "tests/test_reproducibility.py": "",
    
    "runs/.gitkeep": "",
    
    "docs/architecture_v2.md": "",
    "docs/canonical_result.md": "",
    "docs/metrics_design.md": "",
    "docs/statistical_validation.md": "",
}

# Create files
for rel_path, content in files.items():
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

# Create zip
zip_path = Path("slot_validation_project_skeleton.zip")
if zip_path.exists():
    zip_path.unlink()

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in root.rglob("*"):
        zf.write(path, path.relative_to(root.parent))

print(f"Created project skeleton at: {root}")
print(f"Created zip at: {zip_path}")