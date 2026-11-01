# Changelog

All notable changes to AEC. Versions follow [semantic versioning](https://semver.org/); before
1.0, a minor version may change command output or record fields (see "Stability" in README).

## [0.4.0] - unreleased

First public release candidate. No change to what any command computes.

### Added
- `aec` console command after `pip install`, and `aec --version`.
- One line of `--help` text for every subcommand.
- `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue templates, and a full `CONTRIBUTING.md`.
- `docs/release-readiness.md`: what "a release we can be proud of" means for AEC, as checks.
- `docs/evaluations/probe-001.md`: pre-registered design for the first outcome measurement (WP2-probe pilot).
- CI runs the test suite on Python 3.10, 3.11, 3.12 and 3.13.
- A test that the package version, `aec.__version__` and this changelog agree.

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
