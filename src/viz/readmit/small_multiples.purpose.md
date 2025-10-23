# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
@ai-module: viz.readmit.small_multiples
@ai-role: visualization.builder
@ai-intent: Render diagnosis-level small multiples for readmission monitoring.
@ai-created: 2024-05-08
@ai-owned-by: QAT
@ai-risk-data: medium  # aggregates PHI-adjacent metrics but no raw identifiers

## Overview
- Builds multi-panel matplotlib figures that expose interactions between utilization, demographics, and readmission outcomes.
- Supports bubble grids, rate heatmaps, and UpSet-style summaries to replace noisy parallel-coordinate risk views.
- Helper functions remain module-private; only `build_small_multiples` is exported.

## Functions & Schemas
| Function | Inputs | Output Schema | Notes |
| --- | --- | --- | --- |
| `build_small_multiples(df, top_k_diag=9, bin_specs=None, readmit_col="Has_Readmission_30_Days", diagnosis_col="Primary_Diagnosis", gender_col="Gender")` | Pandas DataFrame with required columns, optional bin-spec mapping | Tuple[`Dict[str, matplotlib.figure.Figure]`, `Dict[str, pandas.DataFrame]`]; each DataFrame contains columns documenting grouping keys plus `count` and `rate`. Current figure keys: `bubble`, `heatmap`, `mosaic`, `age_distance_rate`, `comorbidity_prior_bubble`, `comorbidity_upset`. | Figures are consumed by `viz.report.book.build_readmission_report`; table outputs are persisted alongside figures. Optional Age×Distance and UpSet panels are skipped gracefully when prerequisite columns are absent. |

## Coordination Mechanics
- `build_small_multiples` is invoked during the report build loop; figures are saved via `viz.shared.theme.save_figure` and later closed by the orchestrator.
- Relies on shared `viz.shared.binning` presets for consistent quantile/edge binning and uses `viz.shared.theme.apply_base_theme` for styling.
- UpSet computation aggregates across the unfiltered frame; panel-level plots operate on the diagnosis-filtered subset to honour top-K cadence.

## Integration Points
- Downstream: `viz.report.book.build_readmission_report` (manages persistence and manifest wiring).
- Upstream: expects curated dataframe prepared by ingestion notebooks / `run_viz.py` entry script.
- Shares palette expectations with `viz.shared.theme` so the readmission colourway is consistent across modules.

## Dialogic Notes
- @ai-cadence: run — module is execution-oriented; drift captured via manifest tables.
- Expansion hooks: additional facets (e.g., payer mix) should reuse `_top_diagnoses` filtering to preserve ordering coherence.
