# About AEC: background, principles and direction

## Background

AEC (formerly Codex++) explores continuous architectural reasoning for AI-assisted development: helping an AI development system understand what it is building, observe what it is becoming, detect when those diverge, and preserve the reasoning needed for deliberate change. It connects executable structure, semantic purpose, evidence, authority and agent coordination. The current implementation provides structural analysis and reasoning records, with a Spec Kit integration. Spec Kit is one integration surface, not the boundary of AEC; the capability table below distinguishes what is built, partial and planned.

The white paper, *AEC as an extension to specification-driven development* (Zachary Rhodes, 26 October 2026), records the earlier positioning, evidence and validation plan. The approved direction is described in `docs/architecture.md`.

## Principles

The repo carries its own purpose, decisions and objections, so agents can act as collaborators that notice drift rather than as autocomplete. If ordinary Spec Kit artifacts perform as well, the right result is to simplify AEC.

## Capabilities and direction (as of v0.4)

| Capability | Status | Evidence or next step |
| --- | --- | --- |
| Seven CLI subcommands: check, impact, edges, code-impact, init, import-purpose, source | built | `src/aec/` and the unit tests under `tests/` |
| Structured purpose import with singular/plural source headers and full source text | built | `src/aec/purpose_import.py`, `tests/test_import_purpose.py` |
| Source-linked proposed history and confirmation list | built | `tools/reconstruct_decisions.py`, `docs/decisions-to-confirm.md` |
| Repository path and CLI-name documentation checks | built | `tests/test_docs_truth.py` |
| Semantic contracts and reconciliation | partial | Imported declarations and caller comparisons; no semantic verdict engine |
| Evidence-kind adequacy and revision applicability | partial | Narrow outcome-sufficiency and observed_on rules |
| Commit-addressed snapshots and topology/co-change analytics | planned | WP1A/WP1B |
| Context delivery, reconciliation packets and automatic drift triggers | planned | WP2A/WP3 |
| Handoff premise checks and comparative evaluation | planned | WP4/WP5 |
| Adaptive, purpose-aware project reporting profiles | backlog proposal | WP6: project-specific baseline and interpretive reports, provenance, profile reconciliation; [issue #15](https://github.com/eraevous/AEC/issues/15) |

See `docs/architecture.md` for the direction **approved by Zach on 29 October 2026**,
and `docs/failure-modes.md` for evaluation design. WP6 is separately tracked as a 2026-10-30 backlog addition, not yet specified or implemented. WP1–WP5 are approved as direction;
each still needs its own spec and PR. Approval does not establish that planned
features are built or that AEC improves owner outcomes. A passing record check
establishes formal consistency only, not the truth, adequacy or independence of
evidence. Reconstructed history remains proposed in `docs/decisions-to-confirm.md`.
Runtime dependencies: none beyond Python 3.10+; the legacy extractor is not shipped.
