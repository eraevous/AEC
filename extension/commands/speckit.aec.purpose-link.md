---
description: "AEC: report whether the active spec cites the purpose it serves"
---

# AEC purpose link

**Do not modify** `spec.md`, `plan.md`, `tasks.md`, the constitution or any record. This command only reports findings, for the people involved to resolve.

## Locate AEC

Run commands as `python -m aec …`. If `import aec` fails, try `PYTHONPATH="$AEC_HOME/src"` (where `AEC_HOME` is a checkout of https://github.com/eraevous/AEC). If neither works, say AEC is not installed (`pip install git+https://github.com/eraevous/AEC`) and stop. Do not fail silently.

## Steps

1. Find the active feature directory (`.specify/feature.json` → `feature_directory`) and read its `spec.md`.
2. Collect every `id@version` token in the spec (for example `AEC-P0@1`, `P-01@2`).
3. If `.aec/records.jsonl` exists, check each token resolves to a record in it. Note any that point at a superseded version (a newer version of the same id exists).
4. Report:
   - **No purpose cited**: the spec names no `purpose` or `requirement` record. Ask which purpose it serves; do not invent one.
   - **Unresolved** tokens and **superseded** versions.
   - Otherwise: "spec cites <ids>; all resolve (structural check only)".
