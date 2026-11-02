# Snapshots and structural queries (WP1A)

The extractor is **tool_version 0.4.1**, distinct from the package version. WP1A
commands below are additions in the current source checkout; the release install
example for v0.4.1 does not include them until a subsequent release. The generated
`.aec/edges.jsonl` stays git-ignored: regenerate, do not commit it.

```bash
python -m aec snapshot . --rev HEAD -o .aec/head.jsonl
python -m aec edges . -o .aec/edges.jsonl
python -m aec diff --base origin/main --head HEAD --json
python -m aec reach src.pkg.pricing.apply_discount --direction callers --depth 2
python -m aec fan --projection imports --top 20
python -m aec unresolved --why local_value reflective --in src/pkg/ --json
```

From a source checkout, prefix with PYTHONPATH=src. All commands are offline;
extraction never imports/runs target code. Git is the only external runtime program.

## What a snapshot describes

snapshot --rev resolves a full commit SHA and reads regular Python/config blobs
with local Git, without checkout. Symlinks are not followed. Gitlinks are not
fetched or expanded. Without --rev, snapshot/edges reads the working tree: its
header says revision_kind=working-tree, base_revision=HEAD and dirty=true|false.
Non-Git trees use a null base and conservatively dirty=true. Commit headers say
revision_kind=commit and revision=the full SHA. Scope is repo-relative; no absolute
root or temporary paths are stored. Parse failures are listed in skipped.

Dirty checking compares HEAD, index and raw bytes (including initialized gitlink
working state) without status/index refresh or target filters/hooks. Therefore EOL
conversions/clean filters can conservatively make raw bytes differ even where Git's
filtered comparison would call the worktree clean. No filter is executed to hide
that difference. The snapshot never claims a working tree is a commit.

Header method contains tool_version, sorted effective ignore patterns and the
source-root configuration, plus Python AST minor version and a builtin/stdlib-name
fingerprint; method_sha is SHA-256 of canonical JSON. These semantic parser/resolver
inputs prevent cross-runtime body-hash differences from masquerading as code changes. Optional
.aec/extraction.json accepts:

```json
{"ignore":["generated/*"],"source_roots":["src"]}
```

Ignore entries augment the built-in exclusions and match relative paths or path
components with fnmatch semantics. source_roots defaults to "auto" (the existing
unambiguous top-level-directory inference); an explicit list limits alias roots.
Settings must be relative, not machine-specific absolute paths. Detected aliases
remain visible in the header separately from the extraction method. AST class,
module-binding/import and literal-export metadata allow projection/boundary queries;
edge lines stay unchanged except unresolved calls gain why.

## Compare branches or stored snapshots

Diff defaults to origin/main and HEAD, comparing their **merge base** with head,
not the current main tip. Both sides use head's config and the running extractor.
A config change gets a separate "method change in this PR" finding listing fields.
The report includes per-kind added/removed edges, body-hash definition changes,
module additions/removals, boundaries and unresolved changes by reason. Visibility
for the changed region and each projection is included.

```bash
python -m aec diff --base-snapshot .aec/base.jsonl --head-snapshot .aec/head.jsonl
python -m aec diff --base-snapshot .aec/base.jsonl --head-snapshot .aec/head.jsonl --allow-method-mismatch
```

Stored method mismatches, including legacy/unknown versions, are refused. The
explicit override labels the report **METHOD COMPARISON: compares methods, not just
code**. Legacy snapshots load with revision_kind=unknown. The existing edges --diff
alias uses the same method guard; code-impact also refuses incompatible methods.

A module is a file. Cross-file imports/calls report boundary.directory (deepest
shared directory, or .) and src_depth/dst_depth (directory levels below it, excluding
filenames). Same-file edges can have cross_class; cross-file edges can have
crosses_public_surface when a known literal __all__ excludes the destination's
name. Evident __all__ mutations make it unknown rather than producing a false
private-surface flag. These are indicators, not architectural verdicts. Unparsed
external endpoints have no inferred file boundary.

## Reach, fan and visibility

Queries accept --repo ROOT, --rev REV and --json. Reach defaults to calls/callers/
depth 1; depth 0 reaches nothing. Fan supports calls/imports, defaults to top 20,
counts distinct neighbors, and sorts by total degree then symbol. top 0 omits rows
but retains visibility. Projections never mix kinds. Calls/inherits trace only
explicit static import aliases; imports retain the imported module as their unit.
Nodes are projection endpoints: functions/classes for calls (including module-body
and external labels where present), modules for imports, classes for inheritance.

Visibility states resolved/total **raw projection edges**, external calls, skipped
files and unresolved counts by why, globally and for the region. Regional scope
includes touching known endpoints and their containing files: an unknown call's
target is never invented, but the uncertainty in those files is visible. A zero
regional count does not prove no unknown caller exists elsewhere. Unknown target
nodes are excluded from reach/degree arithmetic; resolved external labels remain
distinguishable. Every reach/fan report prints:

> Known structural reachability is not runtime impact; an unresolved or dynamic call is invisible here.

## Retrieve unresolved calls

unresolved lists file, line, caller/src, callee/dst and why, sorted by those fields.
Repeated --why or multiple values filter the five categories: local_value,
self_attr_unknown, unbound_name, computed_callee, reflective. --in accepts a file,
directory prefix, or lexical symbol body. Edges retain the existing collapsed
caller/callee identity and earliest location, rather than promising every callsite.

An imported third-party call is resolved external, not unresolved. A function local whose
only possible value is `C(...)`, for a class C defined in the analysed tree, resolves `x.m()` against C
and its known bases (tool_version 0.4.1, C-11). It must be assigned exactly once, by a plain top-level
statement, and must not be a parameter or lambda parameter, loop, `with` or `except` target,
`global`/`nonlocal` (also from a nested function), deleted, or captured from an outer function. C must
not be rebound by a second local import, and C(...) must return a C: no `__new__` (defined or assigned)
on C or a base, and no metaclass from the analysed tree overriding `__call__`. Any other local stays
local_value, as does an attribute C doesn't define. This is not general type inference.
Known static re-exports are traced; cyclic/expanding aliases stay uncertain.

## CI and existing records

Pull-request CI uses actual head SHA plus merge-base and uploads JSON as a workflow
artifact on Python 3.12. It posts no comments. check --edges and code-impact remain
available for recorded code dependencies; structural call edges never become
justificatory relations automatically. No graph briefing or runtime impact claim
is introduced by WP1A.
