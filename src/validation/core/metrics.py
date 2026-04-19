from validation.canonical.minimal_canonical import CanonicalResult
from validation.metrics.minimal_metrics import MetricsBundle, compute_metrics_impl


def compute_metrics(result: CanonicalResult) -> MetricsBundle:
    return compute_metrics_impl(result)

