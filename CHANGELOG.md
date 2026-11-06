# Changelog

All notable changes to Telosmith (formerly AEC). Versions follow [semantic versioning](https://semver.org/); before
1.0, a minor version may change command output or record fields (see "Stability" in README).

## [Unreleased]

### Records
- Telosmith's own purpose is now `AEC-P0@3` (Kate's wording, anchored to DEC-116); the requirements that served
  `AEC-P0@1` were re-pinned to it, and AGENTS.md names it. Earlier versions stay in the history.

### Added
- Optional record fields `authored_by` (an actor such as `claude:aec`) and `author_role` (`owner`, `independent`,
  `implementer`), shape-checked by `check`, for testing whether independently written records catch more drift.

### Changed
- `check` output: a finding whose verdict turns on a threshold ends with `[threshold: ...; measured: ...]`
  (observed and prospective tiers, outcome sufficiency, superseded references). The rest of the line is unchanged;
  findings with no threshold look as before.

### Added (development)
- `tools/preflight.py` runs locally what CI gates on (unit tests, record touch, the records check, example and
  adoption checks, ruff when installed) and summarises; AGENTS.md asks agents to pass it before opening or marking a
  pull request ready.
### Documentation
- `docs/enforcement-audit.md`: for each rule in AGENTS.md, the mechanism that enforces it (test, CI step, hook,
  `check`) or a label (partial, procedural, advisory), with five gaps listed for a decision. No rule changes.
- `docs/review-vocabulary.md`: five names reviewers tag findings with (ghost-tool, reflexive-fabrication,
  metaphor-literal-swap, simulated-precision, clean-lie), with no scores, used only on PRs that touch a contract, a
  check or authority.
- Rule 7 in `docs/reasoning-vocabulary.md`: authority does not compose; an authority record that cites another gains
  none of its scope. Already true of `check` and `impact`; `tests/test_no_transitive_authority.py` pins it.
- `docs/gates.md`: a register of every state transition and pass/fail point (evaluator, threshold, what it
  protects, reversibility), with four findings it surfaced, among them that a committed record can be changed by a
  plain append without `check` noticing (F1). Nothing in the code changes.

### Added (adoption friction from the DEC-095 pilots, 2026-11-05)
- `aec init --purpose TEXT` writes the purpose `P0@1` with your text instead of the TODO stub (still
  provisional), and `--purpose-anchor PATH#LOCATOR` cites a file in the repository for it: hashed and checked
  when init runs, and nothing is written if it does not resolve.
- `aec init` writes the Claude Code hook and CI snippets only when the repository has Python code (code-impact
  has nothing to report otherwise) and says so; `--hooks` writes them anyway, `--no-hooks` skips them.
- `aec append RECORDS JSON|-` appends one record and computes its anchors: `--anchor` / `--rationale-anchor`
  `[ALIAS=]PATH#LOCATOR` hash the file, check the locator resolves, and add `prefix_bytes` for files declared
  append-only. It refuses (exit 1, nothing written) an `id@version` that exists or a record that adds a `check`
  error; it never edits a line and repairs a missing final newline instead of joining lines.
- `aec anchor [ALIAS=]PATH#LOCATOR [--rationale]` prints a checked anchor as JSON, for records written by hand.
- `aec init --ci-name NAME` names the CI workflow, its job and its file (`.aec/snippets/NAME-ci.yml`, to copy to
  `.github/workflows/NAME.yml`); the default stays `aec`.
- docs/reference/source-anchors.md: in a repository others clone, cite an outside decision (such as a private
  ledger) as text only, not as a hashed anchor.

### Changed (lifecycle gaps from a docs builder's no-Spec-Kit run, 2026-11-04)
- `check` warns `superseded-reference` when the latest version of a record references an older version of
  another record (`C-1@1` depends on `R-1@1` while `R-1@2` exists). A warning, never an error: the old
  version may be meant. `supersedes`, references to a record's own id and superseded referrers are not judged,
  nor are evidence and decisions: they are history by nature, pinned to the version that existed when they
  were observed or made.
- `code-impact` reports such a record as a pointer when the change reaches the newer version
  (`structural: C-1@1 references superseded R-1@1; R-1@2 changed (stale); no status change`; evidence and
  decisions excepted). Before, the
  change reached `R-1@2` and stopped. The summary's pointer count now counts every `structural:` line.
- `code-impact` adds `[note] reach depth 1; N changed symbols at depth 2 not reported (use --reach-depth 2)`
  above the summary when a changed definition is exactly one step beyond the walk from a linked symbol whose
  records are not already classified (edits nothing links to still report nothing); JSON output has a
  `notes` list. The default depth (1) is unchanged, and the note is not a finding (`--exit-code` ignores it).
- A dangling `code:` reference also suggests symbols with the same last name in other modules (a moved
  function): one if unique, up to three if ambiguous (module-level definitions before methods), with a count
  of the rest. Existing near-miss
  suggestions come first and are unchanged.
- `init` run from a Telosmith source checkout (`PYTHONPATH=src` or an editable install; the checkout's
  `pyproject.toml` must name `telosmith`) pins the generated CI job to
  the checkout's `HEAD` commit and prints a note, instead of `@v0.5.0`, which may not exist yet. Git installs
  still pin their recorded commit and other installs still pin the version's tag (#51).

## [0.5.0] - 2026-11-04

Summary of what 0.5.0 adds over 0.4.1 (details in the sections below, from PRs #31 to #51):
- The `telosmith` command (same CLI as `aec`, which stays the primary name in the docs) and the
  `telosmith` distribution name (#39, #40).
- WP1A commands: `snapshot`, `diff`, `reach`, `fan`, `unresolved` (#31).
- `code-impact` covers module links, reports one-hop `reaches changed` pointers (`--reach-depth`), and has
  `--exit-code`; the hook and CI job `init` generates run it (#51).
- Ledger hygiene: `appended` anchor state for append-only files, duplicate-line warning (#48); the relay-kit
  records location setting (#49); record types `ambition` and `experiment` (#37); the `implements`
  deprecation warning and standard-terms vocabulary (#38); extractor resolution of local constructor
  calls (#32); review-integrity fixes (#33).
- Project-internal: review protocol (#34), value map (#36), golden-master harness, ruff, CLI handler split and
  named check rule families (#41 to #44, #46), decisions/owner report experiments (#45, #47).

### Upgrading from 0.4.1
- Regenerate any stored snapshot (for example `.aec/before.jsonl`) after upgrading. A 0.4.1 snapshot
  (extractor tool_version 0.3.0) compared with a 0.5.0 one stops with `method mismatch: legacy/unknown
  method` (checked 2026-11-04). Rebuild the baseline with `aec edges` (or `aec snapshot --rev`) at the
  older commit.

### Changed (release readiness, from a cold-install report on 2026-11-04)
- Version 0.5.0 in `pyproject.toml`, `aec.__version__` and `--version`, so `main` is distinguishable from
  v0.4.1. With no commit known, the CI job `init` generates now pins `@v0.5.0`.
- `check` warns (`evidence-text`) on an evidence record with no or blank `text`: before, it passed and
  reports printed an empty line such as `[needs_review] E-1@1: `. A warning, not an error. Only the latest version
  of an id is judged (appending a version with text clears it), unless a latest record still points at the
  textless version.
- `init` writes "Telosmith records" (not "AEC records") as the header of `records.jsonl`, and its README
  stub and Spec Kit hint use the new name. Record ids, types and the `.aec/` folder are unchanged.
- README, getting-started and the demo install `@main` marked "tag v0.5.0 pending" until the tag exists
  (`docs/RELEASING.md` lists the flip); README's stability section describes 0.5.0.
- `docs/demo.md`: a short end-to-end demo on a toy project, with real output.


### Changed (code-impact coverage and delivery, HO-RK-20261104-DN2X)
- A link to a module (`code:pkg.mod`, what `import-purpose` writes) is now revised when any definition or
  statement in that module changes, as a class link is when a method changes. Before, a module link was only
  retracted when the module was deleted, so it passed `check` but never reported an edit. A package link does
  not cover its submodules.
- `code-impact` reports changed definitions one resolved call or reference away from a linked symbol (a helper,
  a constant) as `structural: ... reaches changed ...` pointers. They assign no status: what a link means is
  unchanged. `--reach-depth N` widens them, `0` turns them off; pointers to records the report already flags
  are dropped.
- `code-impact --exit-code` exits 1 when anything is affected or reported (for hooks).
- The hook and CI job `aec init` generates now run `code-impact`: the hook against `HEAD` after each edit,
  reporting to the agent (exit 2) only when something linked moved; the CI job against the merge-base, into
  the job summary, never failing the job. Telosmith's own CI runs the same step on pull requests.
- Evaluation: `docs/evaluations/code-impact-qual-001.md`, a cheap coverage/delivery qualification, not a value win.
- Fix round (DEC-038 reviews of PR #51). **Delivery to other repositories needs a release >= 0.5 or a commit
  pin:** v0.4.1, the last tag, has no `aec snapshot`, no `code-impact --exit-code` and none of the above.
  `aec init` now pins the generated CI job to the commit it was installed from when it can tell, else to its
  release tag when >= v0.5.0, else to `@main` under a `WARNING: UNPINNED` comment (never v0.4.1). The hook reports
  to the user (exit 1) when the installed `aec` lacks `--exit-code`, and keeps HEAD's snapshot in
  `.aec/hook-before.jsonl` (git-ignored) instead of overwriting the user's `.aec/before.jsonl`. Pointer lines,
  the summary line (`N conclusions with no status change`, no longer "unaffected") and the hook's message call
  pointers candidates for attention that change no status. A negative `--reach-depth` is an error.
### Added (spec 006, ledger hygiene; authorized by Zach 2026-11-04, C-09 and C-21)
- Anchors into append-only files. An anchor may carry `prefix_bytes` (the file length when anchored):
  its `sha256` then covers only those leading bytes. `.aec/sources.json` may declare `append_only` files
  per root; whole-file anchors into them also match a newline-ended prefix. A new anchor state,
  `appended`, means the file grew and begins with exactly the anchored bytes; it is printed distinctly
  by `check` and `source show` and is not a finding. Whole-file digests stay the default: an undeclared
  grown file is still `mismatch`. Telosmith's own records declare relay-kit-private's
  `governance/decisions.jsonl`, and their anchor warnings drop from 13 to the 3 real mismatches.
- `check` reads a byte-identical duplicate record line (left by merging two branches that appended the
  same record) as one record, with a `duplicate-line` warning naming both lines, instead of failing with
  `unique`. Any difference between the lines is still the `unique` error. No command rewrites records;
  `docs/reference/records-hygiene.md` gives the manual clean-up, which is the owner's call.
- Fix round (DEC-038 reviews of PR #48): duplicate lines are compared as written, so a copy differing
  only in surrounding whitespace or CRLF is the `unique` error, not the warning; an anchor whose
  `prefix_bytes` ends mid-line is `mismatch` once the file grows (appended bytes would extend that line);
  the `appended` note says a later entry may supersede the anchored one; `append_only` is per root alias.
### Added (relay-kit records location, HO-RK-20261103-5J0W)
- Where Telosmith finds the owner's relay-kit records is a setting. `records_root` in `.aec/sources.json`
  names the alias (default `records`); `$RELAYKIT_RECORDS`, the variable relay-kit's tools read, overrides
  that root's path over the configured one. Unset, absent or unusable locations leave its anchors
  `unavailable`, as before. This repository keeps Zach's sibling `../relay-kit-private` as its default.
- `docs/integrations/relay-kit.md`: install relay-kit pinned to commit `a7fa03a` (0.1.0; `@v0.1.0` once
  the tag exists) and configure the records location. `docs/architecture.md` describes the decision
  record as the owner's relay-kit records, with relay-kit-private as Zach's instance.

### Changed (name)
- **AEC is now Telosmith** (Zach, 2026-11-02; DEC-036). The distribution is `telosmith`: `aec` and `each`
  are taken on PyPI by unrelated packages, and "AEC" was never expanded and reads as architecture,
  engineering and construction. The `telosmith` command is added. The `aec` command, the Python
  package `aec` and the `.aec/` folder keep working as before.
- The CI job `init` generates installs by URL alone (no `aec @`), so it works across the rename.
- The README and contributor docs use the new name. Their examples keep `aec` until a release ships
  `telosmith`.

### Changed (naming)
- `check` warns on the relation `implements` (deprecated): it duplicated `implemented_by` in reverse,
  and `impact` never propagated through it. Use `implemented_by` on the requirement.
- `docs/reasoning-vocabulary.md` maps each AEC term to the established one (requirements traceability,
  ADRs, configuration management, event sourcing, change impact analysis), and says where AEC differs.
- `aec edges --help` calls its output the dependency graph, as `snapshot` does.
### Added (vocabulary, DEC-033)
- Record types `ambition` (a direction the project or a derived project may take, kept visible so
  commitments don't foreclose it; not a commitment) and `experiment` (trying a few things; results can
  be promoted, the experiment needn't be supported). Neither is reported by `impact`. AEC's own records
  gain its first two ambitions.

### Added (WP1A, commit-addressed snapshots)

- Commit/working-tree snapshots with extractor tool_version 0.4.0 and method identity.
- Symmetric merge-base/head structural diffs, guarded stored comparisons and CI artifact.
- Projection-specific reach/fan and unresolved-call retrieval by five reason kinds, with visibility.
- File/directory boundaries and conservative class/public-surface indicators.

### Changed
- The extractor (tool_version 0.4.1) resolves `x.m()` when `x` is a function local whose only
  possible value is `C(...)` for a class defined in the analysed tree, like `self.m()`. Any local that
  could hold something else stays unresolved. Found by probe-001 (its most consequential caller was
  missed this way); measured in `docs/evaluations/resolver-001.md`: 25 of Data-Guide's 874 unresolved
  calls resolve, all correct by hand check; five edge cases found by GitHub Copilot's review are excluded. Snapshots from extractor 0.4.0 and 0.4.1 are not comparable.

### Fixed (from GitHub Copilot's repository review, 2026-11-01)
- `check` no longer coerces a non-integer `version` (`1.9` loaded as version 1, a different
  `id@version`). Such a record is an error and isn't loaded.
- `check` requires `frozen_sha256` on a prospective claim to be a SHA-256 digest, not any non-empty value.
- The extractor reports `foo.py` as shadowed when a package `foo/` exists. Before, one file's calls
  disappeared without a trace.
- `aec edges` stops if a file changes between its two passes, instead of mixing two versions in one
  snapshot. Both passes now parse the exact bytes that were hashed.

## [0.4.1] - 2026-11-01

### Changed
- `aec init` writes `.aec/.gitignore` so the generated snapshot (`edges.jsonl`, and a `before.jsonl`
  baseline) is not committed. Committed snapshots made every pair of code-touching pull requests
  conflict. An existing `.aec/.gitignore` is never overwritten.
- AEC's own repository no longer tracks `.aec/edges.jsonl`; CI and the Claude hook regenerate it.
- README: how to build a baseline snapshot from a git worktree.
- The CI job `aec init` generates now pins `@v0.4.1`.
- AEC's own CI reports `aec code-impact` for each pull request (base to head, report only), so code
  that moves ahead of its records is visible in the PR. Found by the dogfood-001 audit.
- AEC's own records catch up with the day's changes: claims and evidence for `init` (AEC-R7) and
  `check` (AEC-R8), AEC-R10 re-anchored after the WP1A clarifications, and DEC-023 to DEC-025.
- Documentation reorganised for readers outside the project. The README is now an entry point
  (install, quickstart, what results mean, evidence and limitations). Technical depth moved to
  `docs/guide/`, `docs/reference/`, `docs/integrations/`, `docs/governance.md` and `docs/history/`.
  There is an evaluations index (`docs/evaluations/README.md`) and a second fresh-reader walkthrough.
- SECURITY.md no longer refers to private vulnerability reporting, which isn't enabled.
  CODE_OF_CONDUCT.md's own rules now govern. CONTRIBUTING.md clarifies who may tick the CLA box.

## [0.4.0] - 2026-11-01

First public release. `edges`, `impact` and `code-impact` compute the same results as before; `check` gains one warning (`relation-shape`) and near-miss hints.

### Added
- `aec` console command after `pip install`, and `aec --version`.
- One line of `--help` text for every subcommand.
- `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue templates, and a full `CONTRIBUTING.md`.
- `docs/release-readiness.md`: what "a release we can be proud of" means for AEC, as checks.
- `docs/evaluations/probe-001.md` and `probe-001-results.md`: the first outcome measurement, a pre-registered WP2-probe pilot (18 trials). Result: no signal, and briefings raised token cost on 2 of 3 tasks. All materials are published under `docs/evaluations/probe-001/`.
- CI runs the test suite on Python 3.10, 3.11, 3.12 and 3.13.
- A test that the package version, `aec.__version__` and this changelog agree.
- `check` suggests close matches for an unknown `code:` reference, including a missing source-root prefix such as `src.`.
- `docs/evaluations/walkthrough-001.md`: a clean-install, first-use walkthrough, and the README fixes it led to.
- `check` warns (`relation-shape`) when a relation name such as `implemented_by` is used as a top-level
  field. Such fields were silently unchecked; found while writing the README quickstart.

### Changed
- README now opens with the problem, a quickstart and what AEC is not; governance detail moved lower.
- `pyproject.toml` has a `[build-system]` table, project metadata and URLs.

## [0.3.x] - 2026-10-29 to 2026-10-31 (not tagged)

- Source anchors and offline retrieval: `aec source show` and `aec source search` (WP-S, spec 004, PR #17).
- AEC reconciled with itself: structured purpose import, source-linked reconstructed decisions, doc-truth checks (WP0, spec 003, PR #14).
- Extractor resolves imports under `src/` layouts; snapshots record their `source_roots` (found on the Data-Guide trial).
- Spec for commit-addressed snapshots (WP1A, spec 005, PR #18); not yet implemented.

## [0.2.0] - 2026-10-26 to 2026-10-28 (not tagged)

- Adoptable AEC: `aec init` and `aec import-purpose` (spec 002, PR #10).
- AEC as an installable Spec Kit extension (PR #9).
- AST edge snapshots as the structural bedrock, and `aec code-impact` (spec 001, PR #8).
- MIT licence and contributor licence agreement (PR #11).

## [0.1.0] - 2026-10-26 (not tagged)

- AEC v0: reasoning vocabulary, cross-record `check`, and change-impact analysis (`impact`).

## Before AEC: Codex++ (2025)

- Repository conventions (`.purpose.md`, `.intent.md`, `AGENTS.md`) and the 2025 AST dependency
  extractor (`src/core/`, not shipped). Archived rules: `docs/history/codex-plus-plus-AGENTS.md`.
