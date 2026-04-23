from validation.core.pipeline import run_pipeline
from validation.core.types import PipelineResult, ValidationRules


def run(config, validation_rules: ValidationRules | None = None) -> PipelineResult:
    return run_pipeline(config, validation_rules)
