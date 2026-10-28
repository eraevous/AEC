# AEC

AEC (formerly Codex++) is an experiment in keeping **why** something is being built attached to **what** gets built, when AI agents do much of the building. It is meant as an extension to specification-driven development (GitHub Spec Kit), not a replacement for it. Spec Kit owns specs, plans, tasks and its own consistency checks. AEC adds explicit purpose, authority by subject, evidence status, and versioned criteria, and connects them.

See the white paper, *AEC as an extension to specification-driven development* (Zachary Rhodes, 26 October 2026), for the positioning, evidence and validation plan.

## What is here

| Part | Status |
|---|---|
| Repo conventions: `.purpose.md`, `.intent.md`, `AGENTS.md`, `CHARTER.md`, Run/Drift | from Codex++ (2025). Piloted in eraevous/MtG |
| `docs/reasoning-vocabulary.md` | v0 vocabulary for the work and its justification: purpose, requirement, criterion, assumption, source, claim, evidence, evaluation, decision, authority, revision |
| `src/aec/` (`python -m aec check` / `impact`) | **new, v0.** Cross-record checks and change-impact analysis. Standard library only |
| `examples/mtg-pilot/` | real events from the MtG pilot (2026-10-26) encoded as records, plus six change scenarios |
| `src/core/tools/ast_dependency_extractor.py` | AST call-dependency extractor (2025) |

## The one capability v0 has to earn

> **Something changed. Which conclusions are no longer justified, and which changes were legitimate revisions?**

```bash
PYTHONPATH=src python3 -m aec check  examples/mtg-pilot/records.jsonl
PYTHONPATH=src python3 -m aec impact examples/mtg-pilot/records.jsonl examples/mtg-pilot/scenario1_duty_timing.jsonl
PYTHONPATH=src python3 -m unittest discover -s tests
```

Each conclusion that relied on the changed record is classified:
- `unjustified`: its support broke.
- `weakened`: it lost one support but keeps others.
- `stale`: it pins an old version after an unauthorized change.
- `rebaseline`: an authorized revision; re-examine it, but it is not drift.
- `exploratory`: the changed record was provisional, which is expected during purpose discovery.
- `needs_review`: it sits downstream of a broken or stale conclusion.

Decisions are never declared unjustified by the tool. They belong to a human authority, so they are flagged for review.

On the MtG pilot, the six scenarios reproduce what the reviewers concluded by hand that day:
- Kate's catch on Duty Beyond Death's timing breaks the "recovery improved" claim. It leaves the receiver hypothesis alone, and flags the Vraska decision for review.
- Downgrading the receiver census only weakens the hypothesis, because Zach's observed game account still supports it.
- The P-01 amendment is `stale` and reported until Zach authorizes it, and `rebaseline` once he does.
- Rewording the provisional success criterion is `exploratory`.
- An unrelated inventory change flags nothing.

## What this does not show (yet)

- **Not a comparison.** Nothing here has been run against a properly configured Spec Kit baseline. The white paper's validation plan has to do that: same information, held-out fixtures, independent labels, false alarms and authoring cost counted.
- **The encoding is hand-made.** Someone has to write the records. The authoring cost is unmeasured, and it may decide whether this is worth having.
- **The pilot scenarios were encoded after the fact,** by the same session that wrote the tool. They show the semantics work as intended. They do not show detection of problems nobody had already found.
- **Not a Spec Kit extension yet.** Packaging follows a pinned Spec Kit release and its extension schema.

## Principles (unchanged)

The repo carries its own purpose, decisions and objections, so agents can act as collaborators that notice drift rather than as autocomplete. If ordinary Spec Kit artifacts perform as well, the right result is to simplify AEC.
