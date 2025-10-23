# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
@ai-module: viz.report.book
@ai-role: visualization.orchestrator
@ai-intent: Assemble the readmission analytics “book” and persist figures/tables.
@ai-created: 2024-05-08
@ai-owned-by: QAT
@ai-risk-data: low  # persists aggregated outputs only

## Overview
- Coordinates execution of readmission visualization builders and writes manifests + assets to disk.
- Handles enable/disable flags and config normalization for each visualization family.
- Produces a JSON manifest describing file paths for downstream delivery (slide decks, notebooks).

## Functions & Schemas
| Function | Inputs | Output Schema | Notes |
| --- | --- | --- | --- |
| `build_readmission_report(df, config)` | Pandas DataFrame plus configuration mapping | `Dict[str, Any]` manifest keyed by visualization family. Each entry contains saved figure paths, table CSV paths, or HTML exports plus `"manifest"` pointing at the JSON index. | Iterates across Sankey, corrgram, bars/hists, boxplots, parallel coords, small multiples, and optional diagnosis distributions; writes sidecar CSV/HTML assets and closes matplotlib figures. |

## Coordination Mechanics
- Applies `_maybe_enabled` guard for each viz block; respects nested `config["enable"]` toggles.
- Uses `viz.shared.theme.save_figure` for consistent file output and `plotly.io.write_html` for interactive charts.
- Normalizes `bars_hists` config to ensure booleans don’t break `.get()` access; the new diagnosis distribution panels read configuration from either `config["diagnosis_distribution_panels"]` or `config["bars_hists"]["diagnosis_panels"]`.
- Returns manifest and writes it to disk (`viz_manifest.json`) for downstream consumption.

## Integration Points
- Downstream consumers include `run_viz.py` CLI wrapper and any notebooks expecting the manifest contract.
- Upstream dependencies: visualization builders under `viz.readmit.*` and `viz.shared.theme` for saving assets.
- Manifest path is stored alongside figure/table directories; other agents can use it to locate generated media.

## Dialogic Notes
- @ai-cadence: run — orchestrator executes deterministically based on config.
- Future drift to monitor: manifest schema changes must be mirrored in documentation and `.purpose` updates.
