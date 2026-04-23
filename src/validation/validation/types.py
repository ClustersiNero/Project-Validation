from dataclasses import dataclass, field


@dataclass
class ValidationReport:
    is_valid: bool = True
    issues: list[str] = field(default_factory=list)


@dataclass
class MetricRule:
    expected_value: float | None = None
    expected_range: tuple[float, float] | None = None
    z_value: float | None = None


@dataclass
class ValidationRules:
    metrics: dict[str, MetricRule] = field(default_factory=dict)
    metrics_by_mode: dict[str, dict[str, MetricRule]] = field(default_factory=dict)


@dataclass
class StatisticalCheckResult:
    metric_path: str
    check_type: str
    verdict: str
    observed: float | None = None
    expected_value: float | None = None
    expected_range: tuple[float, float] | None = None
    deviation: float | None = None
    notes: str = ""


@dataclass
class StatisticalValidationReport:
    is_valid: bool = True
    statistical_checks: list[StatisticalCheckResult] = field(default_factory=list)
