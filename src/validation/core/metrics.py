from validation.canonical.schema import CanonicalResult
from validation.metrics.metrics import MetricsBundle, compute_metrics_impl


def compute_metrics(result: CanonicalResult) -> MetricsBundle:
    return compute_metrics_impl(result)

