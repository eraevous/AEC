# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
@ai-module: viz.readmit.sankey
@ai-role: visualization.builder
@ai-intent: Render a Plotly Sankey chart summarizing the patient journey toward readmission.
@ai-created: 2024-05-09
@ai-owned-by: QAT
@ai-risk-data: medium

## Overview
- Aggregates encounter-level data across staged touchpoints (prior admissions, facility distance, diagnosis, length of stay, discharge, readmission).
- Applies readmission-aware colour blending so upstream nodes encode downstream readmit propensity.
- Emits tabular node/link breakdowns to accompany the interactive figure for manifest export.

## Functions & Schemas
| Function | Inputs | Output Schema | Notes |
| --- | --- | --- | --- |
| `build_sankey(df, top_k=10, min_count=25, palette=None, readmit_col="Has_Readmission_30_Days")` | Pandas DataFrame plus optional styling config | Tuple[`plotly.graph_objects.Figure`, `Dict[str, str]`, `Dict[str, pandas.DataFrame]`]. Figure is the Sankey visualization, the middle dict is reserved for future asset paths (currently empty), and the data dict contains two frames: `nodes` (`id`, `label`, `stage`, `color`, `readmit_rate`) and `links` (`source`, `target`, `value`, `color`, `readmit_flag`). | Normalizes booleans, distance miles, and length-of-stay days into labeled bins; compresses long-tail categorical levels; ensures palette defaults stay in sync with `viz.shared.theme`. |

## Coordination Mechanics
- Invoked by `viz.report.book.build_readmission_report`; orchestrator stores the figure HTML/PNG and the returned dataframes in the manifest payload.
- Shares the global readmission palette (`viz.shared.theme`) so downstream assets preserve consistent semantic colours.
- Stage ordering now includes facility distance and length-of-stay gates, aligning with analyst requests; upstream config can still adjust `top_k` and `min_count` for category compression.

## Integration Points
- Upstream expectation: cleaned columns `Prior_Admission`, `Distance_to_Closest_Hospital`, `Primary_Diagnosis`, `Length_of_Stay`, `Discharge_Status`, and `Has_Readmission_30_Days` supplied by data prep notebooks.
- Downstream consumers: manifest assembly in `viz.report.book`, plus analysts exploring Plotly exports.
- Relies on shared theme module; no external services invoked beyond Plotly figure instantiation.

## Dialogic Notes
- @ai-cadence: run — deterministic summarisation for reporting pipelines.
- Monitor drift if encounter schema renames distance/LOS fields; capture via `.intent.md` before updating required column guards.
