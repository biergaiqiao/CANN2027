# CANN2027

Reference project scaffold for NPU health detection inspired by Ascend `msprof_analyze` tooling.
Verified for environments aligned to `mindspore==1.7.0`, `CANN==5.1.0`, Python 3.7, and EulerOS 2.8.3.

The current revision focuses on **sub-health supervision** with a small monitoring model, richer fault propagation views, and CSV-friendly telemetry to simplify downstream reporting.

## Layout

```
/project_name
├── data/                  # raw, collected, and historical datasets
├── models/                # model definitions and lightweight placeholders
├── fault_detection/       # fault injection and analysis utilities
├── monitoring/            # data collection and anomaly analysis modules
├── utils/                 # preprocessing and model loading helpers
└── notebooks/             # space for exploratory notebooks
```

### Highlights

- `monitoring/data_collection/collect_npu.py` now parses `npu-smi info` key/value pairs into structured metrics, and `collect_mindspore.py` can compare two profiler dumps to surface regressions.
- `models/main_model` derives deterministic pseudo-weights from the shipped placeholder files so that inference paths are deterministic, while `models/monitoring_model` exposes z-score based anomaly flags when supervising the main model outputs.
- Fault injection utilities in `fault_detection/fault_injection` illustrate layer, granularity, and system level perturbations for testing and report which perturbations were applied. Additional injections now cover bit flips, multiplicative scaling, stuck-at faults, jitter, throttling, and packet loss to broaden coverage.
- Propagation helpers in `fault_detection/fault_analysis/propagation.py` render readable chains that map injected faults to downstream monitoring nodes and impacted metrics, enabling quick chain-of-custody visualizations for incident reviews.
- `monitoring/analysis/analyze.py::export_metrics_csv` emits time-indexed CSVs so health signals (e.g., utilization, temperature, z-score anomalies) can be consumed directly by dashboards. A sample is provided at `data/collected_data/health_metrics_sample.csv`.

## Getting Started
1. Install Python 3.7+ (the scaffold keeps type hints compatible with 3.7 for MindSpore 1.7/CANN 5.1.0).
2. Import utilities directly, for example:
    ```python

    from monitoring.data_collection.collect_npu import (
        collect_npu_smi,
        collect_npu_smi_lightweight,
    )

    # Full payload with raw command output preserved
    collect_npu_smi("data/collected_data/npu_stats.json")

    # Lightweight payload for frequent sampling (numeric fields only)
    collect_npu_smi_lightweight("data/collected_data/npu_stats_light.json")
    ```
3. Use the small monitoring model to supervise the main model during inference:
    from monitoring.data_collection.collect_npu import collect_npu_smi
    collect_npu_smi("data/collected_data/npu_stats.json")
    ```
3. Use the small monitoring model to supervise the main model during inference:

* `monitoring/data_collection/collect_npu.py` now parses `npu-smi info` key/value pairs into structured metrics, and `collect_mindspore.py` can compare two profiler dumps to surface regressions.
* `models/main_model` derives deterministic pseudo-weights from the shipped placeholder files so that inference paths are deterministic, while `models/monitoring_model` exposes z-score based anomaly flags when supervising the main model outputs.
* Fault injection utilities in `fault_detection/fault_injection` illustrate layer, granularity, and system level perturbations for testing and report which perturbations were applied. Additional injections now cover bit flips, multiplicative scaling, stuck-at faults, jitter, throttling, and packet loss to broaden coverage.
* Propagation helpers in `fault_detection/fault_analysis/propagation.py` render readable chains that map injected faults to downstream monitoring nodes and impacted metrics, enabling quick chain-of-custody visualizations for incident reviews.
* `monitoring/analysis/analyze.py::export_metrics_csv` emits time-indexed CSVs so health signals (e.g., utilization, temperature, z-score anomalies) can be consumed directly by dashboards. A sample is provided at `data/collected_data/health_metrics_sample.csv`.

## Getting Started

1. Install Python 3.7+ (the scaffold keeps type hints compatible with 3.7 for MindSpore 1.7/CANN 5.1.0).

2. Import utilities directly, for example:

   ```python
   from monitoring.data_collection.collect_npu import collect_npu_smi
   collect_npu_smi("data/collected_data/npu_stats.json")
   ```

3. Use the small monitoring model to supervise the main model during inference:

   ```python
   from models.main_model.model import MainModel
   from models.monitoring_model.model import MonitoringModel

   main = MainModel("models/main_model/model_weights.h5")
   main.load_weights()

   monitor = MonitoringModel(window_size=5)
   outputs = main.predict([1.0, 0.8, 0.6, 0.4, 0.2])
   health_scores = monitor.score_main_outputs(outputs)
   ```

4. Extend models and analysis modules with production logic as needed.

### Chain-aware fault propagation and visualization

4. Extend models and analysis modules with production logic as needed.

### Chain-aware fault propagation and visualization


4. Extend models and analysis modules with production logic as needed.

### Chain-aware fault propagation and visualization



Use the propagation helpers to map injected faults to observed monitoring nodes and metrics:

```python
from fault_detection.fault_analysis.propagation import (
    build_propagation,
    render_ascii_graph,
    summarize_propagation,
)

links = build_propagation(
    injections=["layer_7", "fpga_bridge"],
    monitored_nodes=["monitor_model", "npu_smi"],
)
summary = summarize_propagation(links, {"temperature": 72.5, "zscore": 2.8})
print(render_ascii_graph(summary.links))
print(summary.as_path())
```

Both `render_ascii_graph` and `as_path` yield quick chain diagrams that can be pasted into reports.

### Metric CSV export for dashboards

If you have time-series signals, convert them into a CSV for visualization:

```python
from monitoring.analysis.analyze import export_metrics_csv

metrics = {
    "npu_utilization": [62.5, 64.1, 70.2, 78.0],
    "temperature_c": [68.2, 68.5, 69.1, 70.4],
    "zscore_health": [0.3, 0.4, 0.6, 1.1],
}
export_metrics_csv(metrics, "data/collected_data/health_metrics_sample.csv")
```

The sample CSV shipped with the repo follows this schema so BI tools can ingest it immediately.

### NPU metrics captured from `npu-smi info`

`collect_npu_smi` stores the raw terminal output alongside a parsed map of every `key: value` line reported by `npu-smi info`. Typical fields you can expect include:

- Tool metadata such as `version`.
- Per-NPU device descriptors: `npu` index, `chip` id, `bus-id`/`device_id`, and `health` state.
- Live utilization and safety data: `aicore(%)`, `temperature(℃)`, and `power(w)`.
- Memory consumption: `hbm-usage` (MiB) and `memory-usage` (MiB) totals.
- Active process table entries when present (process id/name and memory per process).

<<<<<< codex/generate-project-code-from-data-collection-tools-1g8b1f
Any additional colon-delimited entries emitted by `npu-smi info` are also preserved in the parsed block, so downstream analytics can reason over them without modifying the collector.

When storage footprint matters (e.g., high-frequency polling), call `collect_npu_smi(destination, lightweight=True)` or the convenience helper `collect_npu_smi_lightweight` to store only numeric parsed metrics without the raw command output.

### 可视化与交互式探索
- **快速 matplotlib 折线图**：
  ```python
  from pathlib import Path
  from monitoring.analysis.visualize import (
      build_numeric_timeseries,
      load_npu_payloads,
      plot_metric_timeseries,
  )

  payloads = load_npu_payloads(Path("data/collected_data").glob("npu_stats*.json"))
  timestamps, series = build_numeric_timeseries(payloads)
  fig = plot_metric_timeseries(timestamps, series, "temperature(℃)")
  fig.savefig("data/collected_data/temperature.png", dpi=200)
  ```

- **Gradio 交互面板**（可选依赖，需要 `pip install gradio`）：
  ```python
  from pathlib import Path
  from monitoring.analysis.visualize import launch_npu_dashboard

  launch_npu_dashboard(Path("data/collected_data").glob("npu_stats*.json"))
  ```
  界面允许下拉选择任意指标（如利用率、温度、HBM 占用等）并查看时间序列折线图，便于对比亚健康趋势。

### Differentiation and innovation
- **Sub-health supervision**: A compact monitoring model supervises primary outputs with z-score anomaly flags, catching degradations before hard failures.
- **Chain-of-custody visualization**: Propagation graphs connect injections to monitoring nodes and metric excursions, bridging the gap between fault injection experiments and operational dashboards.
- **CSV-first telemetry**: Built-in CSV export plus a sample dataset reduce friction when integrating with industry-standard observability stacks compared to tools that only emit logs or proprietary formats.

### 无冲突更新小贴士
如果需要持续从 `main` 拉取更新而不想频繁处理冲突，可遵循 `docs/update_workflow.md` 的流程：保持工作区干净、优先使用 `git fetch` + `git rebase`，提交前用 `rg "<<<<<<<|>>>>>>>"` 自查是否遗留冲突标记，并用 `python -m compileall monitoring/analysis fault_detection utils` 快速做语法校验。
=======
`collect_npu_smi` stores the raw terminal output alongside a parsed map of every `key: value` line reported by `npu-smi info`. Typical fields you can expect include:

* Tool metadata such as `version`.
* Per-NPU device descriptors: `npu` index, `chip` id, `bus-id`/`device_id`, and `health` state.
* Live utilization and safety data: `aicore(%)`, `temperature(℃)`, and `power(w)`.
* Memory consumption: `hbm-usage` (MiB) and `memory-usage` (MiB) totals.
* Active process table entries when present (process id/name and memory per process).

