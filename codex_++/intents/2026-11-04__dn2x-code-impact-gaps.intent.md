# DN2X code-impact gaps intent — 2026-11-04

@ai-intent: Close or measure the three `code-impact` gaps Codex found (HO-AEC-20261102-A5RR, section B) before the DEC-031 trial, then run Codex's coverage/delivery qualification. Handoff HO-RK-20261104-DN2X, authorized by Zach ("Write that handoff", 2026-11-03 20:41 CT), dispatched under DEC-048. Branch `dn2x/code-impact-gaps`, one PR; Zach merges.

## Decisions taken inside the authorization

- **Module links (gap 2): fixed in `code_impact.py`, not `edges.py`.** Giving modules a real hash in the snapshot would change the snapshot format and the tool version, which every stored baseline is compared under. Instead a module is "changed" when a definition or module-level edge it owns changes (longest module prefix decides ownership, so a package link does not cover submodules). Rationale: this is the reading a class link already gets (its hash covers its methods), so it fixes a placeholder rather than changing what a link means.
- **Helpers and constants (gap 1): status-free pointers.** Codex warns that letting a changed callee mark the caller's rationale stale changes what a link means. That is outside the authorization, so it is written up as a proposal in the handoff output. What was built is a report line: a changed definition one resolved calls/references step from a linked symbol, with the records to re-check. Default depth 1 because depth 2 on Telosmith's history raised pointers from 22 to 36 for no measured benefit.
- **Folding.** A pointer whose records the report already classifies is dropped (56 → 22 on Telosmith's history). Tested with a mixed decoy.
- **Delivery (gap 3).** Hook: compare with `HEAD` after each edit, exit 2 to the agent only when something linked moved. CI: merge-base comparison into the job summary, never failing the job, no PR comment (PR comments are a gated adoption item, DEC-032). `--exit-code` added so the hook can tell "nothing" from "something" without parsing text. Telosmith's own CI runs the same step on PRs so this PR's run is a live delivery check.

## Questions and assumptions

- Assumed the reorder false alarm (swap `min` arguments) is to be measured, not fixed: equivalence is semantic and Constitution IV keeps `code-impact` structural.
- Assumed "reaches a reviewer" may be satisfied by the Actions job summary and agent stderr; neither shows anyone reads them.
- DEC-038: this changes a classifier's output and the generated CI. It needs at least two reviewers, one from another model family, before merge. None was arranged inside this handoff.
- Concurrent work: hygiene/c09-c21 (anchors, duplicate-line checks). Not touched. Both branches may append to `.aec/records.jsonl`; whichever merges second keeps both blocks.

## Rework

- First cut of the pointer report repeated records that were already stale; the history replay showed 34 of 56 pointers were redundant, so folding was added with its own test.
