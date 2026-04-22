from validation.canonical.schema import CanonicalResult
from validation.metrics.metrics import compute_metrics_impl
from validation.metrics.types import MetricsBundle


def compute_metrics(result: CanonicalResult) -> MetricsBundle:
    return compute_metrics_impl(result)

