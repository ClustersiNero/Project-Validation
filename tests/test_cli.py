import json

from validation.cli import main


def test_cli_prints_summary_without_statistical_rules(capsys):
    exit_code = main(
        [
            "--config-module",
            "configs.game.olympus_mini",
            "--seed",
            "42",
            "--mode-id",
            "1",
            "--bet-count",
            "2",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Run Summary" in captured.out
    assert "Canonical Validation: PASS" in captured.out
    assert "Metrics Validation: PASS" in captured.out
    assert "Statistical Validation: SKIPPED" in captured.out


def test_cli_can_run_with_default_rules(capsys):
    exit_code = main(
        [
            "--config-module",
            "configs.game.olympus_mini",
            "--seed",
            "42",
            "--mode-id",
            "1",
            "--bet-count",
            "100",
            "--with-default-rules",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Statistical Validation:" in captured.out
    assert "Statistical Checks" in captured.out


def test_cli_can_write_json_summary(tmp_path, capsys):
    output_path = tmp_path / "demo_summary.json"

    exit_code = main(
        [
            "--config-module",
            "configs.game.olympus_mini",
            "--seed",
            "42",
            "--mode-id",
            "1",
            "--bet-count",
            "5",
            "--output-json",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    exported = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert "Run Summary" in captured.out
    assert exported["run"]["config_module"] == "configs.game.olympus_mini"
    assert exported["run"]["seed"] == 42
    assert exported["validation"]["canonical"] == "PASS"
    assert exported["validation"]["metrics"] == "PASS"
    assert exported["validation"]["statistical"] == "SKIPPED"
    assert "empirical_rtp" in exported["metrics"]
    assert exported["statistical"] is None


def test_cli_can_write_markdown_trace(tmp_path, capsys):
    output_path = tmp_path / "demo_trace.md"

    exit_code = main(
        [
            "--config-module",
            "configs.game.olympus_mini",
            "--seed",
            "42",
            "--mode-id",
            "1",
            "--bet-count",
            "2",
            "--output-trace",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    exported = output_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "Run Summary" in captured.out
    assert "# Run Trace" in exported
    assert "## Bet 0" in exported
    assert "### Round 0 (basic)" in exported
    assert "#### Roll 0 (initial)" in exported
    assert "Pre-Fill Board" in exported
    assert "Filled Board" in exported
    assert "Cleared Board" in exported
    assert "Gravity Board" in exported
    assert "#### Final Board" not in exported
    assert "fill_start_indices" in exported
    assert "fill_end_indices" in exported
    assert "| Row | C1 | C2 | C3 | C4 | C5 | C6 |" in exported
