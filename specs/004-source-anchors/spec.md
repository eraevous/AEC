# Feature Specification: source anchors and source retrieval (WP-S)

**Feature Branch**: `speckit/004-source-anchors`
**Created**: 2026-10-30
**Status**: **Frozen for implementation.** Zach authorized it (Claude chat, 2026-10-30 13:07 CT): "WP-S looks good, and I agree with the recommendations from Kate. I'm giving the OK to go ahead." The scope below was negotiated between Kate and Claude.
**Serves**: `AEC-P0@1`, `AEC-R2@1` (claim honesty). Failure mode P8 (`docs/failure-modes.md`).
**Roles**: specified by Claude (AEC); implemented by Codex, cold, from this repository only; technical review by Claude; purpose review by Kate; decisions by Zach.

**Input**:
- **representation-001** (relay-kit-private, `experiments/representation-001/results.md`), a pilot. Narrative, structured and hybrid builds of the same history scored 61, 60 and 61 out of 96. Every difference between them came from facts the builder had dropped. Agents never disagreed about facts they actually had. Two incidental questions scored 0 in every condition.
- **Zach (2026-10-30 09:23 CT):** "I agree with that conclusion." The conclusion: "prose for reasons, linked to records for status and open items, with the original sources kept rather than replaced by any summary."
- **Kate's review** in the AEC coordination thread (2026-10-30), which set the scope and the five verification states.

## Why

What a summary drops, a later agent can't recover from the summary. In representation-001, answer quality was limited mainly by which source facts survived construction. Whether the format itself caused those losses is unresolved. Kate put it as "Memory representation is not the same thing as memory preservation." AEC records summarise. WP-S lets a record point back at the source passage it came from, checks that the pointer still holds, and keeps a route to the sources that doesn't depend on any record.

**Design rule:** a knowledge index must not be the only route to knowledge it failed to index.

## Five capabilities, kept separate

| # | Capability | WP-S |
|---|---|---|
| 1 | Preserve a source | Referenced in place; never copied |
| 2 | Link a record to it | **yes** |
| 3 | Find it when needed | **basic**: record-directed retrieval, plus a search fallback |
| 4 | Interpret what it means | no; reviewers and agents |
| 5 | Trust its authority | no; the existing evidence and authority machinery |

`aec` output never says an anchor *supports*, *verifies* or *authorizes* a claim.

## User Scenarios & Testing *(mandatory)*

### User Story 1: a record points at its source, and the pointer is checked (P1)

A record carries `anchors`. `aec check` reports, for each anchor, whether the artifact exists, whether its bytes match, and whether the locator resolves. It never reports whether the passage supports the claim.

**Acceptance Scenarios**:
1. **Given** an anchor to an existing file whose sha256 matches and whose locator resolves, **then** its state is `verified`.
2. **Given** an anchor with a plausible 64-hex digest and no file at the stated path in an available source root, **then** its state is `missing`. *(P8 case 1.)*
3. **Given** a file whose bytes no longer match the anchor's digest, **then** the state is `mismatch`. The finding says the earlier observation is not falsified, but its applicability needs review. *(P8 case 2.)*
4. **Given** a matching file whose locator falls outside it, or whose quoted text isn't in it, **then** the state is `locator_invalid`.
5. **Given** an anchor whose source root isn't configured or isn't present on this machine, **then** the state is `unavailable`, never `missing`. The finding says the source can't be checked here; it doesn't say the source is gone.
6. **Given** a valid artifact (P8 case 3, the decoy), **then** there is no finding.
7. **Given** any of the above, **then** `check` exits 0, or only fails for errors unrelated to anchors. Anchor states are findings, not errors. The same input gives byte-identical output.

### User Story 2: an agent reads the passage behind a record (P1)

`python -m aec source show <record-ref> [--context N]` prints each anchored passage with N lines around it (default 3). Each passage is labelled with the record, the anchor index, its verification state and whether it came from `text` or `rationale`. Passages whose anchor isn't `verified` are printed only with a warning banner, and not printed at all for `missing` or `unavailable`.

**Acceptance Scenarios**:
1. A line-range locator prints exactly those lines plus context, and line numbers match the source.
2. A quote locator prints the lines containing the first exact match.
3. Output is bounded. Passages over `--max-lines` (default 80) are truncated, with an explicit note.

### User Story 3: an agent finds what no record points at (P1)

`python -m aec source search <pattern> [--root R] [--regex] [--max N]` searches the configured source roots directly. Every hit is labelled **`fallback`** (not record-directed), with its path, line and the file's current sha256. Each hit also says which records, if any, anchor that file.

**Acceptance Scenarios**:
1. A term that appears in a source but in no record is found and labelled `fallback`.
2. Search results come in a stable order (path, then line), with a stated limit and a count of hits omitted beyond it.
3. Search reads only configured roots. It never follows symlinks out of a root, never touches the network and never executes anything.

### User Story 4: a record can keep the reason apart from the conclusion (P2)

Records may carry an optional `rationale` string, kept separate from `text` (`text` keeps its current meaning). An anchor may name what it is for: `for: "text" | "rationale"`, with `text` as the default.

## Data contract

**Anchor fields:**

```json
"anchors": [
  {"root": "corpus", "path": "chatgpt-mtg-coord-archive.md", "sha256": "<64 hex>",
   "locator": "L1201-1214", "for": "text"}
]
```

- `sha256` is the SHA-256 of the file's **raw bytes**, with no normalisation. The README documents this.
- `locator` is one of:
  - `L<start>-<end>` or `L<n>` (1-based, inclusive lines);
  - `q:<exact text>` (the first occurrence; must match within one line).
- `root` names a source root. If it's omitted, the path is relative to the repository.
- **Source roots** are set in `.aec/sources.json`: `{"roots": {"corpus": "../relay-kit-private/experiments/representation-001/corpus"}}`. A path may be repo-relative or absolute. A root that doesn't exist on this machine gives `unavailable` for its anchors.
- **AEC never copies source content into the repository.** A content digest identifies content and checks its integrity; it controls no access.
- Anchors are allowed on every record type. They don't change justification status. `impact` and propagation are untouched.
- `check` validates the anchor shape:
  - a malformed digest, an unknown `for`, or an unparseable locator is an **error**, since it's a malformed record;
  - every state from User Story 1 is a **finding**.
- Existing records are never rewritten. Adding anchors to an existing claim means appending a new version.

## Out of scope (deferred)

- Automatically building semantic relations from the corpus.
- Vector, embedding or full-text index services.
- Judging whether a passage supports a claim.
- Deriving authorization from a quoted passage.
- An archival or content-addressed storage service.
- Private or remote source providers (only local roots now).
- Mass migration of historical records.
- The deletion-propagation fix, which is a separate PR.

## Fixtures (frozen with this spec)

These go under `tests/fixtures/anchors/`. Each check needs both a violating fixture and a decoy:

| Fixture | Expected state |
|---|---|
| P8-1: plausible digest, no file | `missing` |
| P8-2: bytes changed after anchoring | `mismatch` |
| P8-3: valid artifact (decoy) | `verified`, no finding |
| locator past end of file; quote not present | `locator_invalid` |
| root configured but absent | `unavailable` |
| term present in a source but in no record | found by `source search`, labelled `fallback` |
| malformed digest (63 hex) | error |

## Success Criteria

- **SC-1:** every fixture above yields exactly its expected state, and the decoys yield no finding.
- **SC-2:** `check`, `source show` and `source search` output is byte-identical across two runs. Paths are relative where the root is relative.
- **SC-3:** standard library only. The full suite passes. `.aec/edges.jsonl` is regenerated.
- **SC-4:** no command output uses "supports", "verifies the claim", "proves" or "authorized" about an anchor. A doc-truth test greps the output templates for these words.
- **SC-5:** Codex records its implementation cost (wall time, and tokens if available) in its intent note.

## After implementation (not part of this PR)

1. **Development smoke test (claude:aec, outside the repo).** Configure the representation-001 corpus as a root. Check that `source search` finds the Q14 and Q15 facts, and whether they're reached through a record or through the fallback, with cost recorded. These are development fixtures, not evaluation results.
2. **representation-002** (separate protocol), three arms:
   - **A:** the frozen N narrative, with no source access;
   - **B:** AEC records plus anchors, `source show` and the fallback `source search`;
   - **C:** the raw corpus with search only.

   It uses newly frozen held-out questions, including unanticipated ones written after the representations are built, and a fact inventory drawn independently from the corpus. Record-directed and fallback retrieval are logged separately within arm B. Build and read costs are reported separately.
