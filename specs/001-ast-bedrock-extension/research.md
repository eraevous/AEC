# Research: AST bedrock + AEC extension

## R1. Edge kinds and how "refers to" is resolved
- **Decision**: there are five kinds: `defines`, `calls`, `imports`, `inherits`, `references`. A reference is an
  `ast.Name` or `ast.Attribute` read (Load context) whose root resolves to a definition in the analyzed code or to an
  imported name. Callees resolve the same way. Unresolvable roots, from dynamic access, builtins or locals, are emitted
  with `resolved: false` and target `?<expr>`. Builtins and local variables are dropped to keep noise down.
- **Rationale**: matches the spec's assumption (no guessing) and keeps the graph useful for impact.
- **Alternatives**: a full type inference library (rejected: violates stdlib-only); calls only (rejected: this is
  what the 2025 tool did, and Zach asked for "what refers to what").

## R2. Symbol identity
- **Decision**: a dotted module path derived from the file path relative to the analysis root, with `__init__`
  collapsed, plus the qualified name (`Class.method`, nested functions as `outer.<locals>.inner`). Records use
  `code:<dotted>`.
- **Rationale**: stable across runs and readable. It matches how Python names things.
- **Alternatives**: a content hash per symbol (useful for diffs and kept as `body_sha` on defines edges), or line numbers
  (they change with unrelated edits, so they are a location only).

## R3. Output format and determinism
- **Decision**: JSON lines. The first line is a header (`tool`, `version`, `root`, file count, a hash of the sorted file
  hashes). It is followed by edges sorted by (kind, src, dst, file, line). Location is a field, not part of identity.
  The diff compares identity (kind, src, dst). The `defines` edges carry `body_sha` so body-only changes show up.
- **Rationale**: diffs cleanly in Git. The header lets you tell stale snapshots apart.

## R4. The 2025 extractor
- **Decision**: keep `src/core/tools/ast_dependency_extractor.py` unchanged (it is historical and Data-Guide has a copy). The new
  `aec edges --legacy-csv` writes its `Source,Call` CSV format for comparison (US4).
- **Rationale**: FR-009 forbids hand-copying into Data-Guide, so comparing output formats is the migration path.
- **Known defects found in review**: it handles `FunctionDef` only (no async). Methods lose their class (named `module.method`).
  It needs pandas and typer. Module names come from `str.replace('.py','')`, which mangles names containing ".py".

## R5. Spec Kit extension mechanism (v1.2.3, verified in the installed package)
- **Decision**: `extension/extension.yml` with `schema_version: "1.0"`, `extension.id: aec`, `requires.speckit_version`,
  `provides.commands` (Markdown command files named `speckit.aec.*`), and `hooks.after_specify`, `after_tasks` and `after_implement`,
  each `optional: true`. Install with `specify extension add <path|url>`.
- **Evidence**: core extensions (`agent-context`, `git`) use exactly this schema. Hook points exist for every core
  command (`before_*` and `after_*` for specify, clarify, plan, tasks, analyze, implement, converge, checklist and constitution).
- **Rationale**: Spec Kit's own route, so no core edits (Constitution: additional constraints).

## R6. How the commands reach the `aec` package from a hook
- **Decision**: command files tell the agent to run `python -m aec …`, resolving the package from (1) an installed
  `aec` distribution (`pip install git+https://github.com/eraevous/AEC`) or (2) `AEC_HOME/src` on `PYTHONPATH`.
  If neither is available, the command says so; it never fails silently.
- **Alternatives**: vendoring the package into the extension. Rejected for now because it duplicates code across releases; revisit if
  installation friction is measured.
