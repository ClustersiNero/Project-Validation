from __future__ import annotations

from slot_validation.canonical.schema import CanonicalResult
from slot_validation.metrics.core import compute_metrics_from_canonical
from slot_validation.metrics.schema import MetricsBundle


def build_metrics_bundle(result: CanonicalResult) -> MetricsBundle:
	return compute_metrics_from_canonical(result)
