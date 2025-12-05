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

