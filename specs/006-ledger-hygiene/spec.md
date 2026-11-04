# Feature Specification: ledger hygiene (C-09 append-only anchors, C-21 duplicate record lines)

**Feature Branch**: `hygiene/c09-c21`
**Created**: 2026-11-04
**Status**: **Authorized by Zach** (2026-11-04 09:17 CT, recorded as DEC-048 in relay-kit-private): "I authorize C-09 ... C-21." Candidates: relay-kit-private `governance/candidates.md`, C-09 and C-21.
**Serves**: `AEC-P0@1`, `AEC-R2@1` (claim honesty), `AEC-R9@1` (source anchors).
**Changes**: frozen spec 004 (data contract: `sha256` is whole-file). Spec 004 is not edited; `specs/004-source-anchors/addendum-2026-11-04.md` points here. Whole-file digests stay the default.

## Why

**C-09.** An anchor digests the whole file. An anchor into an append-only ledger (relay-kit-private `governance/decisions.jsonl`) turns to `mismatch` after every append, although the anchored passage is unchanged. On 2026-11-04 Telosmith's own records carried 13 anchor warnings; 10 were anchors into that ledger whose original bytes are still its exact prefix. Warnings that are noise train readers to ignore the real ones.

Kate's review (2026-11-02, in the candidate): a line hash or a hash of the file through the anchored line does not show that an append-only file kept what it had when anchored. Design: pin the original byte length and full-file hash, and verify that the current file *begins with* exactly those bytes. That is what this spec builds. A separate per-passage digest is not added.

**C-21.** Two branches that append the same record line, once merged, leave a byte-identical second copy. `check` then fails main with "duplicate id@version", and the only remedy was deleting a line from an append-only ledger (Fathom PR #14).

## Requirements

### C-09: prefix integrity for append-only files

- **FR-1** An anchor may carry `prefix_bytes`, a positive JSON integer: the file's length in bytes when it was anchored. Its `sha256` is then the digest of those first `prefix_bytes` bytes (which was the whole file at anchoring time). Any other value (0, negative, string, boolean, float) is an anchor-shape **error**.
- **FR-2** `.aec/sources.json` may carry `append_only`: an object mapping a configured root alias (or `.` for the repository) to a list of relative file paths. A whole-file anchor (no `prefix_bytes`) into a declared file is checked against every prefix of the current file that ends just after a newline, and against the whole file. A malformed `append_only` (not an object, unknown alias, non-list, empty or escaping path) is a usage error, like other malformed source configuration.
- **FR-3** New state **`appended`**: the current file is longer than the anchored bytes and begins with exactly those bytes (equal SHA-256 of the prefix). The locator must resolve inside the anchored prefix; otherwise `locator_invalid`. `appended` is distinct from `verified` and `mismatch` in `check` and `source show` output, and produces **no finding** (like `verified`). Its detail says the later bytes are not checked.
- **FR-4** If the anchored prefix differs, or the file is shorter than `prefix_bytes`, the state is `mismatch`, as before. A file equal to the anchored bytes is `verified`.
- **FR-5** Without `prefix_bytes` and outside `append_only`, nothing changes: a grown file is `mismatch` (P8-2 stays as frozen).
- **FR-6** `source search` is unchanged: an `appended` anchor's digest is not the current file's digest, so it is listed under `records_path_only`.

### C-21: byte-identical duplicate record lines

- **FR-7** When a records file holds a line whose text is identical to an earlier line with the same `id@version`, the copy is read as the same record (loaded once) and `check` reports a **warning** `duplicate-line`, naming both line numbers. Exit status is unaffected.
- **FR-8** The same `id@version` with any difference in line text (content, or the same JSON written with different bytes) remains the **error** `unique`.
- **FR-9** No command rewrites a records file. Removing the copy is a documented manual procedure (`docs/reference/records-hygiene.md`), because AGENTS.md and Constitution II make record lines append-only and a tool that deletes ledger lines would need its own owner decision.

## Fixtures (written before implementation)

| Fixture | Expected |
|---|---|
| `prefix_bytes`, file grown by an append | `appended`, no finding |
| `prefix_bytes`, file unchanged (decoy) | `verified`, no finding |
| `prefix_bytes`, first line edited then appended | `mismatch` |
| `prefix_bytes`, file truncated | `mismatch` |
| `prefix_bytes`, quote only in the appended bytes | `locator_invalid` |
| whole-file anchor, grown file, not declared (decoy for the default) | `mismatch` |
| declared append-only, grown / edited / unchanged | `appended` / `mismatch` / `verified` |
| declared append-only, original ended mid-line | `mismatch` |
| `prefix_bytes` 0, `"45"`, `true` | error |
| byte-identical duplicate line (`tests/fixtures/duplicates/identical.jsonl`) | one record, warning `duplicate-line`, exit 0 |
| same id@version, different content; same JSON reformatted (decoys) | error `unique`, exit 1 |

## Success criteria

- **SC-1** Every fixture yields exactly its expected state or finding; decoys are not flagged beyond their expected state.
- **SC-2** Output is byte-identical across runs; standard library only; full suite passes.
- **SC-3** On Telosmith's own records, with relay-kit-private's `governance/decisions.jsonl` declared append-only, anchor warnings drop from 13 to the real mismatches (3: AEC-R9@1's handoff anchor and AEC-R10@1's two anchors into a since-edited spec). Existing record lines are unchanged.
- **SC-4** No output template says an `appended` anchor supports, proves or authorizes anything.

## Out of scope

- A per-line or per-passage digest (Kate: insufficient as an append-only proof).
- Detecting duplicates before merge in `tools/record_touch.py` or CI (C-21's second option).
- A command that removes duplicate lines.
- Re-anchoring existing records with `prefix_bytes` (would mean appending new versions; the old versions would still be checked).
