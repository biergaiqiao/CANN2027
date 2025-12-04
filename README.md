# CANN2027

Reference project scaffold for NPU health detection inspired by Ascend `msprof_analyze` tooling.
Verified for environments aligned to `mindspore==1.7.0`, `CANN==5.1.0`, Python 3.7, and EulerOS 2.8.3.

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
- Fault injection utilities in `fault_detection/fault_injection` illustrate layer, granularity, and system level perturbations for testing and report which perturbations were applied.

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
