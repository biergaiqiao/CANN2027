# Patent/Whitepaper Draft: Cascading Fault Detection with Sub-Health Supervision

## Technical Field
Monitoring and automated recovery of Ascend NPU clusters under MindSpore 1.7.0 / CANN 5.1.0 deployments.

## Summary
We present a lightweight supervision layer that pairs a compact monitoring model with a primary model. Fault injection signals (layer, granularity, and system levels) are traced through a deterministic propagation graph to visualize how perturbations impact health metrics. The pipeline unifies `npu-smi` telemetry, MindSpore profiler deltas, and monitoring-model z-score outputs into CSV artifacts for auditability.

## Key Claims
1. **Chain-aware diagnosis**: A propagation graph connects injected faults to downstream monitoring nodes with tunable attenuation, enabling real-time visualization and backtracking of anomalies.
2. **Sub-health co-pilot**: A small monitoring model supervises primary outputs, emitting z-score anomaly flags that are correlated with device metrics to catch soft degradations before failures occur.
3. **Multi-level injection coverage**: Bit-flip, scaling, stuck-at, jitter, throttling, and packet-loss injections emulate common NPU pathologies and network stressors while remaining runtime-configurable.
4. **Telemetry fusion**: Collector outputs (Ascend `npu-smi`, MindSpore profiler summaries) are normalized into CSV, allowing dashboards to overlay hardware, runtime, and model-level health in a single timeline.

## Implementation Notes
- Propagation utilities (`fault_detection/fault_analysis/propagation.py`) render ASCII chain diagrams for reports and attach impacted metric values for reproducibility.
- CSV emission (`monitoring/analysis/analyze.py::export_metrics_csv`) standardizes time-indexed metrics for downstream BI or Grafana ingestion.
- Sample health CSV (`data/collected_data/health_metrics_sample.csv`) demonstrates expected schema for quick import.
- Additional injections across layer/granularity/system modules provide concrete hooks for experimentation in Ascend lab environments.

## Differentiation vs. Industry Baselines
- Goes beyond raw device telemetry by **linking injection events to monitoring-model outputs**, producing a causal chain rather than isolated counters.
- Targets **sub-health detection** with a lightweight supervisor, contrasting heavyweight offline analysis tools that lack real-time correlation.
- Ships **ready-to-export CSV artifacts** and ASCII graphs, reducing integration friction for reliability teams.

## Future Work
- Extend propagation graphs with probabilities learned from historical incidents.
- Add automatic remediation scripts tied to specific injection signatures.
- Provide UI widgets that render the ASCII chain as interactive SVGs.
