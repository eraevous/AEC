# AEC

AEC (formerly Codex++) explores continuous architectural reasoning for AI-assisted development: helping an AI development system understand what it is building, observe what it is becoming, detect when those diverge, and preserve the reasoning needed for deliberate change. It connects executable structure, semantic purpose, evidence, authority and agent coordination. The current implementation provides structural analysis and reasoning records, with a Spec Kit integration. Spec Kit is one integration surface, not the boundary of AEC; the capability table below distinguishes what is built, partial and planned.

The white paper, *AEC as an extension to specification-driven development* (Zachary Rhodes, 26 October 2026), records the earlier positioning, evidence and validation plan. The approved direction is described in `docs/architecture.md`.

## Authority and operating rules

`.aec/records.jsonl` governs purpose and authority (`AEC-P0@1`, `AU-zach@1`).
The engineering principles live in `.specify/memory/constitution.md`, applied by
`CHARTER.md`; `AGENTS.md` governs agent behavior. When a project uses Spec Kit,
Spec Kit owns its specification workflow. Purpose files in `codex_++/purpose_files/` are semantic contracts whose
claims are candidates, and `codex_++/intents/` contains provisional reasoning.
Generated edges are static structural facts, not a competing authority. If a
purpose file disagrees with a committed record, report the conflict for review;
the file cannot silently revise the record. Only Zach or an explicitly authorized
decision-maker for that subject may accept a commitment.

## Current capabilities and direction

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

See `docs/architecture.md` for the direction **approved by Zach on 29 October 2026**,
and `docs/failure-modes.md` for evaluation design. WP1–WP5 are approved as direction;
each still needs its own spec and PR. Approval does not establish that planned
features are built or that AEC improves owner outcomes. A passing record check
establishes formal consistency only, not the truth, adequacy or independence of
evidence. Reconstructed history remains proposed in `docs/decisions-to-confirm.md`.
Runtime dependencies: none beyond Python 3.10+; the legacy extractor is not shipped.

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
- Records point at code with `code:<dotted.symbol>` (for example `implemented_by`). A changed symbol makes the conclusions resting on it `stale`. A deleted one makes claims that `depends_on` it `unjustified`; requirements and purposes only lose their recorded satisfaction (`needs_review` plus a finding), and decisions are only flagged. Evidence `observed_on` changed code needs an applicability review and is never invalidated. A code dependency is not a justificatory dependency: see the invariant in `docs/reasoning-vocabulary.md`.
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
- `import-purpose` records what each purpose file **claimed**: a `source` record (path, sha256, the file's own `@ai-generated`/`@ai-verified`) and a provisional, candidate-tier claim with the declared text verbatim, linked to the module only when the named file resolves unambiguously. Singular and plural source headers are supported; structured IO, risk, dependency, integration and guarantee sections are kept, along with all raw fields/sections and the full untruncated source text. It never creates an authority. It reports, and never corrects: missing or ambiguous source files, non-code sources, templates (skipped), and **declared vs observed callers** (`@ai-used-by` against what actually imports or calls the module). Re-running it appends nothing unless a file changed, which gives version 2.
- On Data-Guide: 26 purpose files imported in about 0.6 s with init; 11 of the purpose files' source files no longer exist, and the declared callers of `data_profiler` (four pipeline modules) are all gone while three real callers are undeclared. See `docs/data-guide-trial.md`.
- Code run with `src/` on `sys.path` (`from data_profiler import …` for Data-Guide:src/data_profiler.py) is now resolved to the real module; the snapshot header lists the `source_roots` it used. Stdlib names are never aliased.

## Source anchors and offline retrieval (WP-S)

Records may carry optional `rationale` text separately from `text`, and an
`anchors` array on any record type. An anchor observes source integrity and locator
resolution only. It does not establish whether a passage justifies a conclusion,
what it means, or who may accept a decision. Existing records are never rewritten:
append a new version to add an anchor. `impact` and propagation are unchanged.

```json
{"id":"C-example","version":1,"type":"claim","text":"A conclusion","rationale":"A separate reason","anchors":[{"root":"corpus","path":"notes.md","sha256":"<64 hexadecimal characters>","locator":"L12-15","for":"rationale"}]}
```

The SHA-256 is computed on the file's **raw bytes**, without newline, encoding or
other normalization. Uppercase hex is accepted. `L12-15` is 1-based and inclusive;
`L12` selects one line. `q:exact text` selects the first exact occurrence within
one line. `for` defaults to `text`, or may be `rationale`; neither changes the
meaning/status of the record. Malformed digests, locators, anchor shapes or fields
are record errors. Relative anchor paths cannot contain parent traversal or escape
the root. Omit `root` to anchor a file relative to the repository.

Configure named local roots in .aec/sources.json (an optional machine-local file):

```json
{"roots":{"corpus":"../source-notes"}}
```

Root paths may be repo-relative or absolute local paths; source contents stay in
place. No AEC source command writes source files, copies them into this repository,
executes them, or accesses the network. Sources can contain private information;
configuration/access is the caller's responsibility, not a power granted by a hash.
No remote/URL/UNC providers are supported.

```bash
PYTHONPATH=src python3 -m aec check .aec/records.jsonl
PYTHONPATH=src python3 -m aec source show C-example@1 --context 3 --max-lines 80
PYTHONPATH=src python3 -m aec source search 'a forgotten fact' --root corpus --max 20
PYTHONPATH=src python3 -m aec source search 'fact.*detail' --regex --root corpus
```

`check` prints each valid anchor's state. A `verified` anchor means matching raw
bytes and a resolving locator; it produces **no finding**. Other filesystem states
are warning findings and do not fail the command:

| State | Observation |
| --- | --- |
| verified | Artifact bytes and locator match |
| missing | No file in an available root; this says nothing about earlier existence |
| mismatch | Bytes differ; the earlier observation is not falsified, but applicability needs review |
| locator_invalid | Bytes match, but the range/quote does not resolve |
| unavailable | Root unconfigured/absent, file unreadable, or symlink escapes the read boundary; cannot check here |

Malformed records still fail `check`, as do its pre-existing errors. A digest
mismatch takes precedence over locator resolution; show may display a currently
resolving passage from changed bytes, with a warning. An unresolved locator has no
passage to display. Missing/unavailable sources never yield a passage.

`source show` labels record, zero-based anchor index, field, state, path and
locator. Context defaults to 3 lines; `--context` is nonnegative. `--max-lines`
defaults to 80 and must be positive: each passage, including context, is capped
and omitted lines are explicitly counted. UTF-8 replacement decoding is used only
for views, never for the digest; CRLF files keep the same logical line numbering.

`source search` scans named configured roots directly even if no record points at
the matching text or no default records file exists. Every matching line is
labelled `fallback`, with displayed path, line number, current raw-byte SHA-256 and
all record versions anchoring that file (even if their digests are stale). Literal
matching is default; `--regex` explicitly enables Python regular expressions.
Results sort by path then line, with root alias as a tie-breaker; repeated aliases
can produce separate hits. `--max` defaults to 20, is nonnegative, and reports the
count of matching lines omitted. Zero prints no hits and counts all omissions.

`--root` selects a configured alias. The implicit repository root is selected
explicitly with `--root .`; it is not scanned by default. Unknown aliases are
usage errors. Search never follows directory symlinks; in-root file symlinks are
readable, while escaping ones and unreadable paths get visibility notes. No
persistent index is created. Output bounds limit lines/hits, not input file size
or regex execution time; use basic fallback search on suitable local source roots.

Both source subcommands accept `--repo ROOT` (default current directory) and
`--records PATH` (default ROOT/.aec/records.jsonl; an explicit relative path uses
the current directory). `check --repo ROOT` overrides source configuration lookup;
otherwise records under .aec/ imply their repository parent, and other paths use
the current directory. Relative root configuration stays relative in displayed
paths. Invalid configuration, regexes, references or limits are usage errors.

## Spec Kit extension

`extension/` packages AEC for Spec Kit ≥ 1.2.0 (tested on v1.2.3): optional, report-only hooks after specify, tasks and implement. Install with `specify extension add --dev <AEC>/extension`. This repo is itself built with Spec Kit; see `specs/001-ast-bedrock-extension/` and the build log `docs/speckit-log.md`.

## What this does not show (yet)

- **Not a comparison.** Nothing here has been run against a properly configured Spec Kit baseline. The white paper's validation plan has to do that: same information, held-out fixtures, independent labels, false alarms and authoring cost counted.
- **The encoding is mostly hand-made.** `import-purpose` seeds records from existing purpose files, but purposes, evidence and decisions are still written by people. Authoring cost is logged per feature in `docs/speckit-log.md` but not yet compared with a baseline.
- **The pilot scenarios were encoded after the fact,** by the same session that wrote the tool. They show the semantics work as intended. They do not show detection of problems nobody had already found.
- **The extension is tested for install and remove only.** The hooks' agent-executed behavior (report, don't edit) is stated in each command but can't be unit-tested.

## Principles (unchanged)

The repo carries its own purpose, decisions and objections, so agents can act as collaborators that notice drift rather than as autocomplete. If ordinary Spec Kit artifacts perform as well, the right result is to simplify AEC.

## License

Licensed under the [MIT License](LICENSE). Contributions are welcome under the
[Contributor License Agreement](CLA.md), which keeps them open under the same license
while letting the maintainer also offer commercial versions. See
[CONTRIBUTING.md](CONTRIBUTING.md).
