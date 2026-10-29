# Tasks: AEC reconciled with itself (WP0)

Tests first for each check: a violating fixture plus a decoy (Constitution III). Mark tasks `[X]` as you finish them. Keep the intent note (T001) open the whole time and add to it as you go.

## Phase 1: Setup
- [X] T001 Create `codex_++/intents/<date>__wp0-implementation.intent.md`. Record your starting understanding of AEC (5 lines, from the repo only). Then log questions, assumptions and rework as they happen (FR-010).
- [X] T002 Branch `speckit/003-self-reconciliation` from `main`. Confirm the baseline: all tests pass, and `aec check .aec/records.jsonl --edges .aec/edges.jsonl` gives 0 errors.

## Phase 2: US2 importer (P1)
- [X] T003 [P] Fixtures: add to `tests/fixtures/purpose_repo/codex_++/purpose_files/` a file with singular `@ai-source-file` (with `-`, `#` and bare prefixes, in separate files), a file using both singular and plural, a file with an IO table plus each heading variant from FR-002, and a file over 5,000 characters. Decoy: the existing fixture files must import exactly as before (US2-4).
- [X] T004 [P] Tests in `tests/test_import_purpose.py`: singular links (US2-1); structured fields (US2-2); no truncation (US2-3); unknown fields kept (US2-5); duplicate-source finding; existing expectations unchanged.
- [X] T005 Implement P1–P3 in `src/aec/purpose_import.py`.
- [X] T006 Run import on a copy of AEC itself (`aec init` on a temp copy, then `aec import-purpose`). Check SC-001 and record the output in the intent note. Do NOT append imported records to AEC's own `.aec/records.jsonl` in this feature.
- [X] T007 If `eraevous/Data-Guide` can be cloned, run import on a copy and record the `declared_io` count for SC-002. Otherwise record why not.

## Phase 3: US1 docs (P1)
- [X] T008 [P] `tests/test_docs_truth.py` (P6), with a decoy that must fail.
- [X] T009 Rewrite `AGENTS.md` (P5, FR-005). Move the old one to `docs/history/`.
- [X] T010 Rewrite `CHARTER.md` (FR-006). Fix `VISION.md` references.
- [X] T011 Update `README.md`: the governing-documents rule (US1-2), the built/partial/planned labels (US4), and pointers to `docs/architecture.md` and `docs/failure-modes.md`.

## Phase 4: US3 history (P2)
- [X] T012 Write `.aec/reconstructed/2026-10-history.jsonl` from `docs/speckit-log.md`, `specs/001-ast-bedrock-extension/{plan,research}.md` and `specs/002-adoptable-aec/{plan,tasks}.md`, with at least 15 decisions. Include feature 001's "deleted implementation ⇒ requirement unjustified" and its reversal (T022) linked by `supersedes`.
- [X] T013 [P] Tests for `tools/reconstruct_decisions.py`: records appended with source sha256; nothing `accepted`; reversal linked; the existing records file is a byte-for-byte prefix of the new one; a decoy input with `status: accepted` is refused.
- [X] T014 Implement `tools/reconstruct_decisions.py`. Run it once against AEC's own `.aec/records.jsonl` and generate `docs/decisions-to-confirm.md`.

## Phase 5: Polish
- [X] T015 Regenerate `.aec/edges.jsonl`. `aec check --edges` must give 0 errors, and the full test suite must pass.
- [X] T016 Update the purpose files for `aec.records` and `aec.impact`? **No.** Leave the purpose files as they are: they are claims, and changing them is a separate decision. Note in the intent note anything in them you found false.
- [X] T017 Finish the intent note: questions, assumptions, unclear or wrong spec items, rework, and time spent. Open a PR to `main` titled "003: AEC reconciled with itself (WP0)". Link the intent note from the PR body, and list anything you could not do.
