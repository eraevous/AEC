# Feature Specification: commit-addressed snapshots and structural diffs (WP1A)

**Feature Branch**: `speckit/005-commit-snapshots`
**Created**: 2026-10-30
**Status**: **Package approved by Zach; spec ready for review.** Zach, Claude chat, 2026-10-30 20:29 CT: "I approve WP1A." The spec is frozen for implementation after Kate's purpose review. **Clarified 2026-11-01** with Zach's answers to Kate's questions (see Clarifications).
**Serves**: `AEC-P0@1`, `AEC-R2@1` (deterministic results labelled structural). Failure modes S1, S2, S6 and P1 (`docs/failure-modes.md`).
**Roles**: specified by Claude (AEC); implemented by Codex; technical review by Claude, plus an independent agent; purpose review by Kate; decisions by Zach.

## Why

`aec edges` gives a snapshot of whatever happens to be on disk. Nobody can say which commit it describes, two snapshots from different extractor versions look comparable when they aren't, and a PR can't be compared against the commit its branch started from. WP1A makes the topology **addressable** (by revision and extraction method) and **comparable** (by merge-base and head). It adds the smallest graph measures, each with an honest visibility figure.

It deliberately does **not** deliver graph information to agents as a briefing. That is WP2A, which Zach moved behind a probe that must first show graph information changes what agents do (see `docs/architecture.md`).

## Clarifications

Zach, Claude chat, 2026-11-01 12:15 CT, answering Kate's questions about WP1A. His words are quoted; the rules under each are claude:aec's reading of them, written into the stories below.

1. **One extraction method for both sides.** *"Are there likely future cases we can think of where asymmetric settings would be needed? If there's not a compelling case for otherwise, we can use the symmetric settings for the comparison."*
   - Candidate cases considered:
     - a PR that changes the extraction configuration (`ignore`, source roots);
     - a PR that changes the extractor itself (AEC's own `edges.py`);
     - comparing old stored snapshots from earlier tool versions;
     - evaluating one extractor against another on the same code.
   - None of these needs a diff whose two sides used different methods. The first three are answered by extracting both sides with one method; the fourth compares methods, not code.
   - **Rule:** `aec diff` extracts base and head with one method, taken from the head's configuration and the running tool. When the head changes the extraction configuration, the diff reports that as a separate `method change in this PR` finding, listing the fields, and doesn't silently absorb it.
   - Comparing two *stored* snapshots whose methods differ stays refused, as before. `--allow-method-mismatch` remains only for deliberately comparing methods, and its output says so at the top.
2. **Untraceable calls are retrievable and filterable by why they are untraceable.** *"Untraceable calls should also have some method to be retrieved and filtered to them, distinguishable by the nature of untraceablity."*
   - This replaces claude:aec's earlier proposal, which was a global count only.
   - Every unresolved `calls` edge carries `why`, one of these:

     | `why` | when |
     |---|---|
     | `local_value` | the callee is a local variable or parameter (callbacks, higher-order functions) |
     | `self_attr_unknown` | a `self.`/`cls.` attribute not found on the class or its known bases |
     | `unbound_name` | a name bound neither in the module nor by an import the extractor resolved (for example a star import from an unparsed module, or an injected global) |
     | `computed_callee` | the callee isn't a dotted name: a call result, a subscript, a lambda |
     | `reflective` | the call is built by reflection: `getattr(...)(...)`, `importlib.import_module(...)`, `__import__`, or a call to `eval`/`exec` |

   - Calls that resolve to a name outside the snapshot (an import of a third-party package) are not unresolved. They are listed separately as `external` in visibility.
   - Retrieval: `python -m aec unresolved [--why KIND ...] [--in PATH|SYMBOL] [--rev REV] [--json]` lists each one with file, line, caller, callee label and `why`, in stable order.
   - Visibility blocks in `reach`, `fan` and `diff` count unresolved edges **by `why`**, for the region and for the projection.
3. **Graph units are defined per projection.** *"Yeah, graph units can be dynamically determined as proposed."*
   - In each projection, the nodes are the symbols that appear as endpoints of that projection's edges: functions and classes for `calls` and `inherits`, modules for `imports`.
   - `fan` and `reach` state the node type they counted.
4. **Module boundaries are at file level, with sub-file indicators and directories for higher levels.** *"Module boundaries at file level, with other indicators of subdivisions, and filesystem for higher-level organization."*
   - A module is a file.
   - An edge is **cross-module** when its two ends are defined in different files. Each such edge reports `boundary`: the path of the deepest directory the two files share, and how many directory levels each end sits below it. That is the filesystem as higher-level organisation.
   - **Other indicators of subdivision** are reported, but never treated as module boundaries:
     - `cross_class`, on an edge *within* a file whose two ends belong to different classes;
     - `crosses_public_surface`, on a cross-file edge that reaches a name the target file leaves out of its declared `__all__`.

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
- It extracts both sides with **one method** (Clarification 1). When the head's extraction configuration differs from the base's, it reports `method change in this PR` with the differing fields.
- Given two stored snapshots (`--base-snapshot`/`--head-snapshot`) whose `method_sha` differs, it refuses. It reports `method mismatch` and lists the differing fields, unless `--allow-method-mismatch` is given; with that flag, the output begins by saying it compares methods, not just code.
- The output contains:
  - edges added and removed, per kind;
  - definitions added, removed and changed (body hash);
  - modules added and removed;
  - **changes that cross modules**: added or removed `imports` and `calls` edges whose two ends are in different files, each with its `boundary` (Clarification 4); within-file edges carry the sub-file indicators instead;
  - unresolved `calls` edges added and removed, by `why`.
- Output can be read by a person, or as JSON with `--json`.

**Acceptance Scenarios:**
1. On a fixture repo where the branch adds a call from `a` to `b.f`, the diff lists exactly that edge, and it is cross-module, with its boundary.
2. When the base branch moves after the fork, that change does **not** appear in the diff. This is the merge-base decoy.
3. Stored snapshots with different extractor configurations are refused, with the reason given.
4. A branch that changes the `ignore` configuration gets one-method extraction plus a `method change in this PR` finding.

### User Story 3: basic reach and fan-in/fan-out, with visibility (P1)

- `python -m aec reach SYMBOL [--direction callers|callees] [--projection calls|imports|inherits] [--depth N] [--rev REV]`
- `python -m aec fan [--projection calls|imports] [--top N] [--rev REV]`

Measures are **computed per projection, never across all edge kinds** (per the architecture):
- `reach` gives the set of symbols reachable within depth N, in one direction, in one projection.
- `fan` gives fan-in and fan-out per symbol in one projection.

Each result states the node type of its projection (Clarification 3).

**Every result carries a visibility block:**
- unresolved edges touching the region, counted by `why` (Clarification 2), and `external` calls;
- skipped files;
- the denominator (resolved / total edges in the projection).

It also carries the fixed caveat: *"Known structural reachability is not runtime impact; an unresolved or dynamic call is invisible here."*

**Acceptance Scenarios:**
1. On a fixture, `reach --direction callers` for a function called from two places, one of them through a variable, finds the static caller. Visibility reports one unresolved edge in the region.
2. `fan` agrees with counts computed by hand on the fixture.
3. A `calls` query never includes `imports` edges, and the reverse.

### User Story 3b: retrieve the calls the graph can't trace (P1)

`python -m aec unresolved [--why KIND ...] [--in PATH|SYMBOL] [--rev REV] [--json]` (Clarification 2).

**Acceptance Scenarios:**
1. One fixture has a call of each `why` kind. `--why reflective` returns only the reflective call, and the reverse holds for each kind.
2. A call to an imported third-party function is listed as `external`, not unresolved (decoy).
3. `--in` limits the results to a file or to a symbol's body. Output order is stable.

### User Story 4: a CI report as an artifact (P2)

The CI workflow runs `aec diff --base origin/main --head HEAD --json` on pull requests and uploads the result as a **workflow artifact**. It posts no PR comments in this package.

## Data contract

Snapshot header fields:
- **added:** `revision`, `revision_kind`, `base_revision`, `dirty`, `method` (an object) and `method_sha`;
- **removed:** the absolute `root`;
- **edge lines:** unchanged from tool_version 0.3.0, except that unresolved `calls` edges gain `why`.

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
| Caller through a variable | static caller found; one unresolved edge, `why: local_value`, in visibility |
| One call of each `why` kind | each filtered alone by `--why` |
| Imported third-party call (decoy) | `external`, not unresolved |
| Branch changes `ignore` | one-method extraction plus `method change in this PR` |
| Edge between `src/a/x.py` and `src/b/y.py` | cross-module, boundary `src` with depths 1 and 1 |
| Method calling another class's method in the same file (decoy) | not cross-module; `cross_class` indicator |
| Call from another file to a name outside a declared `__all__` | `crosses_public_surface` indicator |
| `calls` projection query | contains no `imports` edges |

## Success Criteria

- **SC-1:** every fixture yields exactly its expected result.
- **SC-2:** outputs are deterministic and contain no absolute paths.
- **SC-3:** standard library only; extraction never imports or runs target code; `git` is the only external program.
- **SC-4:** every reach and fan result prints its visibility block and the fixed caveat. A doc-truth test checks this.
- **SC-5:** the implementer records the build cost in the intent note.
