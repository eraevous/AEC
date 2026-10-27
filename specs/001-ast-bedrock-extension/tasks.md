# Tasks: AST bedrock + AEC as an installable Spec Kit extension

**Input**: `specs/001-ast-bedrock-extension/` (spec, plan, research, data-model, contracts)
**Tests**: required by Constitution III. Each check gets a violating fixture and a decoy, written before the code.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Create the fixture packages `tests/fixtures/edges_pkg_v1/` and `edges_pkg_v2/`: module functions, a class with methods and a base class, an async function, aliased and relative imports, a dynamic `getattr` call, a syntax-error file, two modules defining the same function name, an `import *`, and a function-local import (analyze A4). Write a hand-labelled `expected_edges.json` for v1.
- [X] T002 [P] Start `docs/speckit-log.md` (Constitution V): record the authoring time and the Spec Kit artifacts produced so far.

## Phase 2: Foundational

- [X] T003 Add a `code:` reference type to `src/aec/records.py` (data-model §Code reference): reference parsing accepts `code:<dotted>` without a version.

## Phase 3: User Story 1, ground truth on every change (P1) 🎯 MVP

### Tests (write first; they must fail)
- [X] T004 [P] [US1] `tests/test_edges.py`: the v1 fixture edges equal `expected_edges.json` for the defines, calls, imports and inherits kinds (SC-001, FR-001, FR-002), plus labelled `references` edges (analyze A2).
- [X] T005 [P] [US1] `tests/test_edges.py`: two runs are byte-identical (SC-003, FR-003). The syntax-error file is listed in `skipped` and the other files still run.
- [X] T006 [P] [US1] `tests/test_edges.py`: diff(v1, v2) is exactly the labelled changes (one call added, one function removed, one body changed). A decoy (whitespace-only change) produces an empty diff (FR-004).
- [X] T007 [P] [US1] `tests/test_edges.py`: the dynamic `getattr` call gives an unresolved `?` target and no guessed edge.
### Implementation
- [X] T008 [US1] `src/aec/edges.py`: walk the files, derive module names (research R2), collect imports, then the defines, inherits, calls and references visitors, then sort, plus the snapshot header (data-model).
- [X] T009 [US1] `src/aec/edges.py`: `diff(old, new)`, including `defs_changed` via `body_sha`.
- [X] T010 [US1] Wire `edges` and `edges --diff` into `src/aec/__main__.py` (contracts/cli.md), plus `--legacy-csv` (research R4).
- [X] T011 [US1] Timing check on Data-Guide (SC-002); record the result in `docs/speckit-log.md`.

## Phase 4: User Story 2, code change to affected conclusions (P2)

### Tests
- [X] T012 [P] [US2] `tests/test_code_impact.py`: a record `implements code:pkg.a.f`. If f's calls change, the requirement and its dependents are reported. If an unlinked function changes, nothing is reported (decoy, SC-004). If f is deleted, the requirement is unjustified (FR-007).
- [X] T013 [P] [US2] `tests/test_aec.py`: `aec check --edges` reports a dangling `code:` reference (violation) and passes a valid one (decoy) (FR-006).
### Implementation
- [X] T014 [US2] `src/aec/code_impact.py`: diff, then change events (data-model), then `impact()`, treating `code:` targets as pseudo source records.
- [X] T015 [US2] `records.check(store, edges=None)`: dangling code references. CLI `check --edges`.
- [X] T016 [US2] CLI `code-impact`.

## Phase 5: User Story 3, AEC inside the Spec Kit flow (P3)

### Tests
- [X] T017 [P] [US3] `tests/test_extension.py`: the manifest parses and matches contracts/extension.yml.md. Every `provides.commands[].file` exists. Every hook command is provided. All hooks are optional (FR-008).
- [X] T018 [US3] `tests/test_extension.py` (skips if `specify` is absent): `specify init` in a temp dir, then `specify extension add extension/`, and the hooks appear in `.specify/extensions.yml`. Then `specify extension remove aec`, and the AEC hooks are gone and no core template has changed (FR-008, FR-009).
### Implementation
- [X] T019 [US3] `extension/extension.yml` plus three command files that report findings only (research R6 for locating the package).
- [X] T020 [US3] `extension/README.md`: install, uninstall, what each hook does, the structural-only label.

## Phase 6: User Story 4, Data-Guide (P4)

- [X] T021 [US4] Run `aec edges` on a Data-Guide checkout, then compare `--legacy-csv` output with its `ast_deps.csv`. Write the classified differences to `docs/data-guide-trial.md`.
- [X] T022 [US4] Install the extension into a temp Spec Kit-initialized copy of Data-Guide. Time it against SC-005 and record the result.

## Phase 7: Polish and cross-cutting

- [X] T023 [P] Add the CI steps: `edges` on the repo itself, `check --edges` on `.aec/records.jsonl`, and the extension tests.
- [X] T024 [P] Add an editor hook example (`.claude/settings.json` PostToolUse → `python -m aec edges . -o .aec/edges.jsonl`) per FR-005a.
- [X] T025 README: the edges and code-impact sections, labelled structural, with the limits stated.
- [X] T027 [P] `tests/test_stdlib_only.py`: every module under `src/aec/` imports only the standard library (`sys.stdlib_module_names`) (FR-005, Constitution II; analyze A3).
- [X] T026 `docs/speckit-log.md` (FR-010): the analyze and converge findings vs AEC findings, authoring time, and lessons.

## Dependencies

Setup (T001–T002) → Foundational (T003) → US1 (T004–T011) → US2 (T012–T016) needs US1's diff. US3 (T017–T020) is independent of US2, and US4 needs US1 and US3. Polish comes last.
**MVP** = through T011. **Parallel**: T004–T007, T012–T013 and T017 are separate test files.

## Phase 8: Convergence

- [X] T028 Restrict packaging to the `aec` package so `pip install` doesn't ship the legacy top-level `core` package (pandas and typer code under a generic name) per FR-009, Constitution II (contradicts)
- [X] T029 Add an automated install test: build and install into a temp venv, then `python -m aec edges` on the fixture, per FR-009 (missing)
- [X] T030 Complete `docs/speckit-log.md` with the implement and converge findings, total authoring time, and lessons, per FR-010, Constitution V (partial)
- [X] T031 Add `root` to the snapshot header, per data-model §Snapshot header (partial)
- [X] T032 Measure memory and time on a larger tree (this repo plus the stdlib `email` package) and record the result, per spec Edge Cases: very large repos (missing)
- [X] T033 Note in contracts/extension.yml.md that the manifest's `category` and `effect` fields follow the core extensions' convention, per plan R5 (unrequested)

