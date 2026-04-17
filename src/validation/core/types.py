from dataclasses import dataclass, field


@dataclass
class RollRecord:
    roll_id: int = 0
    roll_win_amount: float = 0.0


@dataclass
class RoundRecord:
    round_id: int = 0
    round_type: str = ""
    round_win_amount: float = 0.0
    roll_count: int = 0
    rolls: list[RollRecord] = field(default_factory=list)


@dataclass
class BetRecord:
    bet_id: int = 0
    bet_win_amount: float = 0.0
    round_count: int = 0
    rounds: list[RoundRecord] = field(default_factory=list)


@dataclass
class CanonicalResult:
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


@dataclass
class PipelineResult:
    canonical_result: CanonicalResult
    metrics_bundle: MetricsBundle
    canonical_validation: ValidationReport
    metrics_validation: ValidationReport
