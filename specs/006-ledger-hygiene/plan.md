# Implementation Plan: ledger hygiene (spec 006)

**Branch**: hygiene/c09-c21 · **Spec**: [spec.md](spec.md) · **Base**: origin/main 906e8fd · **Date**: 2026-11-04

## Constitution check

I: the spec cites AEC-P0@1, AEC-R2@1, AEC-R9@1; new records are appended. II: stdlib only;
hashing is incremental `hashlib` over line boundaries, deterministic. III: fixtures and decoys
(`tests/fixtures/anchors/appended.json`, `tests/fixtures/duplicates/`) and
`tests/test_ledger_hygiene.py` were committed failing before code. IV: `appended` says the
anchored bytes are intact and the later bytes unchecked; nothing about meaning. V: cost in the
intent note. VI: unaffected.

## Design

- `sources.anchor_errors`: validate optional `prefix_bytes` (positive int, not bool).
- `SourceContext.roots` also parses `append_only` into a set of (alias, posix path); aliases must be
  configured or `.`; paths obey the anchor path rule.
- `SourceContext.inspect`: after reading raw bytes, choose the anchored bytes:
  `prefix_bytes` → `raw[:n]` if `len(raw) >= n` and its digest matches; declared append-only →
  the shortest newline-ended prefix (or the whole file) whose digest matches, found with one
  incremental hash pass. Then the locator resolves against the anchored bytes' lines. State:
  whole file → `verified`; proper prefix → `appended`; none → `mismatch` (current-file locator
  kept for `show`, as before).
- `record_findings` treats `appended` like `verified` (no finding). `check` CLI prints status
  lines for both. `render_show` prints a `NOTE:` (not a `WARNING:`) for `appended`.
- `Store.load` keeps the first text of each `id@version`; an identical later line is skipped and
  a `duplicate-line` warning goes into `problems`. A differing line still loads, so `check`'s
  `unique` rule reports it.

## Validation

New tests, full suite, `aec check` on `.aec/records.jsonl` before/after (13 → 3 warnings with the
ledger declared), examples check, regenerate `.aec/edges.jsonl` and `check --edges`.
