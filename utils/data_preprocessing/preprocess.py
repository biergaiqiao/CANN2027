"""Data preprocessing helpers for monitoring and fault datasets."""
from typing import Iterable, List, Sequence


def normalize(values: Iterable[float]) -> List[float]:
    values = list(values)
    if not values:
        return []
    max_val = max(values)
    min_val = min(values)
    span = max_val - min_val or 1.0
    return [(value - min_val) / span for value in values]


def clamp(values: Iterable[float], lower: float, upper: float) -> List[float]:
    """Clamp values into the provided range."""
    return [max(lower, min(upper, value)) for value in values]


def sliding_window(values: Sequence[float], window: int) -> List[List[float]]:
    """Split a sequence into overlapping windows for feature extraction."""
    window = max(1, window)
    return [list(values[idx : idx + window]) for idx in range(0, len(values), window)]
