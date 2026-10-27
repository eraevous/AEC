"""AEC command line. All results are structural (Constitution IV).

  python -m aec edges [ROOT] [-o FILE] [--legacy-csv FILE]   edge snapshot of a Python tree
  python -m aec edges --diff OLD NEW [--json]                 structural diff of two snapshots
  python -m aec check RECORDS [--edges SNAPSHOT]              cross-record checks (+ dangling code: refs)
  python -m aec impact RECORDS CHANGES [--json]               which conclusions a change affects
  python -m aec code-impact RECORDS OLD NEW [--json]          code change -> affected conclusions
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import edges as E
from .impact import impact, render
from .records import Store, check


def _changes(path: str) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("//")]


def _print_impact(store, rep, as_json):
    if as_json:
        print(json.dumps({"impacts": [asdict(x) for x in rep.impacts.values()], "findings": rep.findings,
                          "unaffected": rep.unaffected}, indent=1))
    else:
        print(render(store, rep))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="aec", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("edges")
    e.add_argument("root", nargs="?", default=".")
    e.add_argument("-o", "--output")
    e.add_argument("--legacy-csv")
    e.add_argument("--diff", nargs=2, metavar=("OLD", "NEW"))
    e.add_argument("--json", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("records")
    c.add_argument("--edges")
    i = sub.add_parser("impact")
    i.add_argument("records")
    i.add_argument("changes")
    i.add_argument("--json", action="store_true")
    ci = sub.add_parser("code-impact")
    ci.add_argument("records")
    ci.add_argument("old")
    ci.add_argument("new")
    ci.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.cmd == "edges":
        if a.diff:
            d = E.diff(E.load(a.diff[0]), E.load(a.diff[1]))
            print(json.dumps(d, indent=1) if a.json else E.render_diff(d))
            return 0
        root = Path(a.root)
        if not root.is_dir():
            print(f"aec edges: {root} is not a directory", file=sys.stderr)
            return 2
        snap = E.snapshot(root)
        text = E.dumps(snap)
        if a.output:
            Path(a.output).parent.mkdir(parents=True, exist_ok=True)
            Path(a.output).write_text(text, encoding="utf-8")
            h = snap["header"]
            print(f"aec edges: {len(snap['edges'])} edges from {h['files']} files "
                  f"({len(h['skipped'])} skipped) -> {a.output}", file=sys.stderr)
        else:
            sys.stdout.write(text)
        if a.legacy_csv:
            Path(a.legacy_csv).write_text(E.legacy_csv(snap), encoding="utf-8")
        return 0

    store = Store.load(a.records)
    if a.cmd == "check":
        snap = E.load(a.edges) if a.edges else None
        fs = check(store, edges=snap)
        for f in fs:
            print(f"[{f.level.upper()}] {f.rule}: {f.ref}: {f.msg}")
        errors = [f for f in fs if f.level == "error"]
        print(f"aec check: {len(errors)} error(s), {len(fs) - len(errors)} warning(s) (structural)")
        return 1 if errors else 0
    if a.cmd == "impact":
        _print_impact(store, impact(store, _changes(a.changes)), a.json)
        return 0
    if a.cmd == "code-impact":
        from .code_impact import code_impact
        rep, events = code_impact(store, E.load(a.old), E.load(a.new))
        if not a.json:
            print(f"# derived {len(events)} change event(s) from the structural diff")
        _print_impact(store, rep, a.json)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
