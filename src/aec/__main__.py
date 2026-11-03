"""Telosmith command line (formerly AEC; `aec` still works). Results are structural: they report what the records and code say, not whether a conclusion is true.

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

from . import __version__
from . import edges as E
from .impact import impact, render
from .records import Store, check


def _changes(path: str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("//")]


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


def _prog() -> str:
    """Help and errors name the command the user typed: `telosmith`, or `aec`, its pre-0.5 alias."""
    name = Path(sys.argv[0]).name if sys.argv and sys.argv[0] else ""
    return "aec" if name.startswith("aec") else "telosmith"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog=_prog(), description=__doc__.split("\n\n")[0])
    ap.add_argument("--version", action="version", version="%(prog)s " + __version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("edges", help="extract the dependency graph of a Python working tree (like `snapshot`), or diff two")
    e.add_argument("root", nargs="?", default=".")
    e.add_argument("-o", "--output")
    e.add_argument("--legacy-csv")
    e.add_argument("--diff", nargs=2, metavar=("OLD", "NEW"))
    e.add_argument("--json", action="store_true")
    e.add_argument("--allow-method-mismatch", action="store_true")
    c = sub.add_parser("check", help="check record invariants; with --edges, also dangling code references")
    c.add_argument("records")
    c.add_argument("--edges")
    c.add_argument("--repo", help="source config root (default: records under .aec/, otherwise cwd)")
    i = sub.add_parser("impact", help="classify which conclusions a set of record changes affects")
    i.add_argument("records")
    i.add_argument("changes")
    i.add_argument("--json", action="store_true")
    ci = sub.add_parser("code-impact", help="derive change events from two edge snapshots and report affected conclusions")
    ci.add_argument("records")
    ci.add_argument("old")
    ci.add_argument("new")
    ci.add_argument("--json", action="store_true")
    it = sub.add_parser("init", help="scaffold .aec/ in a repository (never overwrites)")
    it.add_argument("root", nargs="?", default=".")
    it.add_argument("--owner", help="name for the authority stub (default: git user.name, else 'owner')")
    ip = sub.add_parser("import-purpose", help="import Codex++ purpose files as provisional, source-linked records")
    ip.add_argument("root", nargs="?", default=".")
    ip.add_argument("--dir", default="codex_++/purpose_files", help="purpose-file directory, relative to ROOT")
    ip.add_argument("--records", help="default: ROOT/.aec/records.jsonl")
    ip.add_argument("--edges", help="default: a fresh snapshot of ROOT")
    ip.add_argument("--dry-run", action="store_true", help="report only; append nothing")
    source = sub.add_parser("source", help="offline source integrity and retrieval")
    source_sub = source.add_subparsers(dest="source_cmd", required=True)
    show = source_sub.add_parser("show", help="print the passages a record's source anchors point to")
    show.add_argument("record_ref")
    show.add_argument("--context", type=int, default=3)
    show.add_argument("--max-lines", type=int, default=80)
    show.add_argument("--max-chars", type=int, default=240, help="maximum characters per source line, including truncation markers (default: 240)")
    show.add_argument("--repo", default=".", help="repository containing .aec/sources.json")
    show.add_argument("--records", help="record file (default: ROOT/.aec/records.jsonl)")
    search = source_sub.add_parser("search", help="search configured source roots directly", description="Search named configured roots by default; use --root to select one.")
    search.add_argument("pattern")
    search.add_argument("--root", help="configured alias, or . for the repository; default: named roots only")
    search.add_argument("--regex", action="store_true")
    search.add_argument("--max", type=int, default=20, dest="max_hits")
    search.add_argument("--max-chars", type=int, default=240, help="maximum characters per hit excerpt, including truncation markers (default: 240)")
    search.add_argument("--repo", default=".", help="repository containing .aec/sources.json")
    search.add_argument("--records", help="record file (default: ROOT/.aec/records.jsonl)")
    snap_parser = sub.add_parser("snapshot", help="snapshot a working tree or local git revision")
    snap_parser.add_argument("root", nargs="?", default=".")
    snap_parser.add_argument("--rev")
    snap_parser.add_argument("-o", "--output")
    diff_parser = sub.add_parser("diff", help="compare merge-base/head with one extraction method")
    diff_parser.add_argument("--base")
    diff_parser.add_argument("--head")
    diff_parser.add_argument("--base-snapshot")
    diff_parser.add_argument("--head-snapshot")
    diff_parser.add_argument("--allow-method-mismatch", action="store_true")
    diff_parser.add_argument("--repo", default=".")
    diff_parser.add_argument("--json", action="store_true")
    reach_parser = sub.add_parser("reach", help="known structural reach in one projection")
    reach_parser.add_argument("symbol")
    reach_parser.add_argument("--direction", choices=("callers", "callees"), default="callers")
    reach_parser.add_argument("--projection", choices=("calls", "imports", "inherits"), default="calls")
    reach_parser.add_argument("--depth", type=int, default=1)
    fan_parser = sub.add_parser("fan", help="fan-in/out by distinct neighbors in one projection")
    fan_parser.add_argument("--projection", choices=("calls", "imports"), default="calls")
    fan_parser.add_argument("--top", type=int, default=20)
    from .graph import WHY
    unresolved_parser = sub.add_parser("unresolved", help="retrieve unresolved calls by reason")
    unresolved_parser.add_argument("--why", choices=WHY, nargs="+", action="append")
    unresolved_parser.add_argument("--in", dest="scope")
    for parser in (reach_parser, fan_parser, unresolved_parser):
        parser.add_argument("--repo", default=".")
        parser.add_argument("--rev")
        parser.add_argument("--json", action="store_true")
    return ap


def _cmd_snapshot(a, ap) -> int:
    try:
        text = E.dumps(E.snapshot(a.root, rev=a.rev))
        if a.output:
            Path(a.output).parent.mkdir(parents=True, exist_ok=True)
            Path(a.output).write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
    except (OSError, ValueError) as error:
        ap.error(str(error))
    return 0


def _diff_report(a) -> dict:
    from .snapshots import compare_revisions, structural_diff
    if a.base_snapshot or a.head_snapshot:
        if not (a.base_snapshot and a.head_snapshot) or a.base or a.head:
            raise ValueError("provide both stored snapshots, without revision arguments")
        return structural_diff(E.load(a.base_snapshot), E.load(a.head_snapshot),
                               allow_method_mismatch=a.allow_method_mismatch)
    if a.allow_method_mismatch:
        raise ValueError("method override is for stored-snapshot comparisons only")
    return compare_revisions(a.repo, base=a.base or "origin/main", head=a.head or "HEAD")


def _cmd_diff(a, ap) -> int:
    try:
        report = _diff_report(a)
        if a.json:
            print(json.dumps({"comparison": report["comparison"], **report}, indent=2))
        else:
            if report.get("method_comparison"):
                print("METHOD COMPARISON: compares methods, not just code")
            print("# aec diff (structural)")
            print(json.dumps(report, indent=2))
    except (OSError, ValueError) as error:
        ap.error(str(error))
    return 0


def _cmd_query(a, ap) -> int:
    """reach, fan and unresolved: read-only queries over one snapshot."""
    from .graph import fan, reach, render_query, unresolved
    try:
        snap = E.snapshot(a.repo, rev=a.rev)
        if a.cmd == "reach":
            report = reach(snap, a.symbol, direction=a.direction, projection=a.projection, depth=a.depth)
        elif a.cmd == "fan":
            report = fan(snap, projection=a.projection, top=a.top)
        else:
            reasons = [item for group in (a.why or []) for item in group]
            report = {"label": "structural", "edges": unresolved(snap, why=reasons, scope=a.scope)}
        print(json.dumps(report, sort_keys=True, indent=2) if a.json or a.cmd == "unresolved" else render_query(report))
    except (OSError, ValueError) as error:
        ap.error(str(error))
    return 0


def _cmd_source(a, ap) -> int:
    from .sources import SourceContext, render_search, render_show
    repo = Path(a.repo)
    records = Path(a.records) if a.records else repo / ".aec/records.jsonl"
    try:
        source_store = Store.load(records) if records.exists() else Store([])
        context = SourceContext(repo)
        if a.source_cmd == "show":
            text = render_show(source_store, a.record_ref, context, context=a.context, max_lines=a.max_lines, max_chars=a.max_chars)
        else:
            text = render_search(source_store, a.pattern, context, root=a.root,
                                 regex=a.regex, max_hits=a.max_hits, max_chars=a.max_chars)
    except (OSError, ValueError) as error:
        ap.error(str(error))
    print(text, end="")
    return 0


def _cmd_init(a, ap) -> int:
    from .init import init
    rep = init(a.root, owner=a.owner or _git_user(a.root) or "owner")
    for f in rep["created"]:
        print(f"created {f}")
    for f in rep["kept"]:
        print(f"kept    {f} (exists; not overwritten)")
    print("\nNext steps:\n" + "\n".join(f"  - {x}" for x in rep["next_steps"].splitlines()))
    return 0


def _cmd_import_purpose(a, ap) -> int:
    from .purpose_import import import_purpose
    from .purpose_import import render as render_import
    root = Path(a.root)
    if not (root / a.dir).is_dir():
        print(f"aec import-purpose: no purpose-file directory {root / a.dir} (use --dir)", file=sys.stderr)
        return 2
    rep = import_purpose(root, root / a.dir, Path(a.records) if a.records else root / ".aec" / "records.jsonl",
                         E.load(a.edges) if a.edges else E.snapshot(root), dry_run=a.dry_run)
    print(render_import(rep))
    return 0


def _cmd_edges(a, ap) -> int:
    if a.diff:
        try:
            d = E.diff(E.load(a.diff[0]), E.load(a.diff[1]), allow_method_mismatch=a.allow_method_mismatch)
        except (OSError, ValueError) as error:
            ap.error(str(error))
        print(json.dumps(d, indent=1) if a.json else E.render_diff(d))
        return 0
    root = Path(a.root)
    if not root.is_dir():
        print(f"aec edges: {root} is not a directory", file=sys.stderr)
        return 2
    try:
        snap = E.snapshot(root)
    except E.SourceChanged as error:
        print(f"aec edges: {error}", file=sys.stderr)
        return 2
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


def _cmd_check(a, ap) -> int:
    store = Store.load(a.records)
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


def _cmd_impact(a, ap) -> int:
    store = Store.load(a.records)
    _print_impact(store, impact(store, _changes(a.changes)), a.json)
    return 0


def _cmd_code_impact(a, ap) -> int:
    store = Store.load(a.records)
    from .code_impact import code_impact
    try:
        rep, events = code_impact(store, E.load(a.old), E.load(a.new))
    except ValueError as error:
        ap.error(str(error))
    if not a.json:
        print(f"# derived {len(events)} change event(s) from the structural diff")
    _print_impact(store, rep, a.json)
    return 0


HANDLERS = {
    "edges": _cmd_edges, "check": _cmd_check, "impact": _cmd_impact, "code-impact": _cmd_code_impact,
    "init": _cmd_init, "import-purpose": _cmd_import_purpose, "source": _cmd_source,
    "snapshot": _cmd_snapshot, "diff": _cmd_diff, "reach": _cmd_query, "fan": _cmd_query, "unresolved": _cmd_query,
}


def main(argv=None) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    return HANDLERS[a.cmd](a, ap)


if __name__ == "__main__":
    sys.exit(main())
