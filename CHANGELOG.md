# Changelog

All notable changes to AEC. Versions follow [semantic versioning](https://semver.org/); before
1.0, a minor version may change command output or record fields (see "Stability" in README).

## [Unreleased]

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
  `docs/reference/records-hygiene.md` gives the manual clean-up.

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
