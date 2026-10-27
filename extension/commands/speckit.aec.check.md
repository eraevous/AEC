---
description: "AEC: cross-record checks (references, authority, evidence tiers, dangling code references)"
---

# AEC check

**Do not modify** Spec Kit artifacts or records. Report findings only.

## Locate AEC

Run commands as `python -m aec …`. If `import aec` fails, try `PYTHONPATH="$AEC_HOME/src"` (where `AEC_HOME` is a checkout of https://github.com/eraevous/AEC). If neither works, say AEC is not installed (`pip install git+https://github.com/eraevous/AEC`) and stop. Do not fail silently.

## Steps

1. `python -m aec edges . -o .aec/edges.jsonl`: refresh the structural snapshot of the code (fast, deterministic).
2. `python -m aec check .aec/records.jsonl --edges .aec/edges.jsonl`
3. Report the findings verbatim, grouped as errors and warnings. Label the result **structural**: passing does not show the purpose is preserved.
4. If `.aec/records.jsonl` does not exist, report that AEC records are not set up and point to `docs/reasoning-vocabulary.md` in the AEC repo. Do not create records.
