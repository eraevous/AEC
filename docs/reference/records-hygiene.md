# Records hygiene: duplicate lines after a merge (spec 006)

Two branches that append the same record line leave, once merged, a second byte-identical copy
of it. Lines are compared exactly as written: a copy that differs only in leading or trailing
whitespace, or ends in CRLF where the other ends in LF, is not identical. `check` reads the copy as the same record, loads it once, and reports a warning:

```
[WARNING] duplicate-line: R-merge@1: line 5 repeats line 3 exactly; read as one record (...)
```

The build does not fail. The same `id@version` with **any** difference in its line (different
content, the same JSON written with other spacing or key order, surrounding whitespace, or a
different line ending) is still the error `unique`:
a version was reused, and only its author can say which statement stands.

## Removing the copy (optional)

No Telosmith command rewrites a records file: record lines are append-only (AGENTS.md,
Constitution II), and deleting ledger lines with a tool would need its own owner decision.
The copy is harmless to leave. **Removing it is the owner's call:** the procedure below describes how,
for the owner or someone the owner has explicitly authorized for that copy; it is not itself an
authorization, and an agent or contributor must not delete ledger lines on the strength of this page.
To remove it by hand, in a pull request:

1. Run `check` and note the later line number in the `duplicate-line` warning (the earlier line is kept).
2. Confirm the two lines are byte-identical, e.g. `sed -n '3p;5p' .aec/records.jsonl | uniq | wc -l` prints `1`
   (`sed` and `uniq` keep trailing spaces and CR, so a whitespace variant prints `2`).
3. Delete only the later line, e.g. `sed -i '5d' .aec/records.jsonl`, and check that the diff removes exactly one line.
4. Re-run `check`: the warning is gone and no other finding changed.

A merge conflict on the records file usually means both sides appended; keep both sides' lines in
order and let `check` report any exact copy.
