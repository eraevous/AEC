# Intent: extension CI initialization repair, 2026-10-27
@ai-cadence: run
@ai-intent: Exercise real Spec Kit extension installation without requiring an agent executable.

- Run 40436408337 (PR #9, b4edffc) fails at tests/test_extension.py:58,
  during `specify init`, before AEC extension installation; the other 34 tests pass.
- Pinned Spec Kit v1.2.3 checks for the Claude executable when selecting the
  Claude integration. CI installs Spec Kit, not Claude. Its error is printed
  to stdout, which the assertion currently omits.
- Repair only the test setup: use the supported `--ignore-agent-tools` option
  and include stdout in initialization failure diagnostics. Keep the real
  install/remove, hook registration and unchanged-template assertions intact.
- No AEC runtime, extension manifest, purpose records or acceptance criteria change.
  Passing structural tests does not establish purpose preservation or replace
  the planned Data-Guide overhaul with records written before code changes.

Validation:
- Reproduced the original init command with pinned Spec Kit v1.2.3 and no Claude:
  exit 1, `Agent Detection Error` / `claude not found` on stdout; stderr empty.
- With the repair, all 35 tests pass without skips on Python 3.12, including real
  Spec Kit install/remove and clean-venv AEC package installation.
- Ran the remaining CI steps: regenerated this repository's edge snapshot and
  checked both its linked records and the MTG pilot records: zero errors/warnings.
  The two skipped source files are the deliberately invalid syntax fixtures.
- Snapshot output was used for validation only; omit generated snapshot churn
  from this test-harness repair. AEC runtime behavior is unchanged.
