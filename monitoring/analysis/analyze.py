"""Basic analytics over collected monitoring data."""
import json
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Mapping, Sequence, Union

import csv


def load_metrics(path: Union[Path, str]) -> List[float]:
    data = json.loads(Path(path).read_text())
    if isinstance(data, list):
        return [float(item) for item in data]
    if "metrics" in data:
        return [float(value) for value in data.get("metrics", [])]
    if "summary" in data:
        return [float(value) for value in data["summary"].values()]
    return []


def compute_rollup(metrics: Iterable[float]) -> Dict[str, float]:
    values = list(metrics)
    return {
        "average": mean(values) if values else 0.0,
        "max": max(values, default=0.0),
        "min": min(values, default=0.0),
        "count": float(len(values)),
    }


def summarize_record(path: Union[Path, str]) -> Dict[str, float]:
    """Convenience wrapper for downstream dashboards."""
    metrics = load_metrics(path)
    return compute_rollup(metrics)


def export_metrics_csv(
    metrics: Mapping[str, Sequence[float]], destination: Union[Path, str]
) -> Path:
    """Write metric sequences to a CSV file for visualization and sharing."""

    destination = Path(destination)
    fieldnames = ["timestamp"] + list(metrics.keys())
    max_len = max((len(series) for series in metrics.values()), default=0)
    with destination.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for idx in range(max_len):
            row = {"timestamp": idx}
            for name, series in metrics.items():
                if idx < len(series):
                    row[name] = series[idx]
            writer.writerow(row)
    return destination
