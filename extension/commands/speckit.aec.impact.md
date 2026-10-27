---
description: "AEC: structural diff of the code and the conclusions it affects"
---

# AEC impact

**Do not modify** Spec Kit artifacts, records or code. Report findings only. Decisions are flagged for their owner, never declared invalid.

## Locate AEC

Run commands as `python -m aec …`. If `import aec` fails, try `PYTHONPATH="$AEC_HOME/src"` (where `AEC_HOME` is a checkout of https://github.com/eraevous/AEC). If neither works, say AEC is not installed (`pip install git+https://github.com/eraevous/AEC`) and stop. Do not fail silently.

## Steps

1. If `.aec/edges.jsonl` exists, copy it to `.aec/edges.prev.jsonl`. Then run `python -m aec edges . -o .aec/edges.jsonl`.
2. If there was a previous snapshot:
   - `python -m aec edges --diff .aec/edges.prev.jsonl .aec/edges.jsonl`: show the structural diff.
   - If `.aec/records.jsonl` exists: `python -m aec code-impact .aec/records.jsonl .aec/edges.prev.jsonl .aec/edges.jsonl`
3. Report the diff summary, then the affected conclusions by status (unjustified, stale, needs_review, …) with their explanation paths. Say plainly when nothing is affected.
4. Recommend the follow-up for each stale or unjustified item, such as re-examining a claim or asking the owner about a decision. Do not apply it.
