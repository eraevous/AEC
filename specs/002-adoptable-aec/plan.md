# Implementation Plan: AEC adoptable on a real repository

**Branch**: `speckit/002-adoptable` | **Spec**: [spec.md](spec.md) | **Date**: 2026-10-27

## Summary
Add `aec init` and `aec import-purpose`, two small additions to the record vocabulary (evidence kind / claim category and the `observed_on` relation) with one new check and one new impact rule, and state the code-vs-justification invariant. Stdlib only; everything is plain JSONL appended to `.aec/records.jsonl`.

## Technical Context
Python 3.10+ stdlib (Constitution II). Reuses `aec.edges` (snapshot, module/file map), `aec.records` (Store, check), `aec.impact`. Tests: unittest, fixtures under `tests/fixtures/`. Target repo for SC-001/SC-003: `/home/claude/data-guide` (25 purpose files).

## Constitution Check
- I: imported records are provisional claims plus `source` records; no new authority; spec cites `AEC-R4@1`, `AEC-R2@1`. ✅
- II: stdlib, deterministic ordering, append-only. ✅
- III: each check/rule gets a violating fixture and a decoy (tasks mark them). ✅
- IV: the outcome check is a warning about an *unsupported inference*; import output says "declared by the file", never "true". ✅
- V: authoring cost and what analyze/converge catch are logged in `docs/speckit-log.md`. ✅
- VI: code links resolve against the edge snapshot only. ✅

## Design decisions
- **D1 Import shape.** Per purpose file: a `source` record `PF-<slug>` (path, sha256, the file's own `@ai-generated`/`@ai-verified`, `origin: codex++`) and a `claim` record `PC-<slug>` (tier `candidate`, `epistemic: provisional`, `claim_category: requirement_satisfaction` is NOT set: it is a *declared intent*, so category is left empty) whose text is the file's `@ai-intent` plus the "Intent & Responsibility" bullets verbatim. Relations: `depends_on PF-<slug>@n`; `depends_on code:<module>` for each source file that resolves. Why claim, not purpose: the file is what the repo *claimed* the module does; Zach's current purpose is a separate record he writes (Kate's B condition).
- **D2 Versioning.** Record ids are stable slugs of the purpose-file path. Unchanged sha → nothing appended; changed sha → version n+1 of both records. Records file is read, never rewritten.
- **D3 Resolution.** A source file name resolves by exact repo-relative path first, then by unique basename among snapshot files; several matches → ambiguous finding; none → missing finding; non-`.py` → "not code" note.
- **D4 Declared vs observed callers.** Observed callers of module M = modules with an `imports` edge to M (or to a symbol under M) or a `calls` edge into M. Declared `@ai-used-by` tokens are compared by last dotted component. Tokens that match no module in the snapshot (e.g. `developer`) are reported once as "non-code consumers, not checked". Findings are `declared-not-observed` and `observed-not-declared`.
- **D5 Outcome sufficiency.** New optional fields: evidence `evidence_kind` ∈ {contract_conformance, behavioral_observation, outcome_observation}, claim `claim_category` ∈ {requirement_satisfaction, purpose_outcome}. Rule `outcome-sufficiency` (warning): a `purpose_outcome` claim with ≥1 supporting evidence where every supporting evidence is `contract_conformance`. Evidence without a kind is not counted as conformance (unknown ≠ conformance; avoids false alarms).
- **D6 Applicability.** New relation `observed_on` (evidence → `code:<symbol>`). In impact, a revise or retract of `code:X` gives evidence with `observed_on code:X` the status `needs_review`, which propagates `needs_review` to what it supports. It never yields `unjustified` (Kate: "an edit is not proof that observed behavior changed").
- **D7 init.** Writes only absent files: `.aec/records.jsonl` (owner authority `AU-owner` governing `purpose`, `design`, `acceptance`, `code`; provisional purpose stub `P0` with text "TODO: owner states the purpose"), `.aec/edges.jsonl`, `.aec/snippets/claude-settings.json` (PostToolUse hook), `.aec/snippets/aec-ci.yml`, `.aec/README.md`. Spec Kit detected by `.specify/` → prints `specify extension add --dev <path to AEC>/extension`. The purpose stub is provisional so it never blocks or authorizes anything.

- **D8 Source-root imports (added at converge).** Code run with `src/` on `sys.path` imports `src/x.py` as `x`. The extractor maps a bare top-level import `x` to `R.x` when exactly one top-level directory `R` has a module `x`, `x` is not itself top-level, and `x` is not a stdlib name. The header lists the `source_roots` used, so the mapping is visible rather than silent.
- **D9 Module map in the header (added at implement).** `header.modules` maps every parsed module to its file. Without it a module with no functions (constants only) could not be referenced or detected as deleted. Snapshots from 0.2.0 lack it and still diff (nothing is added for them).

## Project Structure
```
src/aec/init.py            # FR-001, FR-002
src/aec/purpose_import.py  # FR-003..FR-007
src/aec/records.py         # FR-008, FR-009 (+ observed_on in RELATIONS)
src/aec/impact.py          # FR-010
src/aec/__main__.py        # CLI: init, import-purpose
docs/reasoning-vocabulary.md  # FR-011 invariant, new fields
tests/test_init.py, tests/test_import_purpose.py, tests/test_aec.py (C, D)
tests/fixtures/purpose_repo/  # tiny package + purpose files incl. template, notebook, stale caller, missing source, ambiguous name
```
