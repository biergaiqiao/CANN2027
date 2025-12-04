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


def collect_npu_smi(destination: Union[Path, str]) -> Dict[str, Any]:
    """Collect basic NPU stats using `npu-smi info` when available.

    If the command is missing, we synthesize a minimal record so downstream
    analytics can still run in constrained environments.
    """
    destination = Path(destination)
    command = ["npu-smi", "info"]
    timestamp = datetime.utcnow().isoformat() + "Z"
    try:
        raw_output = subprocess.check_output(command, text=True)
        payload = {
            "collector": "npu-smi",
            "timestamp": timestamp,
            "metrics": parse_npu_smi_output(raw_output),
        }
    except (OSError, subprocess.CalledProcessError):
        payload = {
            "collector": "npu-smi",
            "timestamp": timestamp,
            "metrics": {"error": "npu-smi not available in this environment"},
        }
    destination.write_text(json.dumps(payload, indent=2))
    return payload
