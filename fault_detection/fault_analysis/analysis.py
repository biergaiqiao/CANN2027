"""Fault analysis helpers used by detection routines."""
import json
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Sequence


def load_metrics(path: Path) -> List[float]:
    data = json.loads(Path(path).read_text())
    if isinstance(data, list):
        return [float(item) for item in data]
    return [float(value) for value in data.get("metrics", [])]


def compute_rollup(metrics: Iterable[float]) -> Dict[str, float]:
    values = list(metrics)
    return {
        "average": mean(values) if values else 0.0,
        "max": max(values, default=0.0),
        "min": min(values, default=0.0),
    }


def rolling_average(metrics: Sequence[float], window: int = 5) -> List[float]:
    """Compute a simple rolling average for visualization or detection."""
    window = max(1, window)
    averages: List[float] = []
    for idx in range(len(metrics)):
        start = max(0, idx - window + 1)
        window_slice = metrics[start : idx + 1]
        averages.append(mean(window_slice))
    return averages
