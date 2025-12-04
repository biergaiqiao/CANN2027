"""Fault detection helpers built on top of computed metrics."""
from typing import Iterable, List, Sequence


def detect_spikes(metrics: Iterable[float], threshold: float = 0.2) -> List[int]:
    """Return indices where metrics exceed the provided threshold."""
    return [index for index, value in enumerate(metrics) if value > threshold]


def detect_drift(
    baseline: Sequence[float], current: Sequence[float], tolerance: float = 0.1
) -> List[int]:
    """Compare current metrics against a baseline and flag drifted positions."""
    limit = min(len(baseline), len(current))
    flagged: List[int] = []
    for idx in range(limit):
        if abs(current[idx] - baseline[idx]) > tolerance:
            flagged.append(idx)
    return flagged
