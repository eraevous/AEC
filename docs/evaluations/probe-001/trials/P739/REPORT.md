# Report

## Changed
- `src/understanding/workflow.py`: `understand()` now returns the artifact dict (the same object serialized to guide-profile.json). Files are written exactly as before. The old build-and-write logic moved into a new `write_understanding()`, which returns `(artifact, paths)`. `understand()` is a thin wrapper that returns only the artifact.
- `src/cli.py`: the `understand` and `demo` commands print the written file paths from the return value. They now call `write_understanding` and unpack `(_, paths)`, so CLI output is unchanged.

Tests: 89 passed.

## Notes for the requester
- This is a breaking change to the return type of `understand()`. Any external code that used the paths dict will break. In this repo the only callers were the two CLI commands, which are updated. `docs/prototype/acceptance_fertility.py` ignores the return value.
- If you still need the paths from a notebook, use `write_understanding()`. The paths are also deterministic: `out_dir/guide-profile.json`, `guide-report.md` and `guide-report.html`.
- The returned dict is the in-memory artifact, not a re-read of the JSON. If it contains non-JSON-native types (for example tuples), they could differ from `json.loads` of the file. I didn't check for this.
- I added no new tests for the return value.
