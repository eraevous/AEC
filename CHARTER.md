# AEC engineering charter

The governing engineering principles are in `.specify/memory/constitution.md`.
This charter applies them; it creates no competing purpose or authority.
`.aec/records.jsonl` governs those questions (`AEC-P0@1`, `AU-zach@1`).

1. **Standard library runtime, Python 3.10+.** The shipped package is `src/aec/`;
   legacy `src/core/` is excluded. Keep the argparse CLI thin; pure workflow
   functions belong in the AEC modules. No new service without an owner decision.
2. **Deterministic and inspectable.** Stable ordering, plain JSON lines and explicit
   provenance. Code topology comes from static code analysis, never model prose.
   Never manually edit generated edges or equate code and justificatory relations.
3. **Report only.** Findings are structural review dispositions, not semantic
   verdicts, invalidation of human decisions, or permission to change commitments.
   Init writes absent scaffolding; import/reconstruction append their own records
   on request. They never silently fix contracts or overwrite existing records.
4. **Append-only records.** Existing lines stay intact. Revisions append versions
   and explicit relations. Source-linked reconstructed decisions remain proposed;
   only a governing authority may accept commitments. Recorded authorization is
   still a claim requiring evidence, not verified consent.
5. **Tests before checks.** Each new check/classifier gets a violating fixture and
   a clean decoy. Run the unit suite, regenerate edges and run record checks as
   documented in `AGENTS.md` and `.github/workflows/ci.yml`.
6. **Earn additions.** Record authoring/maintenance cost and what Spec Kit actually
   caught in `docs/speckit-log.md`. No purpose-preservation or comparative-benefit
   claim follows from a passing structural check. Keep implementation assumptions,
   ambiguities and rework in `codex_++/intents/`.

Run and Drift are the agent practices described in `AGENTS.md`; automation remains
planned. Purpose files are candidate semantic contracts, not engineering policy.
The historical Cognitive-Scaffolding rules are archived in
`docs/history/codex-plus-plus-AGENTS.md`, not requirements for AEC.
