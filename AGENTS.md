# Telosmith agent operating guide

Telosmith was called AEC until November 2026. The package, the `aec` command and the `.aec/` folder keep that name.

Telosmith keeps the reasons for a change attached to the code and flags conclusions
whose recorded support changed. Deterministic results are **structural**; a
passing check does not establish semantic correctness or purpose achievement.
Read `README.md`, `.specify/memory/constitution.md`, and the feature's spec,
plan and tasks before implementing. No runtime dependencies beyond Python 3.10+.

## Which source governs which question

- `.aec/records.jsonl` governs purpose and authority: `AEC-P0@3` is the purpose
  (the latest version; earlier versions stay in the history);
  `AU-zach@1` governs Telosmith design intent and acceptance, by recorded subject.
- `.specify/memory/constitution.md` governs engineering principles; `CHARTER.md`
  states their practical application. A conflict goes to the constitution.
- `AGENTS.md` governs agent behavior. When a project uses Spec Kit, Spec Kit owns
  specs, plans, tasks and its workflow; a Telosmith report is a review item, never
  permission to rewrite them.
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
Before opening a pull request or marking one ready, run `python3 tools/preflight.py` and open it only when
it passes. It runs what CI gates on (unit tests, record touch, the records check, the example and adoption
checks, plus ruff when installed); say in the PR body that it passed.

## Built commands

Run from the repository root with PYTHONPATH=src:

| Command | Function |
| --- | --- |
| `python -m aec check` | Check formal record invariants; optionally resolve code references against edges |
| `python -m aec impact` | Classify consequences of explicit record change events |
| `python -m aec edges` | Extract a Python AST snapshot or compare two snapshots |
| `python -m aec code-impact` | Derive code change events from snapshots and report affected conclusions |
| `python -m aec init` | Scaffold absent Telosmith files and snippets; never overwrite |
| `python -m aec import-purpose` | Import declared contracts as provisional, source-linked claims |
| `python -m aec source` | Show anchored passages or search local configured roots directly |
| `python -m aec snapshot` | Identify a working tree or local Git commit and extraction method |
| `python -m aec diff` | Compare merge-base/head with one method or guarded stored snapshots |
| `python -m aec reach` | Query known structural reach in one projection with visibility |
| `python -m aec fan` | Count per-projection neighbors with visibility |
| `python -m aec unresolved` | Retrieve unresolved calls by why and file/symbol region |
| `python -m aec anchor` | Print a checked anchor (sha256 + locator) for a passage, as JSON |
| `python -m aec append` | Append one record, computing its anchors |

Source check/show/search are offline and read-only. Anchors/rationale live in
Record.data. Filesystem anchor states are warnings; malformed anchor shapes are
errors. Integrity and locator matches do not establish meaning or consent. See
`specs/004-source-anchors/`, `specs/006-ledger-hygiene/` (append-only files: state `appended`)
and `docs/reference/source-anchors.md` for root/limit details. A byte-identical duplicate record
line is a warning, not an error (`docs/reference/records-hygiene.md`).

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

Built: the fourteen commands above (the five WP1A commands, `anchor` and `append` first released in 0.5.0), offline source integrity/retrieval, structured purpose import, provenance-linked
candidate history and doc-truth checks. Partial: semantic reconciliation (declared
fields and caller comparisons only), evidence adequacy/applicability (narrow
rules only). Planned: WP1B topology/history analytics, context
briefings, reconciliation packets, automatic drift triggers and handoff premise
checks. `docs/architecture.md` records direction approved by Zach on 29 October
2026; `docs/failure-modes.md` is evaluation design. WP1–WP5 are approved as direction,
but each still requires its own spec and PR. Approval does not mean planned
mechanisms exist or authorize work beyond the current scope.

Legacy code remains out of the distributed package; its fate is an owner decision.
The inherited protocol is archived in `docs/history/codex-plus-plus-AGENTS.md`.
