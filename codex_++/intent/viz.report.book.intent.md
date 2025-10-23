@ai-path: viz.report.book
@ai-role: visualization.orchestrator
@ai-cadence: run
@ai-created: 2024-05-07

- Fallback to global `config["bin_specs"]` when module-specific overrides are absent so small-multiple mosaics honor user-provided edges.
- Normalize `small_multiples` config to a mapping before reading overrides to avoid bool/None drift.
