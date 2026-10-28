# Implementation Plan: AST bedrock + AEC as an installable Spec Kit extension

**Branch**: `speckit/aec-extension` (spec dir `001-ast-bedrock-extension`) | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-ast-bedrock-extension/spec.md`

## Summary

Replace the 2025 call-only, pandas- and typer-dependent extractor with a stdlib edge extractor that emits
defines, calls, imports, inherits and references edges as deterministic JSON lines (`aec edges`).
Add a snapshot diff (`aec edges --diff`). Let records point at code (`code:<dotted>`) so `aec check`
reports dangling code references, and add `aec code-impact`, which turns a structural diff into change events for `aec impact`.
Package the commands as a Spec Kit extension (`extension.yml`, Markdown commands, optional
`after_specify`, `after_tasks` and `after_implement` hooks) that is installable with `specify extension add`. Prove
it on a fresh Spec Kit project and on Data-Guide.

## Technical Context

**Language/Version**: Python 3.10+ (stdlib `ast`, `tokenize`, `hashlib`, `json`)
**Primary Dependencies**: none at runtime. Spec Kit CLI v1.2.3, pinned, for extension packaging and tests.
**Storage**: files. `.aec/edges.jsonl` (snapshot), `.aec/records.jsonl` (records).
**Testing**: `unittest` (stdlib), with fixture packages under `tests/fixtures/`
**Target Platform**: any OS with Python 3.10+, local or in CI
**Project Type**: CLI and library, plus a Spec Kit extension package
**Performance Goals**: Data-Guide (32 files, ~3.2k lines) in < 2 s (SC-002). Linear in source size.
**Constraints**: deterministic, stably sorted output. Hooks report only. No third-party packages.
**Scale/Scope**: single repositories, up to ~100k lines. Python sources only.

## Constitution Check

*GATE: must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | How this plan complies | Status |
|---|---|---|
| I. Purpose lives in AEC records | The spec cites `AEC-P0@1`, `AEC-R1@1` and `AEC-R4@1`. Hooks return findings only. The extension edits no Spec Kit artifact. | ✅ |
| II. Stdlib, deterministic | Stdlib only. Edges are sorted by (kind, src, dst, file, line), and the snapshot header carries file hashes. | ✅ |
| III. Violations-first tests | Each check (dangling code reference, diff, impact) gets a violating fixture and a clean decoy, written before the code. | ✅ planned in tasks |
| IV. Structural ≠ purpose | CLI output and README label edge, check and impact results as structural. | ✅ |
| V. Earn it against the baseline | `docs/speckit-log.md` records Spec Kit's analyze and converge findings vs AEC's, plus authoring time. | ✅ |
| VI. Bedrock from code | The edge graph is computed from source on demand and is never written by hand. Records reference symbols; they don't copy them. | ✅ (this feature implements it) |

No violations, so Complexity Tracking stays empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-ast-bedrock-extension/
├── plan.md          # this file
├── research.md      # Phase 0
├── data-model.md    # Phase 1
├── quickstart.md    # Phase 1
├── contracts/       # Phase 1: CLI, edge format, extension manifest
└── tasks.md         # /speckit-tasks
```

### Source Code (repository root)

```text
src/aec/
├── __main__.py      # CLI: check | impact | edges | code-impact
├── records.py       # + code:<dotted> reference resolution against an edge snapshot
├── impact.py        # unchanged semantics; reused by code-impact
├── edges.py         # NEW: stdlib edge extractor + snapshot + diff
└── code_impact.py   # NEW: structural diff -> change events -> impact
extension/            # NEW: Spec Kit extension package (id: aec)
├── extension.yml
├── README.md
└── commands/
    ├── speckit.aec.purpose-link.md   # after_specify: does the spec cite a purpose?
    ├── speckit.aec.check.md          # after_tasks: aec check on records (+ code refs)
    └── speckit.aec.impact.md         # after_implement: edges --diff -> code-impact
tests/
├── test_aec.py
├── test_edges.py      # NEW
├── test_code_impact.py# NEW
├── test_extension.py  # NEW: manifest schema + install into a temp Spec Kit project (skips if specify absent)
└── fixtures/edges_pkg_v1/, edges_pkg_v2/   # NEW: hand-labelled packages
src/core/tools/ast_dependency_extractor.py  # kept; superseded (see research R4)
```

**Structure Decision**: single project. The extension lives in `extension/` in the same repo, so one
release carries both the package and its Spec Kit wrapper.

## Complexity Tracking

_None._
