"""`aec code-impact`: turn a structural diff of the code into change events, then run `aec impact`.

Records point at code with unversioned `code:<dotted>` references. A referenced symbol that was deleted
is retracted. One whose body changed, or whose outgoing edges were added or removed, is revised without
authorization: dependents become stale until someone re-examines them. A module's body is its own
definitions and module-level statements, as a class's body includes its methods: a link to `code:pkg.mod`
is revised when any of them changes (not when a submodule `pkg.mod.x` does). Unreferenced code changes
produce no events (Constitution IV: structural only; nothing here judges whether the change was right).

Separately, a changed definition that a linked symbol reaches through resolved `calls` or `references`
edges (default: one step) is reported as a review pointer. It assigns no status: a changed callee does not
make the caller's rationale stale (A5RR; what a link means is unchanged). The report also says how many
further symbols lie one step beyond the depth it walked, so a quiet report discloses where it stopped.

A latest record that still references an older version of a record the change reached (C-1@1 depends_on
R-1@1 while R-1@2 changed) is reported as a pointer too: only latest versions take a status, so without
it the change would never reach that record. `check` warns about the same reference (superseded-reference).
"""
from __future__ import annotations

from . import edges as E
from .impact import ImpactReport, impact
from .records import CODE, Record, Store

REACH_KINDS = ("calls", "references")


def referenced_symbols(store: Store) -> set[str]:
    return {e["to"][len(CODE):] for r in store.records for e in r.relations if str(e.get("to", "")).startswith(CODE)}


def _owner(sym: str, modules: set[str]) -> str | None:
    """The module whose body contains sym: the longest module name that is sym or a dotted prefix of it."""
    parts = sym.split(".")
    for i in range(len(parts), 0, -1):
        if ".".join(parts[:i]) in modules:
            return ".".join(parts[:i])
    return None


def events_from_diff(d: dict, referenced: set[str], modules: set[str] = frozenset()) -> list[dict]:
    removed = set(d["defs_removed"])
    touched = set(d["defs_changed"]) | {e["src"] for e in d["added"] + d["removed"] if e["kind"] != "defines"}
    # a module is touched by any change to what it contains (a module's own hash is a placeholder)
    contained = touched | set(d["defs_added"]) | removed | {
        e["dst"] for e in d["added"] + d["removed"] if e["kind"] == "defines"}
    touched |= {_owner(s, modules) for s in contained if _owner(s, modules) not in (None, s)}
    events = []
    for sym in sorted(referenced & removed):
        events.append({"change": "retract", "target": CODE + sym, "by": "code", "reason": "symbol deleted"})
    for sym in sorted((referenced & touched) - removed):
        events.append({"change": "revise", "target": CODE + sym, "by": "code", "authorized_by": None,
                       "reason": "body or outgoing edges changed"})
    return events


def _reach_edges(old: dict, new: dict) -> dict[str, set[tuple[str, str]]]:
    """Resolved calls/references from both snapshots (a removed callee is only in the old one)."""
    out_edges: dict[str, set[tuple[str, str]]] = {}
    for snap in (old, new):
        for e in snap["edges"]:
            if e["kind"] in REACH_KINDS and e.get("resolved", True):
                out_edges.setdefault(e["src"], set()).add((e["dst"], e["kind"]))
    return out_edges


def _walk(sym: str, out_edges: dict, modules: set[str], depth: int) -> tuple[dict, set[str], list]:
    """Breadth-first from all of sym's own body (nested defs, methods; covered by its hash) for `depth` steps.
    Returns the first path to each reached symbol, everything seen, and the last frontier."""
    inside = {s for s in out_edges if s == sym or (s.startswith(sym + ".") and _owner(s, modules) == _owner(sym, modules))}
    seen, frontier, paths = set(inside), [(s, []) for s in sorted(inside)], {}
    for _ in range(depth):
        nxt = []
        for s, path in frontier:
            for dst, kind in sorted(out_edges.get(s, ())):
                if dst in seen:
                    continue
                seen.add(dst)
                step = path + [(dst, kind)]
                paths[dst] = step
                nxt.append((dst, step))
        frontier = nxt
    return paths, seen, frontier


def reached_changes(store: Store, d: dict, old: dict, new: dict, referenced: set[str], modules: set[str],
                    depth: int = 1, flagged: frozenset = frozenset()) -> list[str]:
    """Pointers (candidates for attention, not required reassessments; they change no status): linked symbol S reaches changed definition T through resolved calls/references.
    Walks both snapshots' edges (a removed callee is only in the old one). Module links are skipped: their
    own contents already revise them, and walking out of a whole module would flag almost everything.
    Records already in `flagged` (classified by the report) are not repeated; a pointer whose records are
    all flagged is dropped (on Telosmith's own history that removed 34 of 56 pointers)."""
    if depth <= 0:
        return []
    changed = set(d["defs_changed"]) | set(d["defs_removed"])
    if not changed:
        return []
    out_edges = _reach_edges(old, new)
    linked_by: dict[str, list[str]] = {}
    for r in store.records:
        for e in r.relations:
            to = str(e.get("to", ""))
            if to.startswith(CODE):
                linked_by.setdefault(to[len(CODE):], []).append(r.ref)
    findings = []
    for sym in sorted(referenced - modules):
        paths, _, _ = _walk(sym, out_edges, modules, depth)
        hits = {dst: p for dst, p in paths.items() if dst in changed}
        for dst in sorted(hits):
            path = hits[dst]
            via = "".join(f" via {CODE}{p}" for p, _ in path[:-1])
            kinds = "/".join(k for _, k in path)
            records = ", ".join(sorted(set(linked_by.get(sym, [])) - set(flagged)))
            if not records:
                continue
            findings.append(f"structural: {CODE}{sym} reaches changed {CODE}{dst}{via} ({kinds}, depth {len(path)}); "
                            f"no status change; candidate for attention: {records}")
    return findings


def unexamined_beyond(d: dict, old: dict, new: dict, referenced: set[str], modules: set[str], depth: int) -> str | None:
    """A footer line counting the symbols one step past `depth` from linked symbols, which the pointers did
    not examine (one more breadth-first layer; nothing is compared). None when no definition changed or
    nothing lies beyond."""
    if not (set(d["defs_changed"]) | set(d["defs_removed"])):
        return None
    out_edges = _reach_edges(old, new)
    within, beyond = set(), set()
    for sym in sorted(referenced - modules):
        _, seen, frontier = _walk(sym, out_edges, modules, depth)
        within |= seen
        beyond |= {dst for s, _ in frontier for dst, _ in out_edges.get(s, ()) if dst not in seen}
    n = len(beyond - within)
    if not n:
        return None
    return (f"reach depth {depth}; {n} further symbol{'s' if n != 1 else ''} within depth {depth + 1} "
            f"not examined (use --reach-depth {depth + 1})")


def superseded_pointers(store: Store, impacts: dict) -> list[str]:
    """Latest records that reference an older version of a record the change reached, and so take no status."""
    out = []
    for r in sorted((x for x in store.latest.values() if x.ref not in impacts), key=lambda x: x.ref):
        for e in r.relations:
            to = str(e.get("to", ""))
            if e.get("rel") == "supersedes" or to.startswith(CODE) or to not in store.by_ref:
                continue
            rid = store.by_ref[to].id
            newest = store.latest[rid]
            if rid != r.id and newest is not store.by_ref[to] and newest.ref in impacts:
                out.append(f"structural: {r.ref} references superseded {to}; {newest.ref} changed "
                           f"({impacts[newest.ref].status}); no status change; candidate for attention: {r.ref}")
    return out


def code_impact(store: Store, old: dict, new: dict, *, reach_depth: int = 1) -> tuple[ImpactReport, list[dict]]:
    d = E.diff(old, new)
    modules = set(old["header"].get("modules", {})) | set(new["header"].get("modules", {}))
    referenced = referenced_symbols(store)
    events = events_from_diff(d, referenced, modules)
    pseudo = [Record(id=CODE + s, version=0, type="source", subject="code", text=f"code symbol {s}")
              for s in sorted(referenced)]
    rep = impact(Store(store.records + pseudo), events)
    rep.findings.extend(reached_changes(store, d, old, new, referenced, modules, reach_depth, frozenset(rep.impacts)))
    rep.findings.extend(superseded_pointers(store, rep.impacts))
    footer = unexamined_beyond(d, old, new, referenced, modules, reach_depth)
    if footer:
        rep.notes.append(footer)
    return rep, events
