# Getting started

This guide takes you from nothing to a `stale` report on your own code, then covers the extra steps for
repositories that already have Codex++ purpose files. For what the results mean, see the
[README](../../README.md#what-the-results-mean).

## Install

```bash
pip install "git+https://github.com/eraevous/Telosmith.git@main"   # 0.5.0 on main; tag v0.5.0 pending
aec --version
```

Python 3.10 or newer; no other dependencies. From a clone, `pip install -e .` works too, as does
`PYTHONPATH=src python3 -m aec …`, which is what the reference docs use.

## Your first `stale` report

```bash
cd your-project
aec init . --owner "Your Name"          # creates .aec/: records, an edge snapshot, CI/hook snippets (when there is Python code)
# or state the purpose now, citing where it is written:
#   aec init . --owner "Your Name" --purpose "What this is for" --purpose-anchor "README.md#q:what it is for"
```

Find the name Telosmith uses for a function you care about. Names come from the snapshot and include any
source-root folder, for example `src.mypkg.pricing.apply_discount` in a `src/` layout:

```bash
grep '"defines"' .aec/edges.jsonl | grep apply_discount
```

Append a requirement that points at it, and a claim that rests on the requirement, to
`.aec/records.jsonl`. One JSON object per line; links go in `relations`:

```json
{"id": "R-1", "version": 1, "type": "requirement", "subject": "code", "epistemic": "committed", "text": "Discounts never make a price negative.", "relations": [{"rel": "implemented_by", "to": "code:src.mypkg.pricing.apply_discount"}]}
{"id": "C-1", "version": 1, "type": "claim", "tier": "candidate", "text": "Checkout totals are never negative.", "relations": [{"rel": "depends_on", "to": "R-1@1"}]}
```

Or let `aec append` add them: it refuses an `id@version` that already exists or a record `check` would reject,
and computes anchors for you (`--anchor PATH#LOCATOR` hashes the file and checks the locator):

```bash
aec append .aec/records.jsonl '{"id": "R-1", "version": 1, "type": "requirement", "subject": "code", "epistemic": "committed", "text": "Discounts never make a price negative.", "relations": [{"rel": "implemented_by", "to": "code:src.mypkg.pricing.apply_discount"}]}' --anchor "docs/pricing.md#q:never negative"
```

```bash
aec check .aec/records.jsonl --edges .aec/edges.jsonl   # both references resolve? (suggests near misses)
cp .aec/edges.jsonl .aec/before.jsonl                   # keep the "before" snapshot
# ...edit apply_discount...
aec edges . -o .aec/edges.jsonl                          # the "after" snapshot
aec code-impact .aec/records.jsonl .aec/before.jsonl .aec/edges.jsonl
```

`code-impact` marks `R-1@1` as `stale` (the code it rests on changed) and `C-1@1` as
`needs_review` (it rests on something stale). Both mean: look at this again. Edits to code no record points at report nothing. Records are append-only: to change
one, append the same `id` with `"version": 2`. A claim or requirement that still points at the old version
(`C-1@1` depends on `R-1@1` after `R-1@2` exists) gets a `superseded-reference` warning from `check`, and when a change
reaches `R-1@2`, `code-impact` names it in a `structural: C-1@1 references superseded R-1@1` pointer
instead of giving it a status: append a version of it that references `R-1@2` if that is what you mean.
Evidence and decisions are not flagged: they record what existed when they were made.
When a linked function moves to another module, `check` reports the dangling reference and suggests
the same name elsewhere (up to three). The full vocabulary of types and relations is in
[`docs/reasoning-vocabulary.md`](../../docs/reasoning-vocabulary.md).

`.aec/edges.jsonl` is generated, and `aec init` git-ignores it: committed copies conflict on every pair
of pull requests that touch code. To compare a branch against `main` without a saved copy, build
the baseline from a worktree:

```bash
git worktree add /tmp/aec-base main && aec edges /tmp/aec-base -o .aec/before.jsonl && git worktree remove /tmp/aec-base
```

## Getting the report to someone

`code-impact` reports nothing unless it runs. The snippets `aec init` writes run it for you once copied into place:

- **Claude Code hook** (`.aec/snippets/claude-settings.json`): after each edit it refreshes the snapshot, fails on
  record errors, then compares the working tree with `HEAD` (snapshotted to `.aec/hook-before.jsonl`, so your own
  `.aec/before.jsonl` is left alone). When linked code changed, or reaches a change, the report goes to the agent
  (stderr, exit 2). Nothing is printed otherwise. It runs the `aec` installed in your environment, which needs
  `code-impact --exit-code`: a release >= v0.5.0 or a commit pin (v0.4.1 lacks it; the hook says so).
- **CI job** (`.aec/snippets/aec-ci.yml`): compares the merge-base with the checkout and writes the report to the
  job summary on the run page. It never fails the job and posts no pull-request comment. It installs the commit
  `aec init` was installed from when known (a git install, or the `HEAD` of a source checkout run with
  `PYTHONPATH=src` or installed editable, with a note: push that commit), a release >= v0.5.0, or else `@main`
  under a `WARNING: UNPINNED` comment: replace that with a commit you have reviewed.

A link to a module covers every definition in it; a link to a function covers its body, and changes one step
away (a helper it calls, a constant it reads) appear as `structural: ... reaches changed ...` pointers. A
pointer is a candidate for attention, not a required reassessment, and changes no record's status.
`--reach-depth N` widens the walk. When a changed definition sits exactly one step beyond it from a linked
symbol, the report adds `[note] reach depth 1; N changed symbols at depth 2 not reported`, so a quiet report
says what it stopped short of; edits nothing links to still report nothing. The note is not a finding: the
hook stays quiet on it. See [`docs/evaluations/code-impact-qual-001.md`](../evaluations/code-impact-qual-001.md).

## Repositories that already use Codex++ purpose files

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
