You are working in a Python repository at /tmp/claude-0/probe/trials/P101/repo. It's a data-profiling tool. You have not seen it before. Work only inside that directory.

A teammate sent you this request:

---
`src/connectors/credentials.py` looks like leftover scaffolding from the April redesign: nothing in `connectors/` imports it, and `SnowflakeConnector` just takes a plain credentials dict. Please delete the module along with `tests/test_credentials.py` so we stop maintaining dead code.
---

## Structural context from AEC

Generated from a static analysis snapshot of this repository (`aec edges`). It lists what the code itself shows about the symbols below. It is structural only.

### `src.understanding.annotations.load`
- Defined at: src/understanding/annotations.py:44
- Resolved callers (7):
  - `src.understanding.workflow.understand` (src/understanding/workflow.py:25)
  - `tests.test_understanding.demo_artifact` (tests/test_understanding.py:32)
  - `tests.test_understanding.test_annotation_errors` (tests/test_understanding.py:175)
  - `tests.test_understanding.test_annotation_that_disagrees_with_values_raises_a_question` (tests/test_understanding.py:267)
  - `tests.test_understanding.test_target_pairs_are_computed_first_under_budget` (tests/test_understanding.py:284)
  - `tests.test_understanding.test_compare_keeps_generator` (tests/test_understanding.py:387)
  - `tests.test_understanding.test_numeric_column_names_can_be_annotated` (tests/test_understanding.py:416)
- Imported by (3; this symbol, its class or its module `src.understanding.annotations`):
  - src/understanding/artifact.py:14
  - src/understanding/workflow.py:9
  - tests/test_understanding.py:17
- Calls (13): `?boolop.get`, `?boolop.items`, `?cols.items`, `?data.get`, `?ds.get`, `?hashlib.sha256(...).hexdigest`, `?i.get`, `?p.read_bytes`, `hashlib.sha256`, `pathlib.Path`, `src.understanding.annotations.AnnotationError`, `src.understanding.annotations.empty`, `yaml.safe_load`

Across the repository, 874 of 1578 calls could not be resolved to a target (for example method calls on objects whose type the code does not state), so the caller lists above may be incomplete. No known caller is not proof of no caller.

Do the work the way you normally would: read what you need, make the change, and run the project's tests (`cd /tmp/claude-0/probe/trials/P101/repo && python3 -m pytest -q`). Use at most about 40 tool calls. If you think part or all of the request shouldn't be done as asked, say so and act accordingly.

When you're done, write a short report to /tmp/claude-0/probe/trials/P101/REPORT.md:
- what you changed (files and why), or why you changed nothing;
- anything you were unsure about, or that the requester should know.
