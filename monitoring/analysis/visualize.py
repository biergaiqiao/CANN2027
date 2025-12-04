"""Visualization helpers for collected NPU metrics.

These utilities stay lightweight (matplotlib + optional Gradio) so they can run
inside MindSpore 1.7.0/CANN 5.1.0 environments without heavy dependencies.
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import matplotlib.pyplot as plt

__all__ = [
    "load_npu_payloads",
    "build_numeric_timeseries",
    "plot_metric_timeseries",
    "launch_npu_dashboard",
]


def load_npu_payloads(paths: Iterable[Path]) -> List[Dict[str, Any]]:
    """Load JSON payloads captured by ``collect_npu_smi``.

    Each entry should contain a ``timestamp`` and ``metrics`` block.
    """

    payloads: List[Dict[str, Any]] = []
    for path in paths:
        content = Path(path).read_text()
        try:
            payloads.append(json.loads(content))
        except json.JSONDecodeError:
            continue
    return payloads


def _numeric_from_metrics(metrics: Mapping[str, Any]) -> Dict[str, float]:
    parsed = metrics.get("parsed", metrics)
    numeric: Dict[str, float] = {}
    for key, value in parsed.items():
        if isinstance(value, (int, float)):
            numeric[key] = float(value)
    return numeric


def build_numeric_timeseries(
    payloads: Sequence[Mapping[str, Any]]
) -> Tuple[List[str], Dict[str, List[Optional[float]]]]:
    """Align numeric metrics across a sequence of payloads.

    Returns timestamps (string labels) and a dict of metric -> value list.
    Missing values are filled with ``None`` to keep series aligned.
    """

    timestamps: List[str] = []
    series: Dict[str, List[Optional[float]]] = {}

    for idx, payload in enumerate(payloads):
        timestamps.append(str(payload.get("timestamp", idx)))
        metrics = _numeric_from_metrics(payload.get("metrics", {}))

        for metric in metrics:
            if metric not in series:
                series[metric] = [None] * idx

        for metric_name in series:
            value = metrics.get(metric_name)
            series[metric_name].append(value)

    return timestamps, series


def plot_metric_timeseries(
    timestamps: Sequence[str],
    series: Mapping[str, Sequence[Optional[float]]],
    metric: str,
):
    """Render a matplotlib figure for a chosen metric time series."""

    values = series.get(metric, [])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(range(len(values)), values, marker="o", label=metric)
    ax.set_xticks(range(len(timestamps)))
    ax.set_xticklabels(timestamps, rotation=35, ha="right")
    ax.set_xlabel("sample")
    ax.set_ylabel(metric)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    return fig


def launch_npu_dashboard(
    payload_paths: Sequence[Path], default_metric: Optional[str] = None
):
    """Spin up a small Gradio UI to explore collected NPU metrics.

    Example:
        >>> from monitoring.analysis.visualize import launch_npu_dashboard
        >>> launch_npu_dashboard(Path("data/collected_data").glob("npu*.json"))
    """

    try:
        import gradio as gr  # type: ignore
    except ImportError as exc:  # pragma: no cover - runtime availability guard
        raise ImportError(
            "Gradio is not installed. Please `pip install gradio` to use the dashboard."
        ) from exc

    payloads = load_npu_payloads(payload_paths)
    timestamps, series = build_numeric_timeseries(payloads)
    metrics = sorted(series.keys())

    if not metrics:
        raise ValueError("No numeric metrics available to visualize.")

    default_metric = default_metric or metrics[0]

    def _plot(selected_metric: str):
        return plot_metric_timeseries(timestamps, series, selected_metric)

    with gr.Blocks() as demo:
        gr.Markdown("## NPU health metrics explorer")
        dropdown = gr.Dropdown(metrics, value=default_metric, label="Metric")
        plot = gr.Plot(value=_plot(default_metric))
        dropdown.change(_plot, inputs=dropdown, outputs=plot)

    demo.launch()
    return demo
