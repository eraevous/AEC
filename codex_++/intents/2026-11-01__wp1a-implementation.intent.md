# WP1A implementation intent — 2026-11-01

@ai-intent: Implement frozen spec 005 including clarified symmetric methods, why
kinds, projection units and file/directory boundaries. HO-20261101-002 acknowledged.

## Scope and starting context

New branch speckit/005-implementation from fetched main@5000d00 (includes #24/#29).
No source chat/probe corpus is consulted. Current context includes prior AEC work;
no pristine cold-implementer claim. Existing unrelated scratch/outputs stay local.
Plan and tasks written before implementation. Source/anchor behavior and historical
record lines will not be changed. Git operations allowed; new commands are offline.

## Questions / narrower interpretations

- Spec does not name extraction config file: .aec/extraction.json, ignore and
  source_roots only, with stable defaults and explicit validation (see plan).
- Graph endpoint types follow projections; module-body call sources/external labels
  are real existing endpoints and will be stated, not silently discarded.
- An unresolved call cannot be attributed to an unknown target. Region visibility
  conservatively covers files containing the known region, explicitly labelled.
- Boundary/class/export metadata belongs in report/header facts; snapshot edge
  lines remain unchanged except why. Literal __all__ only; no target execution.
- Existing .aec/.gitignore and DEC-025 require local regeneration, not a tracked
  snapshot change. Package 0.4.1 and extractor tool_version 0.4.0 are distinct.
- Constructor local p=DataProfiler(...);p.profile_dataset() stays local_value.
  A separate kind would require identifying value provenance/type inference beyond
  this spec; the fixture can motivate later work, not a silent extra classifier.

Instrumented start (after initial reading/planning): 2026-11-01T22:51:38.693026+00:00

## Baseline and fixture results

Baseline: 126 tests run (125 passed), one existing optional Spec Kit install/remove test skips
because its CLI is not installed. Initial full regression before review refinements:
145 tests run (144 passed) with the same skip. The optional pinned CLI installation was rejected by
automatic approval review as outside stdlib/git-only scope. No workaround attempted;
retain the existing documented skip, with all WP1A fixtures executed locally.

Tests-first fixtures cover every frozen-table case, plus known-constructor local
calls, bound/reflection alias decoys, hostile filters/hooks, re-exports, gitlinks,
method metadata integrity and expanding alias cycles. File/class/export facts are
header metadata, keeping snapshot edge-line changes limited to why. Static imports
are traced without value/type inference. Imported but absent submodules remain
external; import projections retain AST module units rather than function owners.

## Independent technical review and concrete rework

The spec calls for an independent agent: repository-only review (no edits, network
or chat sources) found real defects despite passing initial fixtures. Each was
reproduced in a failing test before its fix:
- git status can run clean filters and post-index-change hooks. Replaced it with
  HEAD/index/raw-blob comparison, no refresh. All git reads disable hooks, external
  pager, replacements, optional locks and protocols/lazy fetching. Raw EOL/filter
  differences conservatively count as dirty rather than executing target helpers.
- Parent-package prefix matching falsely gave absent submodules an owning file.
  Ownership now uses actual declarations and explicit static re-export bindings.
- A mutated literal __all__ could falsely flag a public target as outside exports.
  Other reads/writes/import bindings make the declaration conservatively unknown.
- Known re-exports were then missing from file ownership/caller queries. Header
  import bindings now trace actual owners/canonical call endpoints, while imports
  keep their module unit. This is import-name tracing only, not instance inference.
- Initialized submodule dirty contents were missed. Compare their working state
  recursively with a cycle guard; never fetch gitlinks, and list commit gitlinks
  as unexpanded in skipped visibility.
- Self-expanding import aliases could recurse forever. Guard repeated binding
  rewrites and preserve the original uncertain external label on cycles.
The reviewer confirmed the earlier repros fixed; the final cycle has a local
regression fixture. Agent review is candidate technical evidence, not owner consent.

## Additional method/compatibility interpretations

Method identity also fingerprints Python AST minor version and builtin/stdlib name
sets: these affect AST body hashes, parsing and auto alias resolution. Treat them
as semantic method inputs, not incidental absolute machine paths. A stored method
from a different parser is refused; legacy headers cannot borrow a current hash.
Package 0.4.1 is unchanged; extractor tool_version is 0.4.0. Current docs are updated;
historical evaluations retain the versions on which their observations were made.

Use local git ls-tree plus raw git show blobs instead of archive extraction: this
avoids export-ignore/attribute filtering and matches the spec's git-show option.
Config filename, query defaults and file-scoped regional visibility were unspecified;
all choices are explicit in plan/reference. Regional counts include direct touching
endpoints and the files of known region nodes, without inventing unknown targets.
Known reachability remains distinct from runtime impact. No WP1B/WP2A work added.

## Final verification and cost

150 tests run: 149 passed, 1 pre-existing optional integration skipped. All 23
WP1A tests and the dedicated visibility/caveat doc-truth check pass. Independent
agent final review found no remaining blocking defect after rechecking all repros.
Canonical check: 0 errors/13 warnings, byte-for-byte same findings as base records
under current local source availability; warnings concern prior records/private
source availability, not new WP1A records. Example check: 0 errors/0 warnings.
Ignored snapshot regenerated twice identically; existing record lines are a byte
prefix. Frozen specs 004/005, anchor implementation and propagation match main base.
Model elapsed from instrumented post-planning start 2026-11-01T22:51:38.693026+00:00 to 2026-11-01T23:19:17.798776+00:00: 27.65 minutes.
Initial reading/planning is additional and unmeasured; owner attention and tokens
are unavailable. No analyze/converge workflow or comparative-benefit claim.

Dissent: method identity can only be as honest as its captured parser/resolver
inputs; unknown calls and unknown export mutations intentionally remain visible/
uncertain. File-scoped regional visibility can over-include unrelated calls in the
same file, and cannot find hidden callers in other files; global counts/caveat remain.
The constructor-local fixture suggests a potential provenance subtype for later
filtering, but does not demonstrate enough incremental value to warrant a new kind
in WP1A. It stays local_value; no instance/type inference was added.

Delivery: new branch/PR only, CLA unticked; no merge, record acceptance, anchor
behavior change, WP1B history analytics, WP2A briefings or PR comments. Final chat
result is for claude:aec to file as outputs/HO-20261101-002.md privately.
