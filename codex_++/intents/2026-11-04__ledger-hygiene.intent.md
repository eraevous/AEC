# Ledger hygiene (C-09, C-21) intent — 2026-11-04

@ai-intent: Stop anchors into append-only logs from reading as `mismatch` after every append, and stop a byte-identical duplicate record line from failing `check`. Authorized by Zach (2026-11-04 09:17 CT, DEC-048 in relay-kit-private): "I authorize C-09 ... C-21." Implementer: claude:aec-hygiene, from origin/main@906e8fd. Spec: `specs/006-ledger-hygiene/`.

## Interpretations (made under delegation; overridable)

1. **Prefix, not passage digest.** The brief says "an optional passage-level digest"; the candidate records Kate's review that a line or through-the-line hash doesn't show an append-only file kept what it had. Kate's design (pin the original length and full-file hash; the current file must begin with exactly those bytes) is what the owner and Kate agreed, so that is built: `prefix_bytes`. The anchored passage is covered because the locator must resolve inside the anchored prefix. No separate passage digest was added.
2. **Existing anchors without rewriting records.** Telosmith's 10 ledger anchors (DEC-016..025@1) carry no `prefix_bytes`, and appending new versions would leave the old versions checked and still warning. So `.aec/sources.json` gains `append_only`, a per-file opt-in under which a whole-file digest may match a newline-ended prefix. One incremental hash pass; SHA-256 equality means the prefix is exactly the original bytes, so this is as strong as a pinned length, only found rather than recorded. Whole-file stays the default everywhere else (P8-2 unchanged).
3. **`appended` is not a finding.** It is printed by `check` (with byte counts) and by `source show` (as `NOTE:`), never as `verified`. Rationale: the warning count should be the anchors that need review. Dissent: a later ledger line can supersede the anchored one (e.g. DEC-046 superseded by DEC-043, both appended); `appended` deliberately says the later bytes are unchecked and does not catch that. If supersession-by-append matters, a reader or a future rule over the ledger's own `supersedes` fields has to catch it.
4. **C-21: no dedupe command.** AGENTS.md says never edit existing record lines, and Constitution II makes records append-only. Deleting a copy changes no record's content, but a tool that removes ledger lines is a new power, so it is left for an owner decision. Instead: the copy is loaded once with a `duplicate-line` warning, and `docs/reference/records-hygiene.md` documents a manual removal. "Byte-identical" means identical line text after stripping surrounding whitespace and line endings (how `Store.load` already reads lines); reformatted JSON stays an error.
5. **Spec folder.** Features each get a folder (`docs/speckit-log.md`); C-21 is not about anchors. So spec 006 holds both, and `specs/004-source-anchors/addendum-2026-11-04.md` only points to it.

## Run

- Baseline: 173 passed, 1 skipped (pytest); own `aec check`: 0 errors, 13 warnings (all anchor mismatches).
- Fixtures and tests committed first (2a7ead4): 14 failing, 6 passing.
- After: full suite passes; own `aec check`: 0 errors, 3 warnings. Remaining: AEC-R9@1's anchor into handoff HO-20261030-001.md and AEC-R10@1's two anchors into spec 005; both files were edited, not appended (no prefix of either matches), so they are real mismatches for review. AEC-R10@2 already re-anchors spec 005.
- Appended AEC-R11@1, CL-R11-hygiene@1 and EV-R11-hygiene-tests@1. AEC-R11's rationale anchor points into the ledger with `prefix_bytes`, so it is the first record written in the new form.

## Not done

- C-21's other option (flag the duplicate in `tools/record_touch.py`/CI before merge).
- A dedupe command (see 4).
- Re-anchoring DEC-016..025 with `prefix_bytes`.
- No `/speckit-analyze` or `/speckit-converge` agent run.

## Cost

About 45 minutes of agent wall time from reading to PR; token count not instrumented. Owner time: none (authorization only).
