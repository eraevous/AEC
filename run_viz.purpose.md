# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
@ai-module: run_viz
@ai-role: cli.entrypoint
@ai-intent: Provide a turnkey script for generating the readmission visualization suite.
@ai-created: 2024-05-08
@ai-owned-by: QAT
@ai-risk-data: medium  # reads PHI-like spreadsheets locally, outputs aggregates

## Overview
- Loads the configured Excel dataset, applies optional sampling, and delegates visualization work to `viz.report.book`.
- Establishes default configuration, including readmission palette, bin specs, and optional diagnosis distribution panels.
- Writes artifact manifest JSON to the chosen output directory.

## Interfaces
| Function | Inputs | Output Schema | Notes |
| --- | --- | --- | --- |
| `main`-style top-level script | Constants `DATA_LOC`, `OUT_DIR`, implicit CLI editing | Side effects only: saved figures/tables + manifest JSON; no return value. | Relies on user editing dataset path before execution; safe defaults keep sample sizes manageable. |

## Coordination Mechanics
- Applies shared theme before building the book; tolerates missing theme module.
- Delegates to `viz.report.book.build_book` (aliased import) to produce manifest; ensures output directories exist.
- Exposes configuration fields that downstream modules expect (bin specs, enable flags, diagnosis panels, etc.).

## Integration Points
- Upstream: local data sources (Excel workbook) prepared by analysts.
- Downstream: Figures/CSV manifest consumed by analysts for presentations.
- Shares palette + bin spec conventions with `viz.shared.theme` and `viz.shared.binning`.

## Dialogic Notes
- @ai-cadence: run — script is a launcher, not an analysis environment.
- Future enhancements: consider CLI parsing to avoid manual constant edits.
