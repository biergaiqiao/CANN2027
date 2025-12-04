"""
Monitoring model responsible for anomaly detection and system health scoring.
"""
from collections import deque
from statistics import mean, pstdev
from typing import Deque, Iterable, List, Sequence


class MonitoringModel:
    """Simple moving-average based monitor."""

    def __init__(self, window_size: int = 5, anomaly_z: float = 3.0) -> None:
        self.window_size = window_size
        self.anomaly_z = anomaly_z
        self.window: Deque[float] = deque(maxlen=window_size)

    def update(self, metric: float) -> float:
        """Update the rolling window and return an anomaly score."""
        self.window.append(metric)
        if len(self.window) < self.window.maxlen:
            return 0.0
        mu = mean(self.window)
        sigma = pstdev(self.window) or 1.0
        return abs(metric - mu) / sigma

    def bulk_score(self, metrics: Iterable[float]) -> List[float]:
        """Score a series of metrics for batch processing."""
        scores: List[float] = []
        for metric in metrics:
            scores.append(self.update(metric))
        return scores

    def score_main_outputs(self, outputs: Sequence[float]) -> List[float]:
        """Convenience wrapper when using the monitor alongside the main model.

        The monitor treats model outputs (or latency metrics) as the stream of
        values to watch for sub-health drifts.
        """
        return self.bulk_score(outputs)

    def flag_anomalies(self, outputs: Sequence[float]) -> List[int]:
        """Return indices that exceed the configured z-score threshold."""
        scores = self.bulk_score(outputs)
        return [idx for idx, score in enumerate(scores) if score > self.anomaly_z]
