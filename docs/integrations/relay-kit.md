# Telosmith with relay-kit

[relay-kit](https://github.com/eraevous/relay-kit) owns coordination mechanics (handoffs, delivery,
IDs, the decision and challenge ledgers); Telosmith owns development semantics (DEC-018). The one
canonical decision record lives in the owner's relay-kit records, a repository made with
`relay-kit init`. Telosmith references it rather than copying it: a projected decision in
`.aec/records.jsonl` carries an anchor into the records' `governance/decisions.jsonl`, and
`aec check` reports that anchor as `verified`, `mismatch`, `missing` or `unavailable`.

Telosmith stays standard-library only. It never imports relay-kit; it only reads the records' files,
offline and read-only, like any other source root.

## Install relay-kit (pinned)

```bash
pip install "relay-kit @ git+https://github.com/eraevous/relay-kit@a7fa03a362ca1c0cd6dc911bec4d9f0b54f9bf7e"
relay-kit init ../my-records --owner <your name>
```

The pin is relay-kit's `main` after eraevous/relay-kit#13 (version 0.1.0, 134 tests passing).
When the `v0.1.0` tag is published, replace the commit with `@v0.1.0` on this one line; this is the
only place Telosmith names a relay-kit version (a test checks that every reference agrees).

## Where Telosmith finds your records

The records are one named source root. Two settings decide which alias and where:

| Setting | Where | Default |
| --- | --- | --- |
| `records_root`: the alias your anchors use for the records | `.aec/sources.json` | `records` |
| the records' location | `$RELAYKIT_RECORDS`, else `roots[<records_root>]` in `.aec/sources.json` | none |

Precedence for the location: **`RELAYKIT_RECORDS`** (the same variable relay-kit's own tools read;
a relative path is taken from the working directory, as relay-kit does) **over** the path in
`.aec/sources.json` (relative to the repository). The variable moves only the records root, never
other roots. An empty value is ignored.

```json
{"roots": {"records": "../my-records"}}
```

or, without a config file, `export RELAYKIT_RECORDS=~/src/my-records`, and anchor with
`"root": "records"`.

If the location is unset, absent on this machine, or not a usable local path, anchors into the records
report `unavailable` (a warning; `check` still exits 0). Telosmith never looks for a sibling
checkout it was not told about.

**Zach's instance.** Zach's records are his relay-kit-private repository, checked out beside
Telosmith. This repository's `.aec/sources.json` keeps that layout as its default
(`"records_root": "relay-kit-private"`, `"relay-kit-private": "../relay-kit-private"`), so its
existing anchors are unchanged. In CI that root is absent and those anchors report `unavailable`.
