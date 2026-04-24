import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Sequence

from validation.api.run_pipeline import run
from validation.core.types import PipelineResult, ValidationRules
from validation.export.trace_export import export_trace_markdown
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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _ensure_cwd_on_sys_path()
    config_module = importlib.import_module(args.config_module)
    validation_rules: ValidationRules | None = (
        _load_default_validation_rules() if args.with_default_rules else None
    )
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
    )
    if args.output_trace:
        export_trace_markdown(
            result.canonical_result,
            config_module.PAYTABLE,
            args.output_trace,
            config_module_path=args.config_module,
        )
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


def _format_metric(metric: StatisticalMetric) -> str:
    observed = _format_number(metric.observed)
    return f"{observed} (n={metric.sample_size})"


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
