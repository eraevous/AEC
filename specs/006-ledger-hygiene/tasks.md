# Tasks: ledger hygiene (spec 006)

- [X] T001 Spec, plan, tasks; spec 004 addendum; intent note `codex_++/intents/2026-11-04__ledger-hygiene.intent.md`.
- [X] T002 Baseline: full suite and `aec check` on own records (13 anchor warnings).
- [X] T003 Fixtures and decoys (`tests/fixtures/anchors/appended.json`, `tests/fixtures/duplicates/*.jsonl`) and failing tests `tests/test_ledger_hygiene.py`.
- [X] T004 C-09: `prefix_bytes` shape, `append_only` configuration, `appended` state in check/show (FR-1..6).
- [X] T005 C-21: identical duplicate lines load once with a `duplicate-line` warning; differing stay `unique` errors (FR-7..9).
- [X] T006 Declare relay-kit-private `governance/decisions.jsonl` append-only in `.aec/sources.json`; re-run own check (SC-3).
- [X] T007 Docs: `docs/reference/source-anchors.md`, `docs/reference/records-hygiene.md`, CHANGELOG Unreleased, speckit log.
- [X] T008 Append requirement/claim/evidence records; regenerate edges; `check --edges`; full suite.
- [X] T009 Fix round after the DEC-038 reviews (Kate; review:claude-fresh; `addendum-fix-round.md`): exact-line duplicate comparison; line boundary for `prefix_bytes` growth; supersession wording in the `appended` note; owner-only manual deletion; `append_only` per alias. Tests first (a53618c).
