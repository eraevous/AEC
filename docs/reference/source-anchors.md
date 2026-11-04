# Source anchors and offline retrieval (WP-S)

Records may carry optional `rationale` text separately from `text`, and an
`anchors` array on any record type. An anchor observes source integrity and locator
resolution only. It does not establish whether a passage justifies a conclusion,
what it means, or who may accept a decision. Existing records are never rewritten:
append a new version to add an anchor. `impact` and propagation are unchanged.

```json
{"id":"C-example","version":1,"type":"claim","text":"A conclusion","rationale":"A separate reason","anchors":[{"root":"corpus","path":"notes.md","sha256":"<64 hexadecimal characters>","locator":"L12-15","for":"rationale"}]}
```

The SHA-256 is computed on the file's **raw bytes**, without newline, encoding or
other normalization. Uppercase hex is accepted. `L12-15` is 1-based and inclusive;
`L12` selects one line. `q:exact text` selects the first exact occurrence within
one line. `for` defaults to `text`, or may be `rationale`; neither changes the
meaning/status of the record. Malformed digests, locators, anchor shapes or fields
are record errors. Relative anchor paths cannot contain parent traversal or escape
the root. Omit `root` to anchor a file relative to the repository.

Configure named local roots in .aec/sources.json (an optional machine-local file):

```json
{"roots":{"corpus":"../source-notes"}}
```

Root paths may be repo-relative or absolute local paths; source contents stay in
place. The owner's relay-kit records are one such root: `records_root` names its alias
(default `records`) and `$RELAYKIT_RECORDS`, when set, overrides its path; see
docs/integrations/relay-kit.md. No AEC source command writes source files, copies them into this repository,
executes them, or accesses the network. Sources can contain private information;
configuration/access is the caller's responsibility, not a power granted by a hash.
No remote/URL/UNC providers are supported.

```bash
aec check .aec/records.jsonl
aec source show C-example@1 --context 3 --max-lines 80 --max-chars 240
aec source search 'a forgotten fact' --root corpus --max 20
aec source search 'fact.*detail' --regex --root corpus
```

`check` prints each valid anchor's state. A `verified` anchor means matching raw
bytes and a resolving locator; it produces **no finding**. Other filesystem states
are warning findings and do not fail the command:

| State | Observation |
| --- | --- |
| verified | Artifact bytes and locator match |
| missing | No file in an available root; this says nothing about earlier existence |
| mismatch | Bytes differ; the earlier observation is not falsified, but applicability needs review |
| locator_invalid | Bytes match, but the range/quote does not resolve |
| unavailable | Root unconfigured/absent, file unreadable, or symlink escapes the read boundary; cannot check here |

Malformed records still fail `check`, as do its pre-existing errors. A digest
mismatch takes precedence over locator resolution; show may display a currently
resolving passage from changed bytes, with a warning. An unresolved locator has no
passage to display. Missing/unavailable sources never yield a passage.

`source show` labels record, zero-based anchor index, field, state, path and
locator. Context defaults to 3 lines; `--context` is nonnegative. `--max-lines`
defaults to 80 and must be positive: each passage, including context, is capped
and omitted lines are explicitly counted. Each source line is also capped by
`--max-chars` (default 240, positive), including character-omission markers but
excluding the line-number prefix. Quote-anchored lines use a window around the
first exact quote; range-anchored and context lines show a bounded prefix. Long
quotes can themselves be clipped, and tiny budgets can yield only `…`. Short
lines are unchanged. UTF-8 replacement decoding is used only
for views, never for the digest; CRLF files keep the same logical line numbering.

`source search` scans named configured roots directly even if no record points at
the matching text or no default records file exists. Every matching line is
labelled `fallback`, with displayed path, line number, current raw-byte SHA-256 and
two separate record lists: `records_digest_match` names record versions with an
anchor digest equal to these current bytes; `records_path_only` names record
versions linked to the same path only by different digests. If a record has both
kinds of anchor, it appears only in the digest-match list. Matching a digest alone
does not establish locator validity, interpretation or authority. Literal
matching is default; `--regex` explicitly enables Python regular expressions.
Results sort by path then line, with root alias as a tie-breaker; repeated aliases
can produce separate hits. `--max` defaults to 20, is nonnegative, and reports the
count of matching lines omitted. Zero prints no hits and counts all omissions.
Each hit prints a window around its first match. `--max-chars` defaults to 240 and
must be positive; the bound includes the excerpt and its `…[+N chars]` markers,
but excludes path/digest/record metadata. Markers count characters omitted on each
side. Short lines are unchanged. A match wider than the budget is itself clipped;
very small budgets that cannot fit detailed markers produce only `…`.

`--root` selects a configured alias. The implicit repository root is selected
explicitly with `--root .`; it is not scanned by default. Unknown aliases are
usage errors. Search never follows directory symlinks; in-root file symlinks are
readable, while escaping ones and unreadable paths get visibility notes. No
persistent index is created. Output bounds limit passage lines, per-line passage characters, search hits and search excerpt characters,
not input file size or regex execution time; use basic fallback search on suitable local source roots.

Both source subcommands accept `--repo ROOT` (default current directory) and
`--records PATH` (default ROOT/.aec/records.jsonl; an explicit relative path uses
the current directory). `check --repo ROOT` overrides source configuration lookup;
otherwise records under .aec/ imply their repository parent, and other paths use
the current directory. Relative root configuration stays relative in displayed
paths. Invalid configuration, regexes, references or limits are usage errors.

(From a source checkout without installing, `PYTHONPATH=src python3 -m aec …` works the same.)
