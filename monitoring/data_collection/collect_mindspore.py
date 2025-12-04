"""
MindSpore profiler data collection helper modeled after msprof_analyze utilities.
"""
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Union


def _walk_files(profile_dir: Path) -> Iterable[Path]:
    for path in profile_dir.rglob("*"):
        if path.is_file():
            yield path


def summarize_profiler(profile_dir: Union[Path, str]) -> Dict[str, Any]:
    """Summarize profiler artifacts by counting files and total size."""
    profile_path = Path(profile_dir)
    files = list(_walk_files(profile_path))
    total_size = sum(item.stat().st_size for item in files)
    by_suffix: Counter[str] = Counter(path.suffix for path in files)
    return {
        "files": len(files),
        "total_size_bytes": total_size,
        "by_suffix": dict(by_suffix),
    }


def collect_mindspore_profiler(
    source_dir: Union[Path, str], destination: Union[Path, str]
) -> Dict[str, Any]:
    """Package profiler summary into a JSON record for downstream ingestion."""
    summary = summarize_profiler(source_dir)
    destination = Path(destination)
    payload = {"collector": "mindspore-profiler", "summary": summary}
    destination.write_text(json.dumps(payload, indent=2))
    return payload


def collect_and_compare(
    baseline_dir: Union[Path, str],
    current_dir: Union[Path, str],
    destination: Union[Path, str],
) -> Dict[str, Any]:
    """Compare two profiler runs to highlight regressions."""
    baseline = summarize_profiler(baseline_dir)
    current = summarize_profiler(current_dir)
    delta_files = current.get("files", 0) - baseline.get("files", 0)
    delta_size = current.get("total_size_bytes", 0) - baseline.get("total_size_bytes", 0)
    comparison: Dict[str, Any] = {
        "baseline": baseline,
        "current": current,
        "delta_files": delta_files,
        "delta_bytes": delta_size,
    }
    Path(destination).write_text(json.dumps(comparison, indent=2))
    return comparison
