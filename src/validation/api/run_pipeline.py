from collections.abc import Callable

from validation.core.pipeline import run_pipeline
from validation.core.types import PipelineResult, ValidationRules


def run(
    config,
    validation_rules: ValidationRules | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    post_progress_callback: Callable[[int, int, str], None] | None = None,
) -> PipelineResult:
    return run_pipeline(
        config,
        validation_rules,
        progress_callback=progress_callback,
        post_progress_callback=post_progress_callback,
    )
