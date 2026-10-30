"""AEC command line. All results are structural (Constitution IV).

  python -m aec edges [ROOT] [-o FILE] [--legacy-csv FILE]   edge snapshot of a Python tree
  python -m aec edges --diff OLD NEW [--json]                 structural diff of two snapshots
  python -m aec check RECORDS [--edges SNAPSHOT]              cross-record checks (+ dangling code: refs)
  python -m aec impact RECORDS CHANGES [--json]               which conclusions a change affects
  python -m aec code-impact RECORDS OLD NEW [--json]          code change -> affected conclusions
  python -m aec init [ROOT] [--owner NAME]                    scaffold .aec/ (never overwrites)
  python -m aec import-purpose [ROOT] [--dir D] [--dry-run]   Codex++ .purpose.md -> provisional records
  python -m aec source show REF [--context N]                read anchored passages (offline)
  python -m aec source search PATTERN [--root R] [--regex]   direct fallback source search (offline)
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


def _git_user(root) -> str | None:
    import subprocess
    try:
        out = subprocess.run(["git", "-C", str(root), "config", "user.name"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


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
    c.add_argument("--repo", help="source config root (default: records under .aec/, otherwise cwd)")
    i = sub.add_parser("impact")
    i.add_argument("records")
    i.add_argument("changes")
    i.add_argument("--json", action="store_true")
    ci = sub.add_parser("code-impact")
    ci.add_argument("records")
    ci.add_argument("old")
    ci.add_argument("new")
    ci.add_argument("--json", action="store_true")
    it = sub.add_parser("init")
    it.add_argument("root", nargs="?", default=".")
    it.add_argument("--owner", help="name for the authority stub (default: git user.name, else 'owner')")
    ip = sub.add_parser("import-purpose")
    ip.add_argument("root", nargs="?", default=".")
    ip.add_argument("--dir", default="codex_++/purpose_files", help="purpose-file directory, relative to ROOT")
    ip.add_argument("--records", help="default: ROOT/.aec/records.jsonl")
    ip.add_argument("--edges", help="default: a fresh snapshot of ROOT")
    ip.add_argument("--dry-run", action="store_true", help="report only; append nothing")
    source = sub.add_parser("source", help="offline source integrity and retrieval")
    source_sub = source.add_subparsers(dest="source_cmd", required=True)
    show = source_sub.add_parser("show")
    show.add_argument("record_ref")
    show.add_argument("--context", type=int, default=3)
    show.add_argument("--max-lines", type=int, default=80)
    show.add_argument("--repo", default=".", help="repository containing .aec/sources.json")
    show.add_argument("--records", help="record file (default: ROOT/.aec/records.jsonl)")
    search = source_sub.add_parser("search")
    search.add_argument("pattern")
    search.add_argument("--root", help="configured root alias, or . for the repository")
    search.add_argument("--regex", action="store_true")
    search.add_argument("--max", type=int, default=20, dest="max_hits")
    search.add_argument("--repo", default=".", help="repository containing .aec/sources.json")
    search.add_argument("--records", help="record file (default: ROOT/.aec/records.jsonl)")
    a = ap.parse_args(argv)

    if a.cmd == "source":
        from .sources import SourceContext, render_search, render_show
        repo = Path(a.repo)
        records = Path(a.records) if a.records else repo / ".aec/records.jsonl"
        try:
            source_store = Store.load(records) if records.exists() else Store([])
            context = SourceContext(repo)
            if a.source_cmd == "show":
                text = render_show(source_store, a.record_ref, context, context=a.context, max_lines=a.max_lines)
            else:
                text = render_search(source_store, a.pattern, context, root=a.root,
                                     regex=a.regex, max_hits=a.max_hits)
        except (OSError, ValueError) as error:
            ap.error(str(error))
        print(text, end="")
        return 0
    if a.cmd == "init":
        from .init import init
        rep = init(a.root, owner=a.owner or _git_user(a.root) or "owner")
        for f in rep["created"]:
            print(f"created {f}")
        for f in rep["kept"]:
            print(f"kept    {f} (exists; not overwritten)")
        print("\nNext steps:\n" + "\n".join(f"  - {x}" for x in rep["next_steps"].splitlines()))
        return 0
    if a.cmd == "import-purpose":
        from .purpose_import import import_purpose, render as render_import
        root = Path(a.root)
        if not (root / a.dir).is_dir():
            print(f"aec import-purpose: no purpose-file directory {root / a.dir} (use --dir)", file=sys.stderr)
            return 2
        rep = import_purpose(root, root / a.dir, Path(a.records) if a.records else root / ".aec" / "records.jsonl",
                             E.load(a.edges) if a.edges else E.snapshot(root), dry_run=a.dry_run)
        print(render_import(rep))
        return 0

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
        from .sources import SourceContext, render_status
        records_parent = Path(a.records).absolute().parent
        repo = Path(a.repo) if a.repo else records_parent.parent if records_parent.name == ".aec" else Path.cwd()
        context = SourceContext(repo)
        try:
            fs = check(store, edges=snap, sources=context)
        except ValueError as error:
            ap.error(str(error))
        for record in store.records:
            for item in context.inspect_record(record):
                if item.state == "verified":
                    print(render_status(item))
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
