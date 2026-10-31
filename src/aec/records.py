"""AEC reasoning records: load, index, and the deterministic cross-record checks (`aec check`).

Records are JSON lines (see docs/reasoning-vocabulary.md). Standard library only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

TYPES = {"purpose", "requirement", "criterion", "assumption", "source", "claim", "evidence",
         "evaluation", "decision", "authority", "revision"}
RELATIONS = {"serves", "implements", "implemented_by", "depends_on", "supports", "contradicts", "tests",
             "produced", "selects", "supersedes", "observed_on"}
# feature 002: tell contract conformance from outcome (Kate, AEC round 3). Both fields are optional.
EVIDENCE_KINDS = {"contract_conformance", "behavioral_observation", "outcome_observation"}
CLAIM_CATEGORIES = {"requirement_satisfaction", "purpose_outcome"}
CODE = "code:"  # unversioned reference to a code symbol; the edge snapshot supplies its current state
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
        return self.id if self.id.startswith(CODE) else ref(self.id, self.version)

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


def defined_symbols(edges: dict) -> set[str]:
    """Every symbol an edge snapshot defines (definitions plus the modules that contain them)."""
    out = set(edges["header"].get("modules", {}))
    for e in edges["edges"]:
        if e["kind"] == "defines":
            out.add(e["dst"])
            out.add(e["src"])
    return out


def check(store: Store, edges: dict | None = None, *, sources=None) -> list[Finding]:
    """Deterministic cross-record checks. They say nothing about whether evidence is *good*.
    With an edge snapshot, `code:` references must name a symbol the snapshot defines."""
    out: list[Finding] = []
    symbols = defined_symbols(edges) if edges else None
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
            if to.startswith(CODE):
                if symbols is not None and to[len(CODE):] not in symbols:
                    out.append(Finding("error", "code-reference", r.ref,
                                       f"{e.get('rel')} -> {to}: no such symbol in the edge snapshot (renamed or deleted?)"))
                continue
            try:
                split_ref(to)
            except ValueError as ex:
                out.append(Finding("error", "reference", r.ref, str(ex)))
                continue
            if to not in store.by_ref:
                out.append(Finding("error", "reference", r.ref, f"{e.get('rel')} -> {to} does not resolve"))
        if "rationale" in r.data and not isinstance(r.get("rationale"), str):
            out.append(Finding("error", "rationale-shape", r.ref, "rationale must be a string"))
        if "anchors" in r.data:
            from .sources import SourceContext, record_findings
            if sources is None:
                sources = SourceContext(Path.cwd())
            out.extend(record_findings(r, sources))
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
        kind, cat = r.get("evidence_kind"), r.get("claim_category")
        if kind is not None and kind not in EVIDENCE_KINDS:
            out.append(Finding("error", "evidence-kind", r.ref, f"unknown evidence_kind {kind!r}"))
        if cat is not None and cat not in CLAIM_CATEGORIES:
            out.append(Finding("error", "claim-category", r.ref, f"unknown claim_category {cat!r}"))
        if r.type == "claim" and cat == "purpose_outcome" and store.latest.get(r.id) is r:
            sup = [ev for ev in store.in_edges(r.ref, "supports") if ev.type == "evidence"]
            if sup and all(ev.get("evidence_kind") == "contract_conformance" for ev in sup):
                out.append(Finding("warning", "outcome-sufficiency", r.ref,
                                   "purpose-outcome claim is supported only by contract-conformance evidence ("
                                   + ", ".join(ev.ref for ev in sup) + "): an unsupported inference, not a "
                                   "finding that the outcome failed. Add an outcome observation or narrow the claim."))
        if r.type == "revision" and not r.get("authorized_by"):
            out.append(Finding("warning", "authority", r.ref, "revision without authorized_by: it is a proposal, not yet a revision"))
    return out
