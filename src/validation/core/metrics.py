from validation.core.types import CanonicalResult, MetricsBundle
from validation.metrics.minimal_metrics import compute_metrics_impl


def compute_metrics(result: CanonicalResult) -> MetricsBundle:
    return compute_metrics_impl(result)

