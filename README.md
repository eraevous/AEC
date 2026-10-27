# AEC

AEC (formerly Codex++) is an experiment in keeping **why** something is being built attached to **what** gets built, when AI agents do much of the building. It is meant as an extension to specification-driven development (GitHub Spec Kit), not a replacement for it. Spec Kit owns specs, plans, tasks and its own consistency checks. AEC adds explicit purpose, authority by subject, evidence status, and versioned criteria, and connects them.

See the white paper, *AEC as an extension to specification-driven development* (Zachary Rhodes, 26 October 2026), for the positioning, evidence and validation plan.

## What is here

| Part | Status |
|---|---|
| Repo conventions: `.purpose.md`, `.intent.md`, `AGENTS.md`, `CHARTER.md`, Run/Drift | from Codex++ (2025). Piloted in eraevous/MtG |
| `docs/reasoning-vocabulary.md` | v0 vocabulary for the work and its justification: purpose, requirement, criterion, assumption, source, claim, evidence, evaluation, decision, authority, revision |
| `src/aec/` (`python -m aec …`) | **v0.3.** `check`, `impact`, `edges`, `code-impact`, `init`, `import-purpose`. Standard library only |
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
- `contested`: new evidence contradicts it (change kind `add`).
- `needs_review`: it sits downstream of a broken, stale or contested conclusion, or it is a decision whose basis changed.

These are review dispositions, not truth values. Decisions are never declared unjustified by the tool. They belong to a human authority, so they are flagged for review.

On the MtG pilot, the six scenarios reproduce what the reviewers concluded by hand that day:
- Kate's catch on Duty Beyond Death's timing breaks the "recovery improved" claim. It leaves the receiver hypothesis alone, and flags the Vraska decision for review.
- Downgrading the receiver census only weakens the hypothesis, because Zach's observed game account still supports it.
- The P-01 amendment is `stale` and reported until Zach authorizes it, and `rebaseline` once he does.
- Rewording the provisional success criterion is `exploratory`.
- An unrelated inventory change flags nothing.

## The bedrock: code edges (v0.2)

```bash
PYTHONPATH=src python3 -m aec edges . -o .aec/edges.jsonl          # what defines/calls/imports/inherits/refers to what
PYTHONPATH=src python3 -m aec edges --diff old.jsonl .aec/edges.jsonl   # what changed structurally
PYTHONPATH=src python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl   # dangling code: references
PYTHONPATH=src python3 -m aec code-impact .aec/records.jsonl old.jsonl .aec/edges.jsonl  # which conclusions a code change affects
```

- **Deterministic and stdlib-only**, fast enough to run after every edit: Data-Guide (32 files) takes about 0.2 s. It runs automatically through `.claude/settings.json` (PostToolUse) and in CI.
- Records point at code with `code:<dotted.symbol>` (for example `implemented_by`). A changed symbol makes the conclusions resting on it `stale`. A deleted one makes them `unjustified` (decisions are only flagged). Evidence `observed_on` changed code needs an applicability review and is never invalidated. A code dependency is not a justificatory dependency: see the invariant in `docs/reasoning-vocabulary.md`.
- Dynamic calls are kept as unresolved `?expr` targets and never guessed. On Data-Guide about half of all calls are unresolved (methods on local objects). They never trigger impact by themselves.
- It replaces the 2025 `src/core/tools/ast_dependency_extractor.py` (pandas and typer, calls only, methods lost their class). `--legacy-csv` writes the old format for comparison. See `docs/data-guide-trial.md`.

## Adopting AEC in an existing repo (v0.3)

```bash
python3 -m aec init . --owner "Your Name"     # .aec/: records with an authority + provisional purpose stub,
                                               # the first edge snapshot, hook and CI snippets (never overwrites)
python3 -m aec import-purpose .               # Codex++ .purpose.md files -> provisional records (append-only)
python3 -m aec check .aec/records.jsonl --edges .aec/edges.jsonl
```

- `init` works with or without Spec Kit, and never edits Spec Kit files; with `.specify/` present it prints the extension command.
- `import-purpose` records what each purpose file **claimed**: a `source` record (path, sha256, the file's own `@ai-generated`/`@ai-verified`) and a provisional, candidate-tier claim with the declared text verbatim, linked to the module only when the named file resolves unambiguously. It never creates an authority. It reports, and never corrects: missing or ambiguous source files, non-code sources, templates (skipped), and **declared vs observed callers** (`@ai-used-by` against what actually imports or calls the module). Re-running it appends nothing unless a file changed, which gives version 2.
- On Data-Guide: 26 purpose files imported in about 0.6 s with init; 11 of the purpose files' source files no longer exist, and the declared callers of `data_profiler` (four pipeline modules) are all gone while three real callers are undeclared. See `docs/data-guide-trial.md`.
- Code run with `src/` on `sys.path` (`from data_profiler import …` for `src/data_profiler.py`) is now resolved to the real module; the snapshot header lists the `source_roots` it used. Stdlib names are never aliased.

## Spec Kit extension

`extension/` packages AEC for Spec Kit ≥ 1.2.0 (tested on v1.2.3): optional, report-only hooks after specify, tasks and implement. Install with `specify extension add --dev <AEC>/extension`. This repo is itself built with Spec Kit; see `specs/001-ast-bedrock-extension/` and the build log `docs/speckit-log.md`.

## What this does not show (yet)

- **Not a comparison.** Nothing here has been run against a properly configured Spec Kit baseline. The white paper's validation plan has to do that: same information, held-out fixtures, independent labels, false alarms and authoring cost counted.
- **The encoding is mostly hand-made.** `import-purpose` seeds records from existing purpose files, but purposes, evidence and decisions are still written by people. Authoring cost is logged per feature in `docs/speckit-log.md` but not yet compared with a baseline.
- **The pilot scenarios were encoded after the fact,** by the same session that wrote the tool. They show the semantics work as intended. They do not show detection of problems nobody had already found.
- **The extension is tested for install and remove only.** The hooks' agent-executed behavior (report, don't edit) is stated in each command but can't be unit-tested.

## Principles (unchanged)

The repo carries its own purpose, decisions and objections, so agents can act as collaborators that notice drift rather than as autocomplete. If ordinary Spec Kit artifacts perform as well, the right result is to simplify AEC.
