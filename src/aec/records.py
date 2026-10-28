"""AEC reasoning records: load, index, and the deterministic cross-record checks (`aec check`).

Records are JSON lines (see docs/reasoning-vocabulary.md). Standard library only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

TYPES = {"purpose", "requirement", "criterion", "assumption", "source", "claim", "evidence",
         "evaluation", "decision", "authority", "revision"}
RELATIONS = {"serves", "implements", "depends_on", "supports", "contradicts", "tests", "produced",
             "selects", "supersedes"}
TIERS = {"candidate", "reviewed", "observed", "prospective"}


def ref(rid: str, version: int) -> str:
    return f"{rid}@{version}"


def split_ref(r: str) -> tuple[str, int]:
    rid, _, v = r.rpartition("@")
    if not rid or not v.isdigit():
        raise ValueError(f"bad reference {r!r}: expected id@version")
    return rid, int(v)


@dataclass
class Record:
    id: str
    version: int
    type: str
    text: str = ""
    subject: str | None = None
    relations: list[dict] = field(default_factory=list)
    data: dict = field(default_factory=dict)

    @property
    def ref(self) -> str:
        return ref(self.id, self.version)

    def get(self, key, default=None):
        return self.data.get(key, default)


class Store:
    """All versions of all records. A record id may appear with several versions; none is ever edited."""

    def __init__(self, records: list[Record]):
        self.records = records
        self.by_ref: dict[str, Record] = {}
        self.latest: dict[str, Record] = {}
        for r in records:
            self.by_ref[r.ref] = r
            if r.id not in self.latest or r.version > self.latest[r.id].version:
                self.latest[r.id] = r

    @classmethod
    def load(cls, path: str | Path) -> "Store":
        recs = []
        for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            d = json.loads(line)
            known = {"id", "version", "type", "text", "subject", "relations"}
            recs.append(Record(id=d["id"], version=int(d["version"]), type=d["type"], text=d.get("text", ""),
                               subject=d.get("subject"), relations=d.get("relations", []),
                               data={k: v for k, v in d.items() if k not in known}))
        return cls(recs)

    def out_edges(self, r: Record, rel: str) -> list[str]:
        return [e["to"] for e in r.relations if e.get("rel") == rel]

    def in_edges(self, target_ref: str, rel: str) -> list[Record]:
        return [r for r in self.records if any(e.get("rel") == rel and e.get("to") == target_ref for e in r.relations)]

    def governs(self, authority_id: str | None, subject: str | None) -> bool:
        if not authority_id or not subject:
            return False
        a = self.latest.get(authority_id)
        return bool(a and a.type == "authority" and subject in (a.get("governs") or []))


@dataclass
class Finding:
    level: str  # error | warning
    rule: str
    ref: str
    msg: str


def check(store: Store) -> list[Finding]:
    """Deterministic cross-record checks. They say nothing about whether evidence is *good*."""
    out: list[Finding] = []
    seen = set()
    for r in store.records:
        if r.ref in seen:
            out.append(Finding("error", "unique", r.ref, "duplicate id@version; versions are appended, never reused"))
        seen.add(r.ref)
        if r.type not in TYPES:
            out.append(Finding("error", "type", r.ref, f"unknown type {r.type!r}"))
        for e in r.relations:
            if e.get("rel") not in RELATIONS:
                out.append(Finding("error", "relation", r.ref, f"unknown relation {e.get('rel')!r}"))
            to = e.get("to", "")
            try:
                split_ref(to)
            except ValueError as ex:
                out.append(Finding("error", "reference", r.ref, str(ex)))
                continue
            if to not in store.by_ref:
                out.append(Finding("error", "reference", r.ref, f"{e.get('rel')} -> {to} does not resolve"))
        # rule 1: accepted decisions need a governing authority
        if r.type == "decision" and r.get("status") == "accepted" and not store.governs(r.get("decided_by"), r.subject):
            out.append(Finding("error", "authority", r.ref,
                               f"accepted, but decided_by={r.get('decided_by')!r} does not govern subject {r.subject!r}"))
        # rule 2: evidence tiers need their backing
        if r.type in {"claim", "evidence"}:
            tier = r.get("tier")
            if tier is not None and tier not in TIERS:
                out.append(Finding("error", "tier", r.ref, f"unknown tier {tier!r}"))
            if r.type == "claim" and tier == "observed":
                backed = any(store.in_edges(ev.ref, "produced")
                             for ev in store.in_edges(r.ref, "supports") if ev.type == "evidence")
                if not backed:
                    out.append(Finding("error", "tier", r.ref,
                                       "tier 'observed' but no supporting evidence was produced by an evaluation"))
            if tier == "prospective" and not r.get("frozen_sha256"):
                out.append(Finding("error", "tier", r.ref, "tier 'prospective' needs frozen_sha256 (freeze before the outcome)"))
        if r.type == "revision" and not r.get("authorized_by"):
            out.append(Finding("warning", "authority", r.ref, "revision without authorized_by: it is a proposal, not yet a revision"))
    return out
