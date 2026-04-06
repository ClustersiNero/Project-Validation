from __future__ import annotations

from slot_validation.canonical.schema import CanonicalResult
from slot_validation.metrics.bundle import build_metrics_bundle
from slot_validation.metrics.schema import MetricsBundle


def compute_metrics(result: CanonicalResult) -> MetricsBundle:
	return build_metrics_bundle(result)
