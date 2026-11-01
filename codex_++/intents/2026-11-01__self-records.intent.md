# Self-records (dogfood) intent — 2026-11-01

@ai-intent: Bring AEC's own records up to date and make keeping them current a CI rule. Authorized by Zach (Claude chat, 2026-11-01 12:02 CT): "Yes, please. I would like to continue with the improvements that the repo is meant to bring about to agentic coding, including coding the repo itself."

## What changed

- Appended `AEC-R9` (WP-S) and `AEC-R10` (WP1A), each anchored to the spec passage it states and to the passage recording Zach's authorization.
- Appended `CL-R9-states` with `EV-R9-tests`. This is the repo's first claim and evidence, so `impact` and `code-impact` now have something to propagate to when `sources.py` changes.
- Appended `DEC-016` to `DEC-022` as projections of the canonical decisions in relay-kit-private (DEC-018: one canonical identity, many projections). Each has `origin: projection` and an anchor to its canonical line.
- `.aec/sources.json` names the `relay-kit-private` root (`../relay-kit-private`). In CI that root is absent, so those anchors report `unavailable`, never `missing`. Warnings don't fail the build.
- Added `tools/record_touch.py`, a CI step on pull requests. A diff that touches `src/` must append to `.aec/records.jsonl`, or carry a commit trailer `AEC-Record: none - <reason>`. Tests: two violating fixtures and four decoys. They were written alongside the code, not strictly before it.

## Findings from using AEC on itself (proposals; not implemented)

1. **An append-only log can't be anchored stably.** An anchor checks the digest of the whole file. Appending one unrelated line to `governance/decisions.jsonl` turned all 7 decision anchors to `mismatch`. The anchored lines were unchanged; this was simulated in a scratch copy. Every append to a ledger therefore asks for an applicability review of every anchor into it, which is noise. Mismatch on a log should be the rare case.
   - **Proposal:** an optional `passage_sha256`, the digest of the located lines. When the file digest differs but the passage digest matches, report a distinct state, for example `passage_verified`: the file changed and the anchored passage did not.
   - This changes the frozen spec 004, so it's for Zach (P-level), and its fixture and decoy come first.
   - Until then, these anchors will go to `mismatch` on the next ledger append.
2. **`decided_by` takes a bare authority id; relations take `id@version`.** Writing `AU-zach@1` produced 7 authority errors. The check is right by its own rule, but the two reference forms are easy to confuse. Proposal: accept `id@version` in `decided_by`, or say which form it takes in the error message.
3. **Authorizations are anchored second-hand.** The anchors point at the spec status lines and the handoff that quote Zach, not at a capture of the chat. That's "explicit and retrievable" only for the quotation. The DEC-017 safeguards package (recoverable provenance for authorizations) should decide whether a chat capture is required for consequential ones.
4. **The record-touch rule is structural.** It makes keeping records current visible. It can't tell whether a record is any good, and the trailer can be used to dodge it. If the trailer comes to dominate, that's evidence the rule costs more than it catches (DEC-016's "remedy costs more than the risk").

## Not done

- No record for the deletion fix, because it's in open PR #21. That PR gets its own claim and evidence.
- Both this PR and #21 append to the end of `.aec/records.jsonl`. Whichever merges second keeps both blocks, and its `.aec/edges.jsonl` is regenerated.
