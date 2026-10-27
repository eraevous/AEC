"""`aec code-impact`: turn a structural diff of the code into change events, then run `aec impact`.

Records point at code with unversioned `code:<dotted>` references. A referenced symbol that was deleted
is retracted. One whose body changed, or whose outgoing edges were added or removed, is revised without
authorization: dependents become stale until someone re-examines them. Unreferenced code changes produce
nothing (Constitution IV: structural only; nothing here judges whether the change was right).
"""
from __future__ import annotations

from . import edges as E
from .impact import ImpactReport, impact
from .records import CODE, Record, Store


def referenced_symbols(store: Store) -> set[str]:
    return {e["to"][len(CODE):] for r in store.records for e in r.relations if str(e.get("to", "")).startswith(CODE)}


def events_from_diff(d: dict, referenced: set[str]) -> list[dict]:
    removed = set(d["defs_removed"])
    touched = set(d["defs_changed"]) | {e["src"] for e in d["added"] + d["removed"] if e["kind"] != "defines"}
    events = []
    for sym in sorted(referenced & removed):
        events.append({"change": "retract", "target": CODE + sym, "by": "code", "reason": "symbol deleted"})
    for sym in sorted((referenced & touched) - removed):
        events.append({"change": "revise", "target": CODE + sym, "by": "code", "authorized_by": None,
                       "reason": "body or outgoing edges changed"})
    return events


def code_impact(store: Store, old: dict, new: dict) -> tuple[ImpactReport, list[dict]]:
    events = events_from_diff(E.diff(old, new), referenced_symbols(store))
    pseudo = [Record(id=CODE + s, version=0, type="source", subject="code", text=f"code symbol {s}")
              for s in sorted(referenced_symbols(store))]
    return impact(Store(store.records + pseudo), events), events
