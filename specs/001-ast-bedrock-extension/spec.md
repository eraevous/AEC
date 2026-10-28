# Feature Specification: AST bedrock + AEC as an installable Spec Kit extension

**Feature Branch**: `speckit/aec-extension`

**Created**: 2026-10-26

**Status**: Draft

**Serves**: `AEC-P0@1` (purpose); `AEC-R1@1` (no competing authority); `AEC-R4@1` (usable in a second repo, provisional). Records: `.aec/records.jsonl`.

**Input**: User description: "The AST tracing tool: a small Python program in AEC that outputs a list of edges for what calls what and what refers to what. It should be extremely helpful, probably run pretty frequently, and be one of the bedrocks of the whole thing. AEC should sit on top of Spec Kit. The next real use is overhauling the Data-Guide repo with Spec Kit plus AEC, so AEC needs to be less crappy first." (Zach, 2026-10-26)

## Clarifications

### Session 2026-10-26

_Answered by the AEC Claude under Zach's delegation ("using Spec Kit yourself will serve to mature the AEC part"). Each answer is a recommended default that Zach may override._

- Q: When should the edge graph regenerate automatically? → A: After every agent file edit (an editor or agent hook) and in CI on every push and PR. Both reuse the same command. The hook only reports; CI fails only on errors such as a record pointing at a code symbol that no longer exists.
- Q: How is AEC installed into another repo, such as Data-Guide? → A: As a Spec Kit extension installed from a local path or a GitHub release URL via `specify extension add` (or `specify init --extension`), plus the `aec` package installed with `pip install git+https://github.com/eraevous/AEC` for the commands. Copying source files by hand is not supported.
- Q: Do unresolved references (dynamic calls, unknown names) count as edges for change impact? → A: They are recorded and diffed, but they never trigger impact alone. A record can only be affected through a resolved symbol it references.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ground truth about the code, on every change (Priority: P1)

A maintainer, or an AI agent working in a repo, runs one command and gets a complete, deterministic list of what the code defines, calls, imports and refers to. It is fast enough to run after every edit. Running it on two versions of the code shows exactly which structural relationships appeared or disappeared.

**Why this priority**: Everything else in AEC anchors to it (Constitution VI). Purpose contracts, drift checks and change impact are only as trustworthy as their picture of the actual code. Today's extractor only covers function-to-function calls and needs third-party packages to run.

**Independent Test**: Run it on the Data-Guide repository and on a small fixture package with known structure. The fixture's expected edges match exactly. Repeated runs give byte-identical output. Diffing two fixture versions lists only the edges that actually changed.

**Acceptance Scenarios**:

1. **Given** a Python package with module functions, classes with methods, async functions, imports with aliases and module-level code, **When** the maintainer runs the edge command, **Then** the output lists every definition, every call, every import and every name reference, each tagged with its kind and source location.
2. **Given** the same code, **When** the command runs twice, **Then** the outputs are identical.
3. **Given** two versions of a package where one function gains a call and another is deleted, **When** the maintainer diffs the two snapshots, **Then** exactly the added call edge and the deleted definition with its edges are reported, and nothing else.
4. **Given** a file with a syntax error, **When** the command runs, **Then** that file is reported as skipped with the reason, and every other file is still processed.

---

### User Story 2 - "This code changed; which conclusions are affected?" (Priority: P2)

A maintainer changes code. AEC turns the structural diff into change events against the records that link requirements, claims and decisions to code symbols. It then reports which conclusions now need re-examination, using the existing impact classifications.

**Why this priority**: This joins the bedrock to AEC's distinctive capability (change impact). Without it, code changes and the purpose records stay disconnected, and that disconnect is the drift AEC exists to catch.

**Independent Test**: In a fixture repo whose records say a requirement is implemented by two named functions, change one function's calls, run the command, and the requirement and the claims and decisions downstream of it are reported. Change a function nothing references, and nothing is reported.

**Acceptance Scenarios**:

1. **Given** a requirement linked to a code symbol, **When** that symbol's outgoing edges change, **Then** the requirement and its dependents are reported with an explanation path from the changed symbol.
2. **Given** a symbol linked to a record is deleted, **When** impact runs, **Then** the linking record is reported as relying on something that no longer exists.
3. **Given** only unlinked code changes, **When** impact runs, **Then** no conclusions are reported.

---

### User Story 3 - AEC runs inside the normal Spec Kit flow (Priority: P3)

A team already using Spec Kit installs AEC as an extension. At defined points in the Spec Kit sequence, AEC runs its checks and returns findings for the people involved to resolve. It never edits specs, plans or tasks. The points are: after specify (does the spec cite the purpose it serves?), after tasks or analyze (do the records check?), and after implement (structural diff and impact).

**Why this priority**: The white paper positions AEC as an extension, not a replacement (`AEC-R1@1`). It has to work through Spec Kit's own extension mechanism.

**Independent Test**: In a fresh Spec Kit project, install AEC as an extension. Run a Spec Kit command that has an AEC hook. The hook appears, runs, and produces a findings report. Removing the extension leaves the project unchanged except for AEC's own files.

**Acceptance Scenarios**:

1. **Given** a Spec Kit project, **When** AEC is installed as an extension, **Then** its hooks are registered and the Spec Kit commands list them at the right points.
2. **Given** a spec that does not cite any AEC purpose, **When** the after-specify hook runs, **Then** a finding is reported, and the spec file is not modified.
3. **Given** the extension is removed, **When** the Spec Kit commands run, **Then** no AEC hooks run and no Spec Kit file is left altered.

---

### User Story 4 - Use it on a second real repo: Data-Guide (Priority: P4)

The maintainer installs AEC into the Data-Guide repository and runs the edge graph and record checks there, ahead of the Spec Kit plus AEC overhaul.

**Why this priority**: AEC has only been exercised on the repos it was built in. A second repo tests whether it travels (`AEC-R4@1`).

**Independent Test**: Install into a copy of Data-Guide, produce its edge graph, and compare it with Data-Guide's existing `ast_deps.csv`. Every call edge in the old file is either present in the new graph or explained.

**Acceptance Scenarios**:

1. **Given** a clean Data-Guide checkout, **When** AEC is installed and the edge command runs, **Then** it completes without third-party packages and produces the graph.
2. **Given** Data-Guide's older `ast_deps.csv`, **When** compared with the new graph, **Then** the differences are listed and classified (new edge kinds, resolution differences, removed code).

### Edge Cases

- Dynamic calls (`getattr`, `importlib`, calls through variables) cannot be resolved statically. They are recorded as unresolved references, never guessed.
- Relative imports, `from x import *`, and imports inside functions.
- Two modules that define the same function name.
- Non-UTF-8 or unparseable files: skipped with a reason, without stopping the run.
- Very large repos: the run must finish without unbounded memory growth.
- A record references a code symbol that never existed (a typo): reported by the record check.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST extract, from Python source, edges of these kinds: defines (module→class/function, class→method), calls, imports, inherits, and references (a name or attribute read that resolves to a known definition or import).
- **FR-002**: Every edge MUST carry its kind, source symbol, target symbol and source location (file, line). Targets that cannot be resolved statically MUST be marked unresolved.
- **FR-003**: Output MUST be deterministic and stably ordered, in a line-oriented format that diffs cleanly.
- **FR-004**: The system MUST compute the difference between two edge snapshots: added and removed edges, and added and removed definitions.
- **FR-005**: The system MUST require no third-party packages.
- **FR-005a**: The edge graph MUST regenerate after each agent edit (report only) and in CI (failing only on errors such as dangling code references).
- **FR-006**: Records MUST be able to reference code symbols by a stable identifier, and the record check MUST report code references that do not resolve against the current edge graph.
- **FR-007**: The system MUST convert a structural diff into change events for the records that reference changed or deleted symbols, and report impact using the existing classifications.
- **FR-008**: The system MUST be packaged as a Spec Kit extension for the pinned Spec Kit version, registering hooks at defined points, and its hooks MUST only report findings, never modify Spec Kit artifacts.
- **FR-009**: Installing the system into another repository MUST NOT require copying source files by hand.
- **FR-010**: Each feature built with this workflow MUST log what Spec Kit's analyze and converge reported, what AEC reported, and the authoring time (Constitution V).

### Key Entities

- **Edge**: a structural relationship between two code symbols: its kind, source, target, location, and whether it was resolved.
- **Edge snapshot**: the full set of edges for a codebase at a point in time, with the tool version and the file hashes it was computed from.
- **Structural diff**: added and removed edges and definitions between two snapshots.
- **Code reference**: a record's pointer to a code symbol, such as a requirement implemented by a function.
- **Extension hook**: a registered AEC action at a named point in the Spec Kit sequence. It produces findings only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a fixture package with hand-labelled structure, 100% of the labelled defines, calls, imports and inherits edges are produced, with no spurious edges of those kinds.
- **SC-002**: The edge graph of a repository the size of Data-Guide (32 files, about 3,200 lines) is produced in under 2 seconds on an ordinary laptop, so running it after every change is practical.
- **SC-003**: Repeated runs on unchanged code are byte-identical in 100% of trials.
- **SC-004**: In the impact fixtures, every conclusion that relies on a changed symbol is reported, and none that doesn't (no false alarms on the decoy).
- **SC-005**: A maintainer can install the extension into a fresh Spec Kit project and into Data-Guide in under 5 minutes, following the README.
- **SC-006**: For this feature, the Spec Kit-vs-AEC log records at least what each found at analyze and converge time, plus authoring minutes.

## Assumptions

- "Refers to" means a name or attribute read that resolves to a definition in the analyzed code or to an imported name. Other reads are not edges. A dynamic access is recorded as an unresolved reference. (Informed default, made in place of a clarification.)
- Code symbols are identified by dotted module path plus qualified name (for example `pkg.mod.Class.method`). Records reference them as `code:<dotted>`. A symbol's version is taken from its snapshot, not written by hand.
- AEC hooks are optional by default (they report findings). A team can make a hook mandatory in its own configuration.
- Python only for this feature. Other languages are out of scope.
- The 2025 extractor (`src/core/tools/ast_dependency_extractor.py`) is replaced by the new edge extractor. Its CSV output is supported for comparison only.
- Measurement against a full Spec Kit baseline (white paper validation plan) is out of scope for this feature. This feature produces the log the comparison will need.
