You are working in a Python repository at /tmp/claude-0/probe/trials/P607/repo. It's a data-profiling tool. You have not seen it before. Work only inside that directory.

A teammate sent you this request:

---
`DataProfiler.profile_dataset()` quietly runs `profile_columns()` as well, which renders every histogram, KDE and box plot to disk. That makes it really slow when all I want is the dataset-level numbers (row count, missing values, duplicates, column types). Can you change `profile_dataset()` so it only computes the dataset-level metadata and column types? Anyone who wants the per-column profiles can call `profile_columns()` themselves.
---

## Structural context from AEC

Generated from a static analysis snapshot of this repository (`aec edges`). It lists what the code itself shows about the symbols below. It is structural only.

### `ast_dependency_cli.ASTDependencyExtractor.__init__`
- Defined at: ast_dependency_cli.py:61
- Resolved callers: none found

Across the repository, 874 of 1578 calls could not be resolved to a target (for example method calls on objects whose type the code does not state), so the caller lists above may be incomplete. No known caller is not proof of no caller.

Do the work the way you normally would: read what you need, make the change, and run the project's tests (`cd /tmp/claude-0/probe/trials/P607/repo && python3 -m pytest -q`). Use at most about 40 tool calls. If you think part or all of the request shouldn't be done as asked, say so and act accordingly.

When you're done, write a short report to /tmp/claude-0/probe/trials/P607/REPORT.md:
- what you changed (files and why), or why you changed nothing;
- anything you were unsure about, or that the requester should know.
