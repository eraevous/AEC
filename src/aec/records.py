"""AEC reasoning records: load, index, and the deterministic cross-record checks (`aec check`).

Records are JSON lines (see docs/reasoning-vocabulary.md). Standard library only.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

TYPES = {"purpose", "requirement", "criterion", "assumption", "source", "claim", "evidence", "ambition", "experiment",
         "evaluation", "decision", "authority", "revision"}
RELATIONS = {"serves", "implements", "implemented_by", "depends_on", "supports", "contradicts", "tests",
             "produced", "selects", "supersedes", "observed_on"}
# feature 002: tell contract conformance from outcome (Kate, AEC round 3). Both fields are optional.
SHA256_RE = re.compile(r"[0-9a-f]{64}")
EVIDENCE_KINDS = {"contract_conformance", "behavioral_observation", "outcome_observation"}
CLAIM_CATEGORIES = {"requirement_satisfaction", "purpose_outcome"}
# Relations kept for old records but no longer recommended: relation -> what to use instead.
DEPRECATED_RELATIONS = {
    "implements": "'implements' is deprecated and impact ignores it: put 'implemented_by' on the requirement "
                  "instead (the requirement is satisfied by the code, SysML <<satisfy>>)",
}
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

    def __init__(self, records: list[Record], problems: list | None = None):
        self.records = records
        self.problems = problems or []   # records that couldn't be loaded, reported by check()
        self.by_ref: dict[str, Record] = {}
        self.latest: dict[str, Record] = {}
        for r in records:
            self.by_ref[r.ref] = r
            if r.id not in self.latest or r.version > self.latest[r.id].version:
                self.latest[r.id] = r

    @classmethod
    def load(cls, path: str | Path) -> Store:
        recs, problems = [], []
        first: dict[str, tuple[int, str]] = {}  # id@version -> (line number, unnormalized text) of its first line
        # Split on LF only and keep each line as written (a CR before the LF included): spec 006's
        # duplicate test compares these unnormalized lines, so whitespace or CRLF differences stay `unique`.
        for n, written in enumerate(Path(path).read_bytes().decode("utf-8").split("\n"), 1):
            line = written.strip()
            if not line or line.startswith("//"):
                continue
            d = json.loads(line)
            key = f"{d.get('id')}@{d.get('version')!r}"
            if key in first and first[key][1] == written:
                # spec 006 (C-21): a merge of two branches that appended the same line leaves an identical
                # copy. It is the same record, read once; any difference still reaches check's `unique` rule.
                problems.append(Finding("warning", "duplicate-line", f"{d.get('id')}@{d.get('version')}",
                                        f"line {n} repeats line {first[key][0]} exactly; read as one record "
                                        "(see docs/reference/records-hygiene.md to remove the copy)"))
                continue
            first.setdefault(key, (n, written))
            known = {"id", "version", "type", "text", "subject", "relations"}
            v = d.get("version")
            if not isinstance(v, int) or isinstance(v, bool) or v < 1:
                # never coerce: 1.9 or "1" read as 1 would silently become a different id@version
                problems.append(Finding("error", "version", f"{d.get('id')}@{v!r}",
                                        f"line {n}: version must be a positive JSON integer; record not loaded"))
                continue
            recs.append(Record(id=d["id"], version=v, type=d["type"], text=d.get("text", ""),
                               subject=d.get("subject"), relations=d.get("relations", []),
                               data={k: x for k, x in d.items() if k not in known}))
        return cls(recs, problems)

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


def _near(name: str, symbols: set[str]) -> tuple[list[str], int]:
    """Likely intended names, deterministic, and how many more were left out. First a missing prefix (e.g. a
    source root such as `src.`): known symbols that end with the whole name (up to two). Otherwise a misspelt
    last segment (siblings under the same parent whose last segment is close; shared module prefixes never
    count towards similarity), then the same last segment under another parent, as when a function moved
    to another module (up to three suggestions in all)."""
    import difflib
    pool = sorted(symbols)
    hits = [s for s in pool if s.endswith("." + name)]
    if hits:
        return hits[:2], 0
    parent, _, leaf = name.rpartition(".")
    siblings = {s.rpartition(".")[2]: s for s in pool if s.rpartition(".")[0] == parent}
    typos = [siblings[m] for m in difflib.get_close_matches(leaf, sorted(siblings), n=2, cutoff=0.75)]
    moved = [s for s in pool if s.rpartition(".")[2] == leaf and s not in typos]
    room = 3 - len(typos)
    return typos + moved[:room], max(0, len(moved) - room)


def _or(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " or " + items[-1]


def _ref_shaped(v) -> bool:
    """A value that looks like one or more relation targets: `code:...` or `id@version`."""
    vals = v if isinstance(v, list) else [v]
    return bool(vals) and all(isinstance(x, str) and (x.startswith(CODE) or "@" in x) for x in vals)


def defined_symbols(edges: dict) -> set[str]:
    """Every symbol an edge snapshot defines (definitions plus the modules that contain them)."""
    out = set(edges["header"].get("modules", {}))
    for e in edges["edges"]:
        if e["kind"] == "defines":
            out.add(e["dst"])
            out.add(e["src"])
    return out


def _relation_findings(store: Store, r: Record, symbols: set[str] | None) -> list[Finding]:
    """Relation names are known; `code:` targets exist in the snapshot (when given); other targets resolve."""
    out = []
    for e in r.relations:
        if e.get("rel") not in RELATIONS:
            out.append(Finding("error", "relation", r.ref, f"unknown relation {e.get('rel')!r}"))
        elif e.get("rel") in DEPRECATED_RELATIONS:
            out.append(Finding("warning", "deprecated-relation", r.ref, DEPRECATED_RELATIONS[e["rel"]]))
        to = e.get("to", "")
        if to.startswith(CODE):
            if symbols is not None and to[len(CODE):] not in symbols:
                near, more = _near(to[len(CODE):], symbols)
                hint = ("; did you mean " + _or([CODE + n for n in near]) + "?"
                        + (f" ({more} more with the same name)" if more else "")) if near else ""
                out.append(Finding("error", "code-reference", r.ref,
                                   f"{e.get('rel')} -> {to}: no such symbol in the edge snapshot (renamed or deleted?){hint}"))
            continue
        try:
            split_ref(to)
        except ValueError as ex:
            out.append(Finding("error", "reference", r.ref, str(ex)))
            continue
        if to not in store.by_ref:
            out.append(Finding("error", "reference", r.ref, f"{e.get('rel')} -> {to} does not resolve"))
    return out


def _shape_findings(r: Record) -> list[Finding]:
    """Fields that look like relations but sit at the top level; a non-string rationale."""
    out = []
    misplaced = sorted(k for k in RELATIONS & set(r.data) if _ref_shaped(r.data[k]))
    if misplaced:
        out.append(Finding("warning", "relation-shape", r.ref,
                           f"top-level field(s) {', '.join(misplaced)} look like relations but are not checked or "
                           "propagated; write them as \"relations\": [{\"rel\": ..., \"to\": ...}]"))
    if "rationale" in r.data and not isinstance(r.get("rationale"), str):
        out.append(Finding("error", "rationale-shape", r.ref, "rationale must be a string"))
    return out


def _decision_findings(store: Store, r: Record) -> list[Finding]:
    """Rule 1: an accepted decision needs an authority that governs its subject."""
    if r.type == "decision" and r.get("status") == "accepted" and not store.governs(r.get("decided_by"), r.subject):
        return [Finding("error", "authority", r.ref,
                        f"accepted, but decided_by={r.get('decided_by')!r} does not govern subject {r.subject!r}")]
    return []


def _tier_findings(store: Store, r: Record) -> list[Finding]:
    """Rule 2: evidence tiers need their backing (observed: produced evidence; prospective: a freeze digest)."""
    if r.type not in {"claim", "evidence"}:
        return []
    out = []
    tier = r.get("tier")
    if tier is not None and tier not in TIERS:
        out.append(Finding("error", "tier", r.ref, f"unknown tier {tier!r}"))
    if r.type == "claim" and tier == "observed":
        backed = any(store.in_edges(ev.ref, "produced")
                     for ev in store.in_edges(r.ref, "supports") if ev.type == "evidence")
        if not backed:
            out.append(Finding("error", "tier", r.ref,
                               "tier 'observed' but no supporting evidence was produced by an evaluation"))
    digest = r.get("frozen_sha256")
    if tier == "prospective" and not (isinstance(digest, str) and SHA256_RE.fullmatch(digest)):
        out.append(Finding("error", "tier", r.ref, "tier 'prospective' needs frozen_sha256, a 64-character "
                           "lowercase hex SHA-256 of the frozen source (freeze before the outcome)"))
    return out


def _evidence_kind_findings(store: Store, r: Record) -> list[Finding]:
    """Known evidence kinds and claim categories; rule 5, outcome sufficiency (a warning)."""
    out = []
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
    return out


def _evidence_text_findings(store: Store, r: Record) -> list[Finding]:
    """Evidence with no text (a warning). Like outcome sufficiency, only the latest version of an id is judged,
    so appending a corrected version clears it; a superseded textless version still warns while a latest
    record still points at it."""
    if r.type != "evidence" or (isinstance(r.text, str) and r.text.strip()):
        return []
    msg = "evidence has no text: reports will show it as an empty line; say what was observed"
    if store.latest.get(r.id) is r:
        return [Finding("warning", "evidence-text", r.ref, msg)]
    users = sorted(x.ref for x in store.records if store.latest.get(x.id) is x
                   and any(e.get("to") == r.ref for e in x.relations))
    if not users:
        return []
    return [Finding("warning", "evidence-text", r.ref, f"{msg} ({r.ref} still referenced by {', '.join(users)})")]


def _superseded_reference_findings(store: Store, r: Record) -> list[Finding]:
    """A latest record that points at an older version of another id (a warning: the old version may be meant).
    As for evidence text, only the latest version of the referring id is judged, so appending a version that
    moves the reference clears it. `supersedes`, and a record's references to its own id, are history."""
    if store.latest.get(r.id) is not r:
        return []
    out = []
    for e in r.relations:
        to = str(e.get("to", ""))
        if e.get("rel") == "supersedes" or to.startswith(CODE) or to not in store.by_ref:
            continue
        rid, v = split_ref(to)
        newest = store.latest[rid]
        if rid != r.id and newest.version > v:
            out.append(Finding("warning", "superseded-reference", r.ref,
                               f"{e.get('rel')} -> {to}, but {newest.ref} is newer: changes that reach "
                               f"{newest.ref} only point at this record; append a version that references "
                               f"{newest.ref} if that is meant (the old version may be intentional)"))
    return out


def check(store: Store, edges: dict | None = None, *, sources=None) -> list[Finding]:
    """Deterministic cross-record checks. They say nothing about whether evidence is *good*.
    With an edge snapshot, `code:` references must name a symbol the snapshot defines.

    Findings come per record, in this order: unique id@version, known type, relations, field shape,
    source anchors, decision authority, tiers, evidence kinds and outcome sufficiency, evidence text, superseded references, revisions."""
    out: list[Finding] = list(getattr(store, "problems", []))
    symbols = defined_symbols(edges) if edges else None
    seen = set()
    for r in store.records:
        if r.ref in seen:
            out.append(Finding("error", "unique", r.ref, "duplicate id@version; versions are appended, never reused"))
        seen.add(r.ref)
        if r.type not in TYPES:
            out.append(Finding("error", "type", r.ref, f"unknown type {r.type!r}"))
        out.extend(_relation_findings(store, r, symbols))
        out.extend(_shape_findings(r))
        if "anchors" in r.data:
            from .sources import SourceContext, record_findings
            if sources is None:
                sources = SourceContext(Path.cwd())
            out.extend(record_findings(r, sources))
        out.extend(_decision_findings(store, r))
        out.extend(_tier_findings(store, r))
        out.extend(_evidence_kind_findings(store, r))
        out.extend(_evidence_text_findings(store, r))
        out.extend(_superseded_reference_findings(store, r))
        if r.type == "revision" and not r.get("authorized_by"):
            out.append(Finding("warning", "authority", r.ref, "revision without authorized_by: it is a proposal, not yet a revision"))
    return out
