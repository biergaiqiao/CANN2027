"""Simple anomaly detection utilities for monitoring data."""
from statistics import mean, pstdev
from typing import Iterable, List


def zscore_anomalies(metrics: Iterable[float], z_threshold: float = 3.0) -> List[int]:
    values = list(metrics)
    if not values:
        return []
    mu = mean(values)
    sigma = pstdev(values) or 1.0
    return [idx for idx, value in enumerate(values) if abs(value - mu) / sigma > z_threshold]


def threshold_anomalies(metrics: Iterable[float], threshold: float) -> List[int]:
    return [idx for idx, value in enumerate(metrics) if value > threshold]
