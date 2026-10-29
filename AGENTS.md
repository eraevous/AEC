# AEC agent operating guide

AEC keeps the reasons for a change attached to the code and flags conclusions
whose recorded support changed. Deterministic results are **structural**; a
passing check does not establish semantic correctness or purpose achievement.
Read `README.md`, `.specify/memory/constitution.md`, and the feature's spec,
plan and tasks before implementing. No runtime dependencies beyond Python 3.10+.

## Which source governs which question

- `.aec/records.jsonl` governs purpose and authority: `AEC-P0@1` is the purpose;
  `AU-zach@1` governs AEC design intent and acceptance, by recorded subject.
- `.specify/memory/constitution.md` governs engineering principles; `CHARTER.md`
  states their practical application. A conflict goes to the constitution.
- `AGENTS.md` governs agent behavior. Spec Kit owns specs, plans, tasks and its
  workflow; an AEC report is a review item, never permission to rewrite them.
- `codex_++/purpose_files/` holds semantic contracts as **candidate claims**.
  They cannot override committed purpose or authority records. Report disagreement
  with records/code and propose reconciliation; do not silently choose a new goal.
- `codex_++/intents/` holds provisional reasoning, questions and assumptions.
- `.aec/edges.jsonl` contains generated static structural facts. Never hand-edit it
  or infer a justificatory dependency from an import/call edge alone.

Only Zach (or a decision-maker explicitly authorized for the relevant subject)
may accept scope/goal commitments. An accepted decision must name a governing
authority with `decided_by`; reconstructed decisions remain proposed. A typed
`authorized_by` is a claim, not verified consent. See `docs/reasoning-vocabulary.md`.

## Work cadence and boundaries

Run means implement authorized work, collect evidence and run checks. Drift means
review whether observed behavior still matches declared intent; record questions,
assumptions, tradeoffs and rework in an intent note. Today this is an agent practice,
not an automated trigger or command. Follow the current task; do not invent an
approval gate for ordinary reversible implementation choices. Stop on work outside
its authorization, and present the concrete conflict and a narrower alternative.

Use the standard library, a thin argparse CLI, deterministic ordering and plain
append-only records. Each new check/classifier needs a violating fixture and a
clean decoy, written before implementation. Never edit existing record lines,
accept a reconstructed decision, or treat a passing test as owner approval.
Purpose files change only in their authorized task scope; log discrepancies.

## Built commands

Run from the repository root with PYTHONPATH=src:

| Command | Function |
| --- | --- |
| `python -m aec check` | Check formal record invariants; optionally resolve code references against edges |
| `python -m aec impact` | Classify consequences of explicit record change events |
| `python -m aec edges` | Extract a Python AST snapshot or compare two snapshots |
| `python -m aec code-impact` | Derive code change events from snapshots and report affected conclusions |
| `python -m aec init` | Scaffold absent AEC files and snippets; never overwrite |
| `python -m aec import-purpose` | Import declared contracts as provisional, source-linked claims |

Use --help for required arguments. Record checks do not establish evidence quality
or semantic adequacy. AST calls through local objects/dynamic access can remain
unresolved; skipped/unparsed files and non-Python consumers are invisible.
No known caller is not proof of no caller. See `docs/data-guide-trial.md`.

## Checks (same commands as CI)

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m aec edges . -o .aec/edges.jsonl
PYTHONPATH=src python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl
PYTHONPATH=src python3 -m aec check examples/mtg-pilot/records.jsonl
```

CI is defined in `.github/workflows/ci.yml`. It also checks init/import on a
fixture copy. The extension install/remove test needs the pinned Spec Kit CLI
v1.2.3; it skips when that CLI is absent. The package-install test needs build
dependencies available to pip. See `docs/speckit-log.md` for setup and actual costs.

## Built, partial and planned

Built: the six commands above, structured purpose import, provenance-linked
candidate history and doc-truth checks. Partial: semantic reconciliation (declared
fields and caller comparisons only), evidence adequacy/applicability (narrow
rules only). Planned: commit-addressed snapshots, topology analytics, context
briefings, reconciliation packets, automatic drift triggers and handoff premise
checks. `docs/architecture.md` is proposed direction; `docs/failure-modes.md`
is evaluation design. Neither claims those planned mechanisms exist or authorizes
work beyond the current scope.

Legacy code remains out of the distributed package; its fate is an owner decision.
The inherited protocol is archived in `docs/history/codex-plus-plus-AGENTS.md`.
