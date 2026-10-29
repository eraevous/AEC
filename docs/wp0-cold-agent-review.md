# WP0 repository-only usability check

Observed 2026-10-29. A fresh agent with no conversation history received a
repository-only copy, read AGENTS and the ten frozen questions, and used only
that copy's docs/code. It did not modify repository files or consult external
sources. This is candidate machine evidence, not technical/purpose acceptance.
The copy preceded the final compact-IO parser fix, which changes none of the
questions' answers. Paths below are repository-relative.

## Fresh-agent answers (recorded with path prefixes normalized)

1. AEC keeps why something is built attached to what gets built in AI-assisted
   development, so broken justifications are caught and legitimate revisions
   remain distinguishable. Authoritative committed purpose: AEC-P0@1; governing
   authority: AU-zach@1. Sources: .aec/records.jsonl and AGENTS.md.
2. Six subcommands: check (formal record/code-reference invariants), impact
   (explicit record change events), edges (extract/diff Python AST snapshots),
   code-impact (derive code events and affected conclusions), init (scaffold
   absent files without overwrite), import-purpose (provisional source-linked
   declared contracts). Sources: AGENTS.md and src/aec/__main__.py.
3. Python >=3.10; no third-party runtime dependencies. Legacy src/core is excluded
   from distribution. Source: pyproject.toml.
4. Committed records govern; purpose files are candidate semantic claims and
   cannot override purpose/authority records. Report disagreement and propose
   reconciliation. Source: AGENTS.md.
5. Zach or a decision-maker explicitly authorized for the subject may accept.
   An accepted decision has status=accepted and decided_by naming an authority
   whose governs includes its subject; AU-zach governs aec-scope. Reconstructed
   decisions remain proposed; typed authorization does not verify actual consent.
   Sources: AGENTS.md, .aec/records.jsonl, src/aec/records.py.
6. In the code-change pipeline, deletion of a requirement's implemented_by target
   gives needs_review and an implementation-path finding; a claim explicitly
   depending on deleted code gets unjustified. Plain impact cannot discover code
   deletions or synthesize code records: an absent code target reports "change
   target ... does not resolve" and leaves conclusions unaffected. code-impact
   supplies the synthetic records and deletion events. Sources: src/aec/impact.py,
   src/aec/code_impact.py, CLI and docs/reasoning-vocabulary.md.
7. Passing check means its implemented formal checks found no errors; zero exit
   status may still include warnings. It does not establish semantic correctness,
   evidence quality/independence, human consent, satisfaction or purpose achievement.
   Sources: src/aec/records.py, CLI and README.md.
8. Built: static topology, reasoning checks/impact, six commands, candidate history,
   doc checks. Partial: declared contracts/caller comparison and narrow evidence
   adequacy/applicability rules. Planned: commit-addressed snapshots, analytics,
   context delivery, reconciliation packets, drift triggers and handoff premise
   checks. Architecture is proposed, WP0 implemented pending review. Sources:
   docs/architecture.md and AGENTS.md.
9. Run CI's unittest discovery, regenerate edges, check canonical records against
   edges, and check the example records, with PYTHONPATH=src. CI uses Python 3.12
   and pinned Spec Kit v1.2.3. It additionally copies the purpose fixture into
   RUNNER_TEMP, runs init, import-purpose and check against its edges. Missing
   specify skips install/remove; pip build dependencies are needed for packaging.
   Sources: .github/workflows/ci.yml and AGENTS.md.
10. Calls through local objects/dynamic access may remain unresolved; unresolved
    reads have no edges. Only parsed Python files are visible: non-Python and
    skipped-file consumers are absent. No known caller does not prove no caller.
    Sources: src/aec/edges.py and AGENTS.md.

## Discrepancies found and disposition

- Question 6 conflates plain impact with the code-impact pipeline. The fresh
  answer identified and demonstrated both behaviors rather than repeating the
  expected status labels without qualification.
- The vocabulary's intended deleted-code exception is narrower than actual
  _dependents behavior: evaluation records and necessary links other than
  depends_on can also produce unjustified. This was verified against code.
  Added an explicit implementation-limit note to docs/reasoning-vocabulary.md;
  did not change the frozen question, vocabulary, propagation code or purpose files.

## Implementer grading against code

10/10 specific, correct answers. The command qualification in answer 6 is correct,
not a documentation-failure answer. This exceeds SC-003's 9/10 gate. The grader
was the implementer; external Claude technical review and Kate purpose review
remain pending, and this observation does not replace them. The check also found
a real documentation/implementation discrepancy; the added note reports it.
