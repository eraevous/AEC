"""AEC command line.

  python -m aec check  RECORDS.jsonl            cross-record checks (references, authority, evidence tiers)
  python -m aec impact RECORDS.jsonl CHANGES.jsonl [--json]
                                                which conclusions a change leaves unjustified, stale,
                                                to re-baseline, or merely exploratory
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .impact import impact, render
from .records import Store, check


def _changes(path: str) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("//")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="aec", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("records")
    i = sub.add_parser("impact")
    i.add_argument("records")
    i.add_argument("changes")
    i.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    store = Store.load(a.records)
    if a.cmd == "check":
        fs = check(store)
        for f in fs:
            print(f"[{f.level.upper()}] {f.rule}: {f.ref}: {f.msg}")
        errors = [f for f in fs if f.level == "error"]
        print(f"aec check: {len(errors)} error(s), {len(fs) - len(errors)} warning(s)")
        return 1 if errors else 0
    rep = impact(store, _changes(a.changes))
    if a.json:
        print(json.dumps({"impacts": [asdict(x) for x in rep.impacts.values()], "findings": rep.findings,
                          "unaffected": rep.unaffected}, indent=1))
    else:
        print(render(store, rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
