# DEC-021 mechanism precondition: raw outputs (2026-11-04, before any trial)

Deterministic tool output, run by claude:aec-eval for [the protocol](../dec-021-protocol.md), section "Mechanism precondition". No trial, key or grade exists. K1 was fixed in protocol @1 (commit 195ffba) before these runs and is not re-chosen.

Inputs (hashes in `inputs.sha256`):
- `rec-3367ab3.jsonl` = `git -C Fathom show 3367ab3:.aec/records.jsonl` (92 lines).
- `edges-<tool>-<rev>.json` = `aec edges <tree archive of rev>` at the named Telosmith commit. The base archive is 944f82f, whose tree is identical to the merge base 3b89d7c (tree ae208ca).

Commands (Telosmith checkout as cwd, `PYTHONPATH=src`):
```
python -m aec edges ../fathom-<rev> -o edges-<tool>-<rev>.json
python -m aec code-impact rec-3367ab3.jsonl edges-<tool>-944f82f.json edges-<tool>-3367ab3.json      # arm C records
python3 filter_b.py rec-3367ab3.jsonl recB.jsonl
python -m aec code-impact recB.jsonl edges-<tool>-944f82f.json edges-<tool>-3367ab3.json             # arm B records
```
Tools: 906e8fd (the protocol's pin; `code_impact.py`, `impact.py` and `edges.py` are unchanged on main at 7387f88) and 486da47 (PR #51 head, DN2X gap fixes, unmerged).

| file | what |
|---|---|
| `code-impact-906e8fd-full.txt`, `code-impact-906e8fd-armB.txt` | 23 affected in both; identical statuses. Full records reproduce the historical "Impact reports 23 affected" |
| `code-impact-486da47-full.txt`, `code-impact-486da47-armB.txt` | the same 23, plus 18 structural `reach` pointers, none to `target.relationship_chart` |
| `qual-906e8fd.md`, `qual-486da47.md` | DN2X's frozen link mapping (`code-impact-qual-001`, `sha256sum -c FREEZE.sha256` OK) through the helper, constant and module cases; byte-for-byte the tables in PR #51's `before.md` / `after.md` |

Neither tool names `FT-R7@2` or `FT-R18@1`. Both name `FT-TA-R1@2` and `FT-PO-R1@2` as stale, and `FT-TA-R1@2`'s chain runs via `charts.svg_chart`, not via `target.relationship_chart`, where F01 is.
