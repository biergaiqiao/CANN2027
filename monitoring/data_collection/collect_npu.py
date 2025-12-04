
"""
Lightweight NPU monitoring inspired by Ascend msprof_analyze tooling.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import subprocess


def _parse_key_value_line(line: str) -> Tuple[str, Any]:
    if ":" not in line:
        return "", None
    key, raw_value = line.split(":", 1)
    key = key.strip().lower().replace(" ", "_")
    value = raw_value.strip()
    numeric_match = re.match(r"([-+]?\d+\.\d+|[-+]?\d+)", value)
    if numeric_match:
        try:
            value = float(numeric_match.group(1))
        except ValueError:
            pass
    return key, value


def parse_npu_smi_output(output: str) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {"raw": output}
    parsed: List[Tuple[str, Any]] = []
    for line in output.splitlines():
        key, value = _parse_key_value_line(line)
        if key:
            parsed.append((key, value))
    metrics["parsed"] = {key: value for key, value in parsed}
    return metrics


def _prune_numeric_metrics(metrics: Dict[str, Any]) -> Dict[str, float]:
    parsed = metrics.get("parsed", {}) if isinstance(metrics, dict) else {}
    numeric_entries = {}
    for key, value in parsed.items():
        if isinstance(value, (int, float)):
            numeric_entries[key] = float(value)
    return numeric_entries


def collect_npu_smi(destination: Union[Path, str], lightweight: bool = False) -> Dict[str, Any]:
    """Collect basic NPU stats using `npu-smi info` when available.

    If the command is missing, we synthesize a minimal record so downstream
    analytics can still run in constrained environments.

    Passing ``lightweight=True`` stores only numeric parsed metrics and omits
    the raw command output to keep artifacts small for frequent sampling.
    """
    destination = Path(destination)
    command = ["npu-smi", "info"]
    timestamp = datetime.utcnow().isoformat() + "Z"
    try:
        raw_output = subprocess.check_output(command, text=True)
        metrics = parse_npu_smi_output(raw_output)
        payload: Dict[str, Any] = {
            "collector": "npu-smi",
            "timestamp": timestamp,
            "metrics": metrics if not lightweight else _prune_numeric_metrics(metrics),
        }
    except (OSError, subprocess.CalledProcessError):
        payload = {
            "collector": "npu-smi",
            "timestamp": timestamp,
            "metrics": {"error": "npu-smi not available in this environment"},
        }
    destination.write_text(json.dumps(payload, indent=2))
    return payload


def collect_npu_smi_lightweight(destination: Union[Path, str]) -> Dict[str, Any]:
    """Shortcut for sampling with minimal footprint.

    This helper only writes numeric parsed metrics, which is useful when
    polling frequently or shipping artifacts over constrained links.
    """

    return collect_npu_smi(destination, lightweight=True)
=======

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Mapping, Sequence, Union

__all__ = [
    "load_metrics",
    "compute_rollup",
    "summarize_record",
    "export_metrics_csv",
]


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
    """Write metric sequences to a CSV file for visualization and sharing.

    The helper is intentionally light-weight so it can be imported directly
    inside notebooks or MindSpore 1.7.0 monitoring scripts. It also creates the
    parent directory for the destination file to avoid `FileNotFoundError`
    surprises when exporting health indicators during fault-injection runs.
    """

    if not metrics:
        raise ValueError("No metrics provided for CSV export")

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

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
