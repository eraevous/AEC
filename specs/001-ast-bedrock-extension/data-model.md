# Data model

## Edge (one JSON line)
| field | type | notes |
|---|---|---|
| `kind` | `defines` \| `calls` \| `imports` \| `inherits` \| `references` | |
| `src` | dotted symbol | the module, class or function where it occurs |
| `dst` | dotted symbol, or `?<expr>` | resolved target, or an unresolved expression |
| `resolved` | bool | false only for `?` targets |
| `file` | posix path relative to the root | |
| `line` | int | |
| `body_sha` | hex (12) | on `defines` only: a hash of the defined node's source segment |

Identity = (`kind`, `src`, `dst`). Location fields are informational.

## Snapshot header (the first line)
`{"aec_edges": 1, "tool_version": "0.2.0", "root": ".", "files": N, "files_sha": "<sha256 of sorted file hashes>", "skipped": [{"file":..,"reason":..}]}`

## Structural diff
`{"added": [edge…], "removed": [edge…], "defs_added": [sym…], "defs_removed": [sym…], "defs_changed": [sym…]}`.
`defs_changed` means the same symbol with a different `body_sha`.

## Code reference (in records)
A relation target of the form `code:<dotted>` (for example `{"rel":"implements","to":"code:pkg.mod.func"}`). It is not version-
pinned; the edge snapshot supplies the current state. `aec check --edges SNAPSHOT` reports any `code:` target not
defined in the snapshot.

## Change events produced by code-impact
- A symbol in `defs_removed` that records reference → `{"change":"retract","target":"code:<sym>"}`.
- A symbol in `defs_changed`, or whose outgoing edges were added or removed, that records reference →
  `{"change":"revise","target":"code:<sym>"}` with no authorization (stale until someone reviews it).
Code references are treated as pseudo-records of type `source` so the existing impact semantics apply unchanged.
