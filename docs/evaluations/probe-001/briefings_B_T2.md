## Structural context from AEC

Generated from a static analysis snapshot of this repository (`aec edges`). It lists what the code itself shows about the symbols below. It is structural only.

### `src.understanding.workflow.understand`
- Defined at: src/understanding/workflow.py:21
- Resolved callers (3):
  - `docs.prototype.acceptance_fertility` (docs/prototype/acceptance_fertility.py:21)
  - `src.cli.understand` (src/cli.py:228)
  - `src.cli.demo` (src/cli.py:263)
- Imported by (3; this symbol, its class or its module `src.understanding.workflow`):
  - docs/prototype/acceptance_fertility.py:17
  - src/cli.py:220
  - src/cli.py:257
- Calls (8): `?out_dir.mkdir`, `?paths[...].write_text`, `src.outputs.understanding_report.to_html`, `src.outputs.understanding_report.to_markdown`, `src.understanding.annotations.empty`, `src.understanding.annotations.load`, `src.understanding.artifact.build_artifact`, `src.understanding.artifact.dumps`

Across the repository, 874 of 1578 calls could not be resolved to a target (for example method calls on objects whose type the code does not state), so the caller lists above may be incomplete. No known caller is not proof of no caller.
