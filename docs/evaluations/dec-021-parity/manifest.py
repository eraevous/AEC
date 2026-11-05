"""DEC-021 information-parity manifest (pre-registration, not a Telosmith command).

Usage:
  python3 manifest.py RECORDS.jsonl > manifest.tsv     # build the table from Fathom's records at 3367ab3
  python3 manifest.py RECORDS.jsonl --check manifest.tsv  # the committed table matches the records
  python3 manifest.py RECORDS.jsonl --arms ARMS_DIR       # after the preparer runs: every row is delivered

RECORDS is `git -C <Fathom> show 3367ab3:.aec/records.jsonl`. Every record line and every relation gets a row
saying which arm receives it and in which form. "prose" is docs/project-record.md (the same file in all three
arms); "jsonl" is .aec/records.jsonl (B: filtered, C: full). Computed guidance is listed separately and is
unequal by design. Stdlib only.
"""
import json
import sys
from pathlib import Path

B_TYPES = {"requirement", "evidence", "claim", "decision", "authority"}
B_RELS = {"implemented_by", "observed_on", "depends_on", "supports", "supersedes"}
COLS = ["kind", "from", "rel", "to", "A_prose", "B_prose", "B_jsonl", "C_prose", "C_jsonl"]
GUIDANCE = [  # (output, A, B, C): unequal by design; this is the intervention, not a confound
    ("path-reminder (file-level obligations whose linked files are in the diff)", 1, 0, 0),
    ("aec edges, base and head, one pinned method", 0, 1, 1),
    ("aec check --edges", 0, 1, 1),
    ("aec code-impact base..head with visibility figure", 0, 1, 1),
    ("aec diff", 0, 0, 1),
    ("aec reach/fan/unresolved for every changed symbol", 0, 0, 1),
    ("aec source show for every record code-impact names", 0, 0, 1),
    ("free use of any aec command during the trial", 0, 0, 1),
]


def lines(path):
    for raw in Path(path).read_text().splitlines():
        if raw.strip() and not raw.startswith("//"):
            yield json.loads(raw)


def rows(path):
    out = []
    for r in lines(path):
        ref = f"{r['id']}@{r['version']}"
        kept = r["type"] in B_TYPES
        out.append(["record", ref, r["type"], "", 1, 1, int(kept), 1, 1])
        for e in r.get("relations", []):
            out.append(["relation", ref, e["rel"], e["to"], 1, 1, int(kept and e["rel"] in B_RELS), 1, 1])
    for name, a, b, c in GUIDANCE:
        out.append(["guidance", name, "", "", a, 0, b, 0, c])
    return out


def render(rs):
    return "\t".join(COLS) + "\n" + "".join("\t".join(map(str, r)) + "\n" for r in rs)


def invariants(rs):
    bad = []
    for r in rs:
        if r[0] in ("record", "relation") and not (r[4] == r[5] == r[7] == 1):
            bad.append(f"not in every arm's prose: {r[:4]}")  # equal source evidence
        if r[0] in ("record", "relation") and r[6] and not r[8]:
            bad.append(f"in B's jsonl but not C's: {r[:4]}")
    return bad


def prose_has(text, r):
    """Every record line appears by ref; every relation as one line naming both ends (code: refs as path::symbol)."""
    def show(x):
        return x[len("code:"):] if x.startswith("code:") else x
    if r[0] == "record":
        return r[1] in text
    return any(r[1] in ln and show(r[3]) in ln and r[2] in ln for ln in text.splitlines())


def check_arms(rs, root):
    bad = []
    root = Path(root)
    jsonl = {}
    for arm in "BC":
        p = root / arm / ".aec" / "records.jsonl"
        got = set()
        if p.exists():
            for r in lines(p):
                ref = f"{r['id']}@{r['version']}"
                got.add(("record", ref, r["type"], ""))
                got.update(("relation", ref, e["rel"], e["to"]) for e in r.get("relations", []))
        jsonl[arm] = got
    prose = {arm: (root / arm / "docs" / "project-record.md").read_text() for arm in "ABC"}
    if not (prose["A"] == prose["B"] == prose["C"]):
        bad.append("docs/project-record.md differs between arms")
    for r in rs:
        if r[0] == "guidance":
            continue
        key = tuple(r[:4])
        if not prose_has(prose["A"], r):
            bad.append(f"missing from prose: {key}")
        if bool(r[6]) != (key in jsonl["B"]):
            bad.append(f"B jsonl mismatch: {key}")
        if bool(r[8]) != (key in jsonl["C"]):
            bad.append(f"C jsonl mismatch: {key}")
    return bad


def main(argv):
    rs = rows(argv[1])
    bad = invariants(rs)
    if len(argv) > 3 and argv[2] == "--check":
        if Path(argv[3]).read_text() != render(rs):
            bad.append(f"{argv[3]} does not match the records")
    elif len(argv) > 3 and argv[2] == "--arms":
        bad += check_arms(rs, argv[3])
    else:
        sys.stdout.write(render(rs))
    for b in bad:
        print("PARITY:", b, file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
