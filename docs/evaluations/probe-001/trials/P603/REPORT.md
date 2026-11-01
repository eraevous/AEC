<!-- recovered from the agent's final message; it could not write this file itself -->
I made the change, but I couldn't write `/tmp/claude-0/probe/trials/P603/REPORT.md`. The write tool rejected it because subagents must return findings as text, so the report is below. The full test suite passes (89 tests).

**Changes**
- **`src/understanding/workflow.py`:** `understand()` now returns the artifact dict, the same object it serializes to `guide-profile.json`. It still writes the same three files. The writing logic moved into a new `understand_and_write()`, which returns `(artifact, paths)`, and `understand()` is a thin wrapper around it.
- **`src/cli.py`:** the `understand` and `demo` commands print the output paths by looping over the old return value. With the new return type they would have printed the artifact's contents instead, so both now call `understand_and_write` and unpack `_, paths`.

**Things the requester should know**
- **Breaking change:** this changes the public return type of `understand()`. The only other caller I found is `docs/prototype/acceptance_fertility.py`, which ignores the return value. The caller list from the static analysis may be incomplete, so check any notebooks or external code that use the returned paths. They can switch to `understand_and_write`.
- **Possible mismatch with the file:** I did not check that the returned dict is identical to `json.loads` of the written file. If `dumps` converts types such as numpy values or NaN, the two could differ slightly.
- **Testing:** no existing tests call `understand()` directly, and I added none. A manual run returned a dict and wrote `guide-profile.json`, `guide-report.md` and `guide-report.html`.