# Tasks: AEC adoptable on a real repository

**Input**: spec.md, plan.md · **Tests**: required (Constitution III): violating fixture + decoy, written first.

## Phase 1: Setup
- [X] T001 Fixture repo `tests/fixtures/purpose_repo/`: package `pkg/` with `core.py`, `util.py`, `report.py`, two `helpers.py` (ambiguous basename), and `codex_++/purpose_files/` containing: core (correct callers), util (declares a caller that doesn't call it, misses one that does), report (source file deleted), a template file with placeholders, a notebook-sourced file, a header-less file, an ambiguous `helpers.py` file.
- [X] T002 [P] Start the feature 002 section in `docs/speckit-log.md` (authoring time, artifacts).

## Phase 2: US3 + US4 vocabulary (records/impact) — small, foundational
- [X] T003 [P] [US3] Tests in `tests/test_aec.py`: outcome claim with only conformance evidence → warning `outcome-sufficiency`, not error, claim not otherwise affected; + outcome_observation → no warning; requirement_satisfaction + conformance → no warning (decoy); unknown kind/category → error.
- [X] T004 [P] [US4] Tests in `tests/test_code_impact.py`: evidence `observed_on code:pkg.a.f`; f body changes → evidence `needs_review`, supported claim `needs_review`; f deleted → still `needs_review`, never `unjustified`; unrelated g changes → nothing (decoy).
- [X] T005 [US3] `records.py`: EVIDENCE_KINDS, CLAIM_CATEGORIES, rule `outcome-sufficiency`; `observed_on` in RELATIONS.
- [X] T006 [US4] `impact.py`: `observed_on` dependents get `needs_review` on revise/retract of the code pseudo-record.

## Phase 3: US1 init (P1)
- [X] T007 [P] [US1] `tests/test_init.py`: plain dir → files created, `check` 0 errors; second run → nothing overwritten, report lists kept files; with `.specify/` → output contains the extension command and no file under `.specify/` changes.
- [X] T008 [US1] `src/aec/init.py` + CLI `aec init [ROOT] --owner`.

## Phase 4: US2 import-purpose (P1)
- [X] T009 [P] [US2] `tests/test_import_purpose.py`: per fixture file the expected records/findings (provisional, provenance sha, verbatim intent, code links only when unambiguous; template skipped; notebook no link; header-less text-only + finding; ambiguous reported); used_by mismatch both directions; imported claim cannot authorize an accepted decision; idempotent re-run; changed file → version 2; `check --edges` passes after import.
- [X] T010 [US2] `src/aec/purpose_import.py`: parse, resolve, compare callers, append records.
- [X] T011 [US2] CLI `aec import-purpose [ROOT] --dir --records --edges --dry-run`.

## Phase 5: Polish
- [X] T012 [P] `docs/reasoning-vocabulary.md`: invariant (FR-011), new fields, observed_on; README: init + import sections with limits; extension README: point at init.
- [X] T013 [P] Data-Guide trial: copy, `init`, `import-purpose`, time it (SC-001), hand-verify 5 caller findings (SC-003); write results to `docs/data-guide-trial.md`.
- [X] T014 CI: run init+import on the fixture repo and `check --edges` after.
- [X] T015 AEC records: append `AEC-R7` (adoption by init/import, `implemented_by` code) and `AEC-R8` (outcome sufficiency) to `.aec/records.jsonl`; regenerate edges; `check --edges` clean.
- [X] T016 `docs/speckit-log.md`: analyze/converge findings vs AEC, authoring time, lessons.

## Dependencies
T001 → T009. T003/T004 → T005/T006. T007 → T008. T009 → T010 → T011. Polish last. US1, US2 and Phase 2 are independent of each other.

## Phase 6: Convergence (added after implement)
- [X] T017 Bare imports under a source root (`from data_profiler import …` for `src/data_profiler.py`) resolved to the real module, stdlib names excluded, `source_roots` in the header; test + stdlib decoy (found on Data-Guide: SC-003 was unreachable without it)
- [X] T018 Snapshot header carries a module→file map (tool_version 0.3.0) so modules with no functions resolve and count as deleted when removed; older snapshots still diff
- [X] T019 Caller attribution uses the enclosing module for function-local imports (the `data_profiler` ↔ `bivariate_profiler` cycle)
- [X] T020 `import-purpose` exits 2 with a message when the purpose-file directory is missing; CLI test
- [X] T021 Version bump: package and extension 0.3.0
- [X] T022 Kate round 4: deleting code that implements an obligation breaks its recorded satisfaction, not the obligation (`needs_review` + finding); claims that `depends_on` deleted code stay `unjustified`. Outcome check documented as a necessary-evidence-type check, not sufficiency
