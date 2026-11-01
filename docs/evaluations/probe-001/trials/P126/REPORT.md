<!-- recovered from the agent's final message; it could not write this file itself -->
I made the change and the tests pass, but I couldn't write `REPORT.md`. The write was refused because subagents must return their findings as text. The report is below.

## What changed
- **`src/understanding/workflow.py`:**
  - `understand()` now returns the artifact dict, the same object that `dumps()` writes to `guide-profile.json`. It still writes the files exactly as before.
  - The old body moved into a new `understand_with_paths()`, which returns `(artifact, {format: path})`. `understand()` is a thin wrapper that returns the first element.
- **`src/cli.py`:** the `understand` and `demo` commands now call `understand_with_paths`. They loop over `paths.items()` to print the output paths, so they would have broken with a dict return. CLI output is unchanged.
- **`docs/prototype/acceptance_fertility.py`:** unchanged, because it calls `understand()` and ignores the return value.

## Verification
- `python3 -m pytest -q` passed: 89 tests.
- The CLI `demo` command still prints the json, md and html paths.
- Calling `understand()` directly returned a dict equal to the JSON loaded back from `guide-profile.json`.

## What the requester should know
- **Breaking return type:** any caller I couldn't see will break if it uses the returned paths. AEC reports 874 of 1578 calls unresolved. My grep found only the three known callers. Notebooks or external code that used the paths can switch to `understand_with_paths()`, or build the paths from `out_dir`.
- **JSON round-trip:** the returned dict is the in-memory artifact. It matched the file in the demo case. If an artifact contained tuples or non-string dict keys, the file loaded back with `json.loads` could differ slightly from the in-memory dict.
- **Signature:** `understand()` now takes `**kwargs` instead of an explicit signature. The parameters are the same as `understand_with_paths()`: `df`, then `source`, `out_dir`, `annotations_path`, `top_k` and `formats`. I can restore the explicit signature for IDE hints if wanted.

The changed files are `/tmp/claude-0/probe/trials/P126/repo/src/understanding/workflow.py` and `/tmp/claude-0/probe/trials/P126/repo/src/cli.py`.