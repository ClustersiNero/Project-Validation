from dataclasses import dataclass, field


@dataclass
class SimulationMetadata:
    simulation_id: str = ""
    config_id: str = ""
    config_version: str = ""
    engine_version: str = ""
    schema_version: str = ""
    mode: str = ""
    seed: int = 0
    bet_amount: float = 0.0
    bet_level: float = 0.0
    total_bets: int = 0
    timestamp: str = ""


@dataclass
class Cell:
    symbol_id: int
    multiplier_value: int | None = None


@dataclass
class RollRecord:
    roll_id: int = 0
    roll_win_amount: float = 0.0
    roll_type: str = ""
    strip_set_id: int = 0
    multiplier_profile_id: int = 0
    roll_filled_state: list[list[Cell]] = field(default_factory=list)
    roll_final_state: list[list[Cell | None]] = field(default_factory=list)
    roll_multi_symbols_num: int = 0
    roll_multi_symbols_carry: list[int] = field(default_factory=list)
    roll_scatter_symbols_num: int = 0


@dataclass
class RoundRecord:
    round_id: int = 0
    round_type: str = ""
    round_win_amount: float = 0.0
    base_symbol_win_amount: float = 0.0
    carried_multiplier: float = 0.0
    round_multiplier_increment: float = 0.0
    round_total_multiplier: float = 1.0
    round_scatter_increment: int = 0
    award_free_rounds: int = 0
    scatter_win_amount: float = 0.0
    roll_count: int = 0
    round_final_state: object | None = None
    rolls: list[RollRecord] = field(default_factory=list)


@dataclass
class BetRecord:
    bet_id: int = 0
    bet_win_amount: float = 0.0
    basic_win_amount: float = 0.0
    free_win_amount: float = 0.0
    round_count: int = 0
    bet_final_state: object | None = None
    rounds: list[RoundRecord] = field(default_factory=list)


@dataclass
class CanonicalResult:
    simulation_metadata: SimulationMetadata = field(default_factory=SimulationMetadata)
    bets: list[BetRecord] = field(default_factory=list)


@dataclass
class MetricsBundle:
    bet_count: int = 0
    round_count: int = 0
    roll_count: int = 0
    total_bet_win_amount: float = 0.0
    total_round_win_amount: float = 0.0
    total_roll_win_amount: float = 0.0


@dataclass
class ValidationReport:
    is_valid: bool = True
    issues: list[str] = field(default_factory=list)
    meta: "ValidationMeta | None" = None
    structural_checks: list["CheckResult"] = field(default_factory=list)
    statistical_checks: list["CheckResult"] = field(default_factory=list)
    regression_checks: list["CheckResult"] = field(default_factory=list)
    summary: "ValidationSummary | None" = None


@dataclass
class ValidationMeta:
    simulation_id: str = ""
    config_id: str = ""
    config_version: str = ""
    schema_version: str = ""
    engine_version: str = ""
    validation_version: str = "minimal_validation.v1"
    timestamp: str = ""


@dataclass
class CheckResult:
    metric_path: str = ""
    observed: float | None = None
    expected: float | None = None
    range: tuple[float, float] | None = None
    deviation: float | None = None
    verdict: str = "pass"
    notes: str = ""


@dataclass
class ValidationSummary:
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    structural_passed: int = 0
    structural_failed: int = 0
    statistical_passed: int = 0
    statistical_failed: int = 0
    regression_passed: int = 0
    regression_failed: int = 0
    overall_verdict: str = "pass"


@dataclass
class PipelineResult:
    canonical_result: CanonicalResult
    metrics_bundle: MetricsBundle
    canonical_validation: ValidationReport
    metrics_validation: ValidationReport
