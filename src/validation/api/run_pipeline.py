from validation.core.pipeline import run_pipeline
from validation.core.types import PipelineResult


def run(config) -> PipelineResult:
    return run_pipeline(config)
