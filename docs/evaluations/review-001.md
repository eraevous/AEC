# review-001: first independent audit (GitHub Copilot, 2026-11-01)

**Reviewer:** GitHub Copilot, run by Zach at "Balanced" review effort.
**Commit:** not stated by the reviewer. It is consistent with main at `7828a7d` (2026-11-01 18:19 CT,
just after PR #32), whose suite has the 161 tests the report counts.
**Prompt:** [as run](review-001/prompt.md), which became protocol v1 with two changes
([review-protocol.md](review-protocol.md)). **Report:** [verbatim](review-001/report.md).

## Findings and dispositions

Every finding was reproduced by claude:aec-release before it was acted on.

| # | Finding (reviewer's severity) | Reproduced | Disposition |
|---|---|---|---|
| 1 | `check` accepts malformed identity and freeze metadata: `version: 1.9` loads as 1; any truthy `frozen_sha256` passes (medium) | yes | **Fixed**, PR #33: a non-integer version is an error, and the digest must be SHA-256 shaped |
| 2 | `foo.py` beside `foo/__init__.py` collide; one file's calls vanish silently (medium) | yes | **Fixed**, PR #33: the package is analysed (as Python imports it); `foo.py` is reported as shadowed |
| 3 | probe-001 shows no incremental value on its tasks (medium, strategic) | n/a | **No code change.** It matches the README and probe-001-results. It feeds the open "is AEC worth its cost?" question (below) |
| 4 | A file edited between the extractor's two passes yields a snapshot mixing both versions (low) | yes | **Fixed**, PR #33: both passes parse the hashed bytes, and a change between them stops extraction |
| A | `docs/architecture.md` status table out of date (WP0 "awaiting merge", WP1A "pending review") | yes | **Fixed**, PR #33 |

## What the review didn't cover

These are gaps relative to its own prompt; next runs should watch for them:

- **Phase 4, question 7 ("where might AEC itself drift?")** was answered only through the status table.
  The repository's history has better examples: duplicated candidate ids, documentation claims that
  went stale, and records lagging code changes.
- **Security, coupling between modules, and test quality** (not just whether tests pass) got little
  attention, as did the Spec Kit extension and the CI workflows.
- The prompt's "AI-Enhanced Coding" expansion of AEC wasn't flagged as unverifiable. The report
  doesn't repeat it either.

## Architectural dissent, recorded

The reviewer's strongest criticism is that it's unproven whether AEC's records and graph are worth
their authoring and maintenance cost. The pilot shows no gain, and the reasoning graph only acts on
links people keep up to date. It argued against both abandoning AEC and adding infrastructure. Its
view is that the open questions are whether people can maintain the records accurately, and whether
AEC changes decisions enough to justify that work. This is committed requirement AEC-R3 ("Adoption is
earned against a well-configured Spec Kit baseline with authoring cost counted; if equal, simplify
AEC"), restated by an outsider.
