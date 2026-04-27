import argparse
import importlib
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from validation.api.run_pipeline import run
from validation.core.types import PipelineResult, ValidationRules
from validation.export.trace_export import export_trace_markdown
from validation.export.tuning_export import export_tuning_csvs
from validation.metrics.types import StatisticalMetric


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validation-demo",
        description="Run one validation pipeline demo and print a compact summary.",
    )
    parser.add_argument(
        "--config-module",
        default="configs.game.olympus_mini",
        help="Python module path that defines the five game config blocks.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Deterministic seed.")
    parser.add_argument("--mode-id", type=int, default=1, help="Simulation mode id.")
    parser.add_argument("--bet-count", type=int, default=100, help="Number of bets to run.")
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show a simple progress bar while simulating bets.",
    )
    parser.add_argument(
        "--with-default-rules",
        action="store_true",
        help="Run statistical validation with configs.validation.default_rules.DEFAULT_VALIDATION_RULES.",
    )
    parser.add_argument(
        "--output-json",
        help="Optional path for writing a compact JSON summary export.",
    )
    parser.add_argument(
        "--output-trace",
        help="Optional path for writing a human-readable Markdown trace export.",
    )
    parser.add_argument(
        "--output-tuning-prefix",
        help="Optional output prefix for writing tuning CSV exports: <prefix>_bets.csv and <prefix>_rounds.csv.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _ensure_cwd_on_sys_path()
    config_module = importlib.import_module(args.config_module)
    validation_rules: ValidationRules | None = (
        _load_default_validation_rules() if args.with_default_rules else None
    )
    reporter = ProgressReporter() if args.progress else None
    result = run(
        {
            "seed": args.seed,
            "mode_id": args.mode_id,
            "bet_count": args.bet_count,
            "simulation_mode": config_module.SIMULATION_MODE,
            "paytable": config_module.PAYTABLE,
            "multiplier_data": config_module.MULTIPLIER_DATA,
            "strip_sets": config_module.STRIP_SETS,
            "implementation_config": config_module.IMPLEMENTATION_CONFIG,
        },
        validation_rules=validation_rules,
        progress_callback=reporter.build_counter_callback("Simulating") if reporter else None,
        post_progress_callback=reporter.post_processing_callback if reporter else None,
    )
    if args.output_trace:
        export_trace_markdown(
            result.canonical_result,
            config_module.PAYTABLE,
            args.output_trace,
            config_module_path=args.config_module,
            progress_callback=reporter.build_counter_callback("Writing trace") if reporter else None,
        )
    if args.output_tuning_prefix:
        export_tuning_csvs(
            result.canonical_result,
            args.output_tuning_prefix,
            config_module_path=args.config_module,
        )
    if reporter is not None:
        reporter.finish()
    summary = _build_summary_data(result, args.config_module)
    if args.output_json:
        _write_summary_json(summary, args.output_json)
    print(_format_summary(summary))
    return 0


def _format_summary(summary: dict) -> str:
    run_summary = summary["run"]
    validations = summary["validation"]
    metrics = summary["metrics"]
    lines = [
        "Run Summary",
        f"Config Module: {run_summary['config_module']}",
        f"Config Id: {run_summary['config_id']}",
        f"Mode: {run_summary['mode']}",
        f"Seed: {run_summary['seed']}",
        f"Bets: {run_summary['total_bets']}",
        f"Canonical Validation: {validations['canonical']}",
        f"Metrics Validation: {validations['metrics']}",
        f"Statistical Validation: {validations['statistical']}",
        "",
        "Key Metrics",
        f"- empirical_rtp: {_format_metric_summary(metrics['empirical_rtp'])}",
        f"- basic_rtp: {_format_metric_summary(metrics['basic_rtp'])}",
        f"- free_rtp: {_format_metric_summary(metrics['free_rtp'])}",
        f"- bet_hit_frequency: {_format_metric_summary(metrics['bet_hit_frequency'])}",
        f"- free_trigger_frequency: {_format_metric_summary(metrics['free_trigger_frequency'])}",
        f"- round_hit_frequency: {_format_metric_summary(metrics['round_hit_frequency'])}",
        f"- roll_hit_frequency: {_format_metric_summary(metrics['roll_hit_frequency'])}",
        f"- initial_roll_share: {_format_metric_summary(metrics['initial_roll_share'])}",
        f"- cascade_roll_share: {_format_metric_summary(metrics['cascade_roll_share'])}",
    ]
    statistical = summary["statistical"]
    if statistical is not None:
        lines.extend(["", "Statistical Checks"])
        lines.append(
            f"- pass={statistical['passed_checks']}, fail={statistical['failed_checks']}"
        )
        if statistical["checks"]:
            for check in statistical["checks"][:5]:
                expected = (
                    f"range={check['expected_range']}"
                    if check["expected_range"] is not None
                    else f"expected={_format_number(check['expected_value'])}"
                )
                observed = _format_number(check["observed"])
                lines.append(
                    f"- {check['check_type']} {check['metric_path']}: {check['verdict'].upper()} "
                    f"(observed={observed}, {expected})"
                )
        else:
            lines.append("- no checks generated")
    return "\n".join(lines)


def _build_summary_data(result: PipelineResult, config_module_path: str) -> dict:
    metadata = result.canonical_result.simulation_metadata
    statistical = result.statistical_validation
    passed_checks = (
        sum(1 for check in statistical.statistical_checks if check.verdict == "pass")
        if statistical is not None
        else 0
    )
    return {
        "run": {
            "config_module": config_module_path,
            "config_id": metadata.config_id,
            "mode": metadata.mode,
            "seed": metadata.seed,
            "total_bets": metadata.total_bets,
        },
        "validation": {
            "canonical": _validation_status(result.canonical_validation),
            "metrics": _validation_status(result.metrics_validation),
            "statistical": _statistical_status(result.statistical_validation),
        },
        "metrics": {
            "empirical_rtp": _metric_to_dict(result.metrics_bundle.bet_metrics.core.empirical_rtp),
            "basic_rtp": _metric_to_dict(result.metrics_bundle.bet_metrics.core.basic_rtp),
            "free_rtp": _metric_to_dict(result.metrics_bundle.bet_metrics.core.free_rtp),
            "bet_hit_frequency": _metric_to_dict(result.metrics_bundle.bet_metrics.core.bet_hit_frequency),
            "free_trigger_frequency": _metric_to_dict(
                result.metrics_bundle.bet_metrics.core.free_containing_bet_frequency
            ),
            "round_hit_frequency": _metric_to_dict(result.metrics_bundle.round_metrics.core.round_hit_frequency),
            "roll_hit_frequency": _metric_to_dict(result.metrics_bundle.roll_metrics.core.roll_hit_frequency),
            "initial_roll_share": _metric_to_dict(
                result.metrics_bundle.roll_metrics.core.roll_type_distribution.initial
            ),
            "cascade_roll_share": _metric_to_dict(
                result.metrics_bundle.roll_metrics.core.roll_type_distribution.cascade
            ),
        },
        "statistical": (
            {
                "passed_checks": passed_checks,
                "failed_checks": len(statistical.statistical_checks) - passed_checks,
                "checks": [
                    {
                        "metric_path": check.metric_path,
                        "check_type": check.check_type,
                        "verdict": check.verdict,
                        "observed": check.observed,
                        "expected_value": check.expected_value,
                        "expected_range": list(check.expected_range)
                        if check.expected_range is not None
                        else None,
                        "deviation": check.deviation,
                        "notes": check.notes,
                    }
                    for check in statistical.statistical_checks
                ],
            }
            if statistical is not None
            else None
        ),
    }


def _validation_status(report) -> str:
    if report.is_valid:
        return "PASS"
    return f"FAIL ({len(report.issues)} issues)"


def _statistical_status(report) -> str:
    if report is None:
        return "SKIPPED"
    if report.is_valid:
        return f"PASS ({len(report.statistical_checks)} checks)"
    return f"FAIL ({len(report.statistical_checks)} checks)"


def _format_metric_summary(metric: dict) -> str:
    observed = _format_number(metric["observed"])
    return f"{observed} (n={metric['sample_size']})"


def _format_number(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{value:.6f}"


def _ensure_cwd_on_sys_path() -> None:
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)


def _load_default_validation_rules() -> ValidationRules:
    rules_module = importlib.import_module("configs.validation.default_rules")
    return rules_module.DEFAULT_VALIDATION_RULES


def _metric_to_dict(metric: StatisticalMetric) -> dict:
    return {
        "observed": metric.observed,
        "standard_deviation": metric.standard_deviation,
        "sample_size": metric.sample_size,
    }


def _write_summary_json(summary: dict, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


@dataclass
class ProgressReporter:
    bar_width: int = 30
    min_interval_seconds: float = 0.1
    _last_signature: tuple[str, int, int, str | None] | None = None
    _last_update: float = 0.0
    _rendered: bool = False

    def build_counter_callback(self, label: str):
        def callback(completed: int, total: int) -> None:
            self.render(label, completed, total)

        return callback

    def post_processing_callback(self, completed: int, total: int, detail: str) -> None:
        self.render("Post-processing", completed, total, detail)

    def render(
        self,
        label: str,
        completed: int,
        total: int,
        detail: str | None = None,
    ) -> None:
        now = time.monotonic()
        signature = (label, completed, total, detail)
        if (
            completed < total
            and signature == self._last_signature
            and now - self._last_update < self.min_interval_seconds
        ):
            return
        percent = 100 if total <= 0 else int((completed / total) * 100)
        filled = 0 if total <= 0 else int((completed / total) * self.bar_width)
        bar = "#" * filled + "-" * (self.bar_width - filled)
        suffix = f" {detail}" if detail else ""
        print(
            f"\r{label} [{bar}] {completed}/{total} ({percent}%){suffix}",
            end="",
            flush=True,
        )
        self._last_signature = signature
        self._last_update = now
        self._rendered = True

    def finish(self) -> None:
        if self._rendered:
            print()
