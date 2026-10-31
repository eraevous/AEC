# Feature Specification: commit-addressed snapshots and structural diffs (WP1A)

**Feature Branch**: `speckit/005-commit-snapshots`
**Created**: 2026-10-30
**Status**: **Package approved by Zach; spec ready for review.** Zach, Claude chat, 2026-10-30 20:29 CT: "I approve WP1A." The spec is frozen for implementation after Kate's purpose review.
**Serves**: `AEC-P0@1`, `AEC-R2@1` (deterministic results labelled structural). Failure modes S1, S2, S6 and P1 (`docs/failure-modes.md`).
**Roles**: specified by Claude (AEC); implemented by Codex; technical review by Claude, plus an independent agent; purpose review by Kate; decisions by Zach.

## Why

`aec edges` gives a snapshot of whatever happens to be on disk. Nobody can say which commit it describes, two snapshots from different extractor versions look comparable when they aren't, and a PR can't be compared against the commit its branch started from. WP1A makes the topology **addressable** (by revision and extraction method) and **comparable** (by merge-base and head). It adds the smallest graph measures, each with an honest visibility figure.

It deliberately does **not** deliver graph information to agents as a briefing. That is WP2A, which Zach moved behind a probe that must first show graph information changes what agents do (see `docs/architecture.md`).

## User Scenarios & Testing *(mandatory)*

### User Story 1: a snapshot names exactly what it describes (P1)

`python -m aec snapshot [ROOT] [--rev REV] [-o FILE]`:
- **With `--rev`**, it extracts the tree at that git revision **without checking it out or executing anything**: it reads the blobs with `git archive` or `git show`. The header records `revision` (the full SHA) and `revision_kind: "commit"`.
- **Without `--rev`**, it snapshots the working tree. The header records `revision_kind: "working-tree"`, plus `base_revision` (HEAD) and `dirty: true|false`. It never claims to be a commit.
- **Every header records the extraction method:** `tool_version`, `ignore` patterns, the source-root configuration, and `method_sha`, a hash of all of those.
- **Environment-dependent fields are normalised.** The absolute root path is not stored; the output is repo-relative.

**Acceptance Scenarios:**
1. The same revision snapshotted twice gives byte-identical output.
2. A snapshot of `--rev HEAD~1` matches a snapshot of a checkout of HEAD~1, edge for edge.
3. A working-tree snapshot with uncommitted changes says `dirty: true` and `revision_kind: "working-tree"`.
4. A file that fails to parse at that revision is listed in `skipped` with the reason; it is never silently dropped.

### User Story 2: a PR compared against the commit it started from (P1)

`python -m aec diff [--base REF] [--head REF] [--json]`:
- It defaults to `--base origin/main --head HEAD`, and compares **merge-base(base, head)** with head, not the base tip.
- It refuses to compare snapshots whose `method_sha` differs. It reports `method mismatch` and lists the differing fields, unless `--allow-method-mismatch` is given; with that flag, the mismatch is printed at the top.
- The output contains:
  - edges added and removed, per kind;
  - definitions added, removed and changed (body hash);
  - modules added and removed;
  - **changes that cross modules**: added or removed `imports` and `calls` edges whose two ends are in different top-level modules.
- Output can be read by a person, or as JSON with `--json`.

**Acceptance Scenarios:**
1. On a fixture repo where the branch adds a call from `a` to `b.f`, the diff lists exactly that edge, and it is cross-module.
2. When the base branch moves after the fork, that change does **not** appear in the diff. This is the merge-base decoy.
3. Snapshots with different extractor configurations are refused, with the reason given.

### User Story 3: basic reach and fan-in/fan-out, with visibility (P1)

- `python -m aec reach SYMBOL [--direction callers|callees] [--projection calls|imports|inherits] [--depth N] [--rev REV]`
- `python -m aec fan [--projection calls|imports] [--top N] [--rev REV]`

Measures are **computed per projection, never across all edge kinds** (per the architecture):
- `reach` gives the set of symbols reachable within depth N, in one direction, in one projection.
- `fan` gives fan-in and fan-out per symbol in one projection.

**Every result carries a visibility block:**
- unresolved edges touching the region;
- skipped files;
- the denominator (resolved / total edges in the projection).

It also carries the fixed caveat: *"Known structural reachability is not runtime impact; an unresolved or dynamic call is invisible here."*

**Acceptance Scenarios:**
1. On a fixture, `reach --direction callers` for a function called from two places, one of them through a variable, finds the static caller. Visibility reports one unresolved edge in the region.
2. `fan` agrees with counts computed by hand on the fixture.
3. A `calls` query never includes `imports` edges, and the reverse.

### User Story 4: a CI report as an artifact (P2)

The CI workflow runs `aec diff --base origin/main --head HEAD --json` on pull requests and uploads the result as a **workflow artifact**. It posts no PR comments in this package.

## Data contract

Snapshot header fields:
- **added:** `revision`, `revision_kind`, `base_revision`, `dirty`, `method` (an object) and `method_sha`;
- **removed:** the absolute `root`;
- **kept:** the edge lines are unchanged from tool_version 0.3.0.

`aec edges` keeps working as an alias for a working-tree snapshot.

`tool_version` becomes 0.4.0. Snapshots from earlier versions load with `revision_kind: "unknown"`, and `diff` treats them as a method mismatch.

## Out of scope

- History analytics: cycles per projection, churn, co-change. Those are WP1B.
- Context briefings for agents, which is WP2A, moved behind the probe.
- PR comments, dashboards and a graph database or service.
- Executing target code, and dynamic or runtime call tracing.

## Fixtures (frozen with this spec)

A test helper builds a throwaway git repo with known history: base commits, a fork, a commit on the branch, and a commit on the base after the fork.

| Fixture | Expected |
|---|---|
| Same revision snapshotted twice | byte-identical |
| `--rev` vs checkout of the same commit | identical edges |
| Dirty working tree | `revision_kind: working-tree`, `dirty: true` |
| Branch adds a cross-module call | listed, flagged cross-module |
| Base moves after the fork (decoy) | absent from the diff |
| Different `ignore` configuration | diff refused: method mismatch |
| Caller through a variable | static caller found; one unresolved edge in visibility |
| `calls` projection query | contains no `imports` edges |

## Success Criteria

- **SC-1:** every fixture yields exactly its expected result.
- **SC-2:** outputs are deterministic and contain no absolute paths.
- **SC-3:** standard library only; extraction never imports or runs target code; `git` is the only external program.
- **SC-4:** every reach and fan result prints its visibility block and the fixed caveat. A doc-truth test checks this.
- **SC-5:** the implementer records the build cost in the intent note.
