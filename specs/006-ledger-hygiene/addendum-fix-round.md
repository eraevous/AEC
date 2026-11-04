# Spec 006 addendum: fix round after the DEC-038 reviews (2026-11-04)

Reviews of PR #48 by Kate and review:claude-fresh. `spec.md` is not edited (AEC-R11@1 anchors it whole);
these requirements tighten it.

- **FR-3a** (Kate, blocking) A proper prefix must end with a newline, for `prefix_bytes` as for declared
  `append_only` files: growth after a mid-line prefix extends its last line and is `mismatch`. A file equal
  to the anchored bytes is still `verified` whether or not it ends with a newline.
- **FR-3b** (both, should-fix) The `appended` detail says a later entry may supersede the anchored one,
  not only that later bytes are unchecked.
- **FR-8a** (both, blocking) Duplicate lines are compared as written (split on LF only): leading or
  trailing whitespace and CRLF vs LF are differences, so such a copy is the error `unique`.
- **FR-9a** (both, should-fix) The manual removal in `docs/reference/records-hygiene.md` is the owner's
  call and does not itself authorize deleting a line.
- `append_only` applies per root alias (documented in `docs/reference/source-anchors.md`).

| Fixture | Expected |
|---|---|
| `prefix_bytes` ending mid-line, then growth extending that line | `mismatch` |
| `prefix_bytes` newline-ended then growth; mid-line prefix, file unchanged (decoys) | `appended` / `verified` |
| copy differing only by trailing space (`tests/fixtures/duplicates/trailing-space.jsonl`), leading space, or CRLF | error `unique`, exit 1 |
| byte-identical copy, LF or CRLF throughout (decoys) | warning `duplicate-line` |

Tests: `tests/test_ledger_hygiene.py` (committed failing first, a53618c).
