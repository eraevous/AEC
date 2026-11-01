# Implementation Plan: WP1A commit snapshots and structural queries

**Branch**: speckit/005-implementation · **Base**: main@5000d00 · **Date**: 2026-11-01
**Spec**: [spec.md](spec.md), including all Clarifications; serves AEC-P0@1/AEC-R2@1.

## Constitution and scope
Python 3.10+ standard library, git as the only external runtime program. Extraction
reads text/AST/blobs; never imports/runs target code, checks out revisions or calls
network commands. Results are structural with visibility/caveat. Tests precede each
classifier/check and include negative decoys. Existing records are append-only;
anchor/propagation behavior is unchanged. No WP1B analytics, WP2A briefing or PR
comments. Append candidate claim/evidence and record cost. Regenerate the ignored
edge snapshot locally, respecting DEC-025 rather than recommitting it.

## Design and recorded interpretations
- Extend edges.py extraction to tool_version 0.4.0 and the five unresolved-call why
  kinds. Keep edge identity/order; only unresolved calls gain why. Constructor-bound
  local variables remain local_value; do not introduce type inference.
- Add snapshots.py for local git/tree materialization, configuration/method identity,
  snapshot comparison and boundary metadata; graph.py for projection queries.
  CLI remains parsing/dispatch/rendering.
- Configuration location is unspecified: use optional .aec/extraction.json with
  ignore (additional relative glob/component patterns) and source_roots ('auto',
  default; or explicit repo-relative directory list). Reject unknown/unsafe fields.
  method includes running tool_version, sorted effective ignores and source-root
  configuration, not content-dependent detected aliases. Include Python AST minor version and a
  builtin/stdlib-name fingerprint because parsing/hashing/alias resolution depend
  on those semantic inputs; do not confuse those with incidental machine paths.
  Hash canonical JSON.
- Commit snapshots use resolved full commit SHA, git ls-tree and raw git show
  blobs (no archive attributes/filters); materialize regular files only in a disposable directory. Never follow
  archive links or unsafe members. Working snapshots compare HEAD/index/raw blobs without git status, filters or
  index refresh; non-git trees remain usable with base_revision null/dirty true.
  Header root is absent; parser/read failures use relative paths. Ignore output file
  timestamps and temporary paths. Config paths must be repo-relative.
- Snapshot additionally records class names, literal __all__ declarations and import
  module labels as AST facts in header metadata: required for accurate subdivision,
  public-surface and module-projection queries without changing edge-line fields.
- diff uses merge-base(base,head), materializes both, then applies head configuration
  and running extractor symmetrically. Separately compare effective base/head method
  fields. Stored method mismatch/legacy unknown refuses by default; deliberate
  --allow-method-mismatch labels method comparison explicitly. Low-level edges.diff
  shares this guard. Existing edges --diff remains supported.
- Boundary/report indicators live on report copies of edges, not snapshot edge lines.
  Deepest shared directory and depths count directories below it (not filenames).
  cross_class requires two distinct containing classes within a file; __all__ only
  when literal declaration is known. Only explicit AST module imports/re-exports are traced for ownership; cyclic
  or uncertain aliases remain external. Mutated __all__ is unknown, not private.
- Graph nodes are endpoints in the selected projection. Calls may include module-
  body sources and external function labels; imports normalize to modules using AST
  import metadata; inheritance uses class endpoints. Unresolved edges are excluded
  from reach/degree calculations, counted by why; external calls remain distinguishable.
  Fan counts distinct graph neighbors; denominator counts raw projection edges.
- Reach defaults: callers, calls, depth 1; depth 0 is empty. Fan defaults calls/top 20,
  descending total degree then symbol; top 0 allowed. Both also accept --json/--repo.
  Region visibility is file-scoped for files containing origin/reached nodes: it
  includes unknown callers in those files without asserting their dynamic targets.
  Projection-wide and regional counts both state scope/denominator; skipped files
  remain a global visibility limit. Always print the exact caveat.
- unresolved filters allow repeated/multiple --why values, file/directory or lexical
  symbol-body --in filtering; stable file/line/caller/callee/why order. Each existing
  collapsed caller/callee edge is listed once (earliest location), not every callsite.
- CI extracts actual PR head SHA and compares merge-base against fetched origin/main,
  uploading JSON on Python 3.12 only; no comments. Existing record-touch stays intact.

## Validation and review
Throwaway git history fixtures cover every frozen table row, all why kinds and
constructor-local proposal, symmetric config and merge-base decoys, literal exports,
file/class boundaries, exact projection/visibility counts, method refusal/override,
legacy loads, dirty/non-git trees, no absolute paths, symlinks/no target execution,
CLI repeatability and artifact workflow. Full regressions and record-touch, local
regeneration, then an independent agent technical review (spec's role requirement).
No package version bump is needed: tool_version is extractor identity, distinct
from released package 0.4.1. Historical version observations are retained.
