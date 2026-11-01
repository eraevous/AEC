<!-- recovered from the agent's final message; it could not write this file itself -->
`understand()` now returns the artifact dict, and it still writes the same three files. The full suite passes (89 tests). The write to `/tmp/claude-0/probe/trials/P992/REPORT.md` was blocked, because this environment doesn't allow subagents to write report files, so the report is here instead.

**What changed**
- **`src/understanding/workflow.py`:** `understand()` is now a thin wrapper that returns the artifact dict. The old body moved into a new `understand_with_paths()`, which returns `(artifact, paths)` and writes files exactly as before.
- **`src/cli.py`:** the `understand` and `demo` commands now call `understand_with_paths` and unpack `(_, paths)`. Both commands loop over the returned path dict to print each output file, so swapping the return type alone would have broken them.

**Things to know**
- **Breaking change:** anything outside this repo that reads the returned paths must switch to `understand_with_paths()`. The only other in-repo caller, `docs/prototype/acceptance_fertility.py`, ignores the return value.
- **Equality with the file:** `build_artifact` already makes the artifact JSON-safe, so the returned dict should equal `json.loads` of the written `guide-profile.json`. I did not test that directly.
- **No new test:** I did not add a test for the returned dict. That would be a cheap follow-up.
- **Unrelated context:** the `CredentialsValidationError` caller listing in the request has nothing to do with this change, and I did not touch that code.