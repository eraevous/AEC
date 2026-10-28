# CLI contract (`python -m aec`)

| command | input | output | exit |
|---|---|---|---|
| `edges [ROOT] [-o FILE] [--legacy-csv FILE]` | Python source tree | an edge snapshot as JSON lines (stdout or FILE) | 0, or 2 if ROOT is missing |
| `edges --diff OLD NEW [--json]` | two snapshots | structural diff (text or JSON) | 0 |
| `check RECORDS [--edges SNAPSHOT]` | records (+ snapshot) | findings | 1 on errors |
| `impact RECORDS CHANGES [--json]` | records + change events | impact report | 0 |
| `code-impact RECORDS OLD NEW [--json]` | records + two snapshots | impact report for code-linked conclusions | 0 |

All output is labelled structural. None of the commands writes to Spec Kit artifacts.
