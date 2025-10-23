# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
@ai-module: viz.readmit.bars_hists
@ai-role: visualization.builder
@ai-intent: Summarize readmission distributions across categorical and numeric features.
@ai-created: 2024-05-08
@ai-owned-by: QAT
@ai-risk-data: medium

## Overview
- Provides categorical count and numeric histogram comparisons split by readmission outcome.
- Adds diagnosis × gender distribution panels (ridgeline + box plots) to surface class separation patterns.
- Shares palette utilities with other readmit visual builders for visual cohesion.

## Functions & Schemas
| Function | Inputs | Output Schema | Notes |
| --- | --- | --- | --- |
| `build_bars_and_hists(df, categoricals, numerics, readmit_col="Has_Readmission_30_Days", bins=12)` | DataFrame + feature lists | Tuple[`matplotlib.figure.Figure`, `pandas.DataFrame`] where the summary table columns = `feature`, `bin`, `readmission`, `count`, `rate`, `viz_type`. | Figure contains clustered + stacked bars for categoricals and overlaid + stacked histograms for numerics. Summary table feeds manifest CSV exports. |
| `build_diagnosis_distribution_panels(df, measure="Age", top_k_diag=6, readmit_col="Has_Readmission_30_Days", diagnosis_col="Primary_Diagnosis", gender_col="Gender", bandwidth=1.0)` | DataFrame with measure + demographic columns | Tuple[`Dict[str, matplotlib.figure.Figure]`, `pandas.DataFrame`] keyed by `ridgeline` and `box`. Summary columns = `[diagnosis_col, gender_col, "readmit", "count", "mean", "median", "q1", "q3"]`. | Designed to plug into `viz.report.book` manifest; gracefully returns empty dict/summary when prerequisites are missing. |

## Coordination Mechanics
- `build_bars_and_hists` is invoked once per report build; the orchestrator saves the single composite figure and summary CSV.
- `build_diagnosis_distribution_panels` is optional: triggered via configuration (`config["bars_hists"]["diagnosis_panels"]` or top-level `config["diagnosis_distribution_panels"]`). The orchestrator handles iteration over returned figures and persists each to disk.
- Both routines apply the shared theme to maintain typography and palettes.

## Integration Points
- Downstream consumer: `viz.report.book.build_readmission_report` orchestrates saves and manifest entries.
- Upstream: configuration delivered via `run_viz.py` / CLI toggles; expects cleaned columns from preprocessing notebooks.
- Shares colour palette with `viz.shared.theme`; uses `_ensure_boolean` helper consistent with other readmission modules.

## Dialogic Notes
- @ai-cadence: run — focus on deterministic rendering, no background threads.
- Future drift to monitor: KDE bandwidth heuristics vs. sparse diagnosis panels; capture overrides via config before adjusting defaults.
