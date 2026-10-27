"""`aec impact`: something changed, so which conclusions are no longer justified?

Given change events (retract or revise), walk the justification structure backwards from the changed
record and classify every conclusion that relied on it. Authorized revisions and provisional
(exploratory) changes are separated from unauthorized changes and broken support. See
docs/reasoning-vocabulary.md for the semantics.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .records import Record, Store, split_ref

# severity order: a conclusion keeps the most severe status it reaches
SEVERITY = ["exploratory", "rebaseline", "weakened", "contested", "needs_review", "stale", "unjustified"]
# broken, unauthorized or contested support makes dependents need review
PROPAGATES = {"unjustified", "stale", "contested"}


@dataclass
class Impact:
    ref: str
    status: str
    because: list[str] = field(default_factory=list)  # chain of refs from the change to this conclusion


@dataclass
class ImpactReport:
    changes: list[dict]
    impacts: dict[str, Impact]
    findings: list[str]
    unaffected: int

    def by_status(self) -> dict[str, list[Impact]]:
        out: dict[str, list[Impact]] = {s: [] for s in reversed(SEVERITY)}
        for i in self.impacts.values():
            out[i.status].append(i)
        return out


def _dependents(store: Store, target_ref: str) -> list[tuple[Record, str]]:
    """Records whose justification includes target_ref, with how: 'necessary' (depends_on, selects,
    or produced-by) or 'support' (one of possibly several pieces of supporting evidence)."""
    out: list[tuple[Record, str]] = []
    target = store.by_ref.get(target_ref)
    for r in store.records:
        for e in r.relations:
            if e.get("to") != target_ref:
                continue
            if e.get("rel") in ("depends_on", "selects", "implemented_by"):
                out.append((r, "necessary"))
            elif e.get("rel") == "observed_on":
                out.append((r, "applicability"))  # evidence observed on this: re-check it still applies
    if target is not None:
        # evidence supporting a claim: the claim depends on that evidence (as one support among several)
        for e in target.relations:
            to = e.get("to")
            if e.get("rel") == "supports" and to in store.by_ref:
                out.append((store.by_ref[to], "support"))
            if e.get("rel") == "produced" and to in store.by_ref:
                out.append((store.by_ref[to], "necessary"))
    # only the current version of a dependent matters
    return [(r, how) for r, how in out if store.latest.get(r.id) is r]


def _live_supports(store: Store, claim: Record, dead: set[str]) -> list[str]:
    return [ev.ref for ev in store.in_edges(claim.ref, "supports") if ev.ref not in dead]


def _raise(impacts: dict[str, Impact], ref: str, status: str, because: list[str]) -> bool:
    cur = impacts.get(ref)
    if cur is None or SEVERITY.index(status) > SEVERITY.index(cur.status):
        impacts[ref] = Impact(ref, status, because)
        return True
    return False


def impact(store: Store, changes: list[dict]) -> ImpactReport:
    impacts: dict[str, Impact] = {}
    findings: list[str] = []
    dead: set[str] = set()  # refs whose support no longer holds
    queue: list[str] = []

    for ch in changes:
        kind, target_ref = ch["change"], ch["target"]
        if target_ref not in store.by_ref:
            findings.append(f"change target {target_ref} does not resolve")
            continue
        target = store.by_ref[target_ref]
        provisional = target.get("epistemic") == "provisional"
        authorized = store.governs(ch.get("authorized_by"), target.subject)

        if kind == "retract":
            dead.add(target_ref)
            for dep, how in _dependents(store, target_ref):
                if how == "support" and dep.type == "claim" and _live_supports(store, dep, dead):
                    status = "weakened"
                elif dep.type == "decision" or how == "applicability":
                    # decisions belong to a human authority; observations stay valid records of what was seen.
                    # Either way: flag for review, never invalidate.
                    status = "needs_review"
                else:
                    status = "unjustified"
                if _raise(impacts, dep.ref, status, [target_ref, dep.ref]) and status in PROPAGATES | {"needs_review"}:
                    queue.append(dep.ref)
        elif kind == "add":
            # new evidence: a contradiction starts a reassessment; new support changes nothing
            for e in target.relations:
                to = e.get("to")
                if e.get("rel") == "contradicts" and to in store.by_ref:
                    if _raise(impacts, to, "contested", [target_ref, to]):
                        queue.append(to)
        elif kind == "revise":
            new = ch.get("new")
            if new and new not in store.by_ref:
                findings.append(f"revision {target_ref} -> {new}: new version is not in the record store")
            if provisional:
                status = "exploratory"
            elif authorized:
                status = "rebaseline"
            else:
                status = "stale"
                if target.type in {"purpose", "criterion", "requirement"}:
                    findings.append(
                        f"unauthorized revision of committed {target.type} {target_ref}: "
                        f"by={ch.get('by')!r}, authorized_by={ch.get('authorized_by')!r} does not govern "
                        f"subject {target.subject!r}. This is a proposal, not a revision.")
            for dep, how in _dependents(store, target_ref):
                dep_status = "needs_review" if how == "applicability" else status
                if _raise(impacts, dep.ref, dep_status, [target_ref, dep.ref]) and dep_status in PROPAGATES | {"needs_review"}:
                    queue.append(dep.ref)
        else:
            findings.append(f"unknown change kind {kind!r}")

    # transitive. A claim, requirement or piece of evidence that *necessarily* rests on an unjustified
    # conclusion is itself unjustified. Decisions are never declared unjustified by the tool: they belong
    # to a human authority, so they are flagged for review. Everything else downstream of a broken or
    # stale conclusion needs review.
    while queue:
        cur = queue.pop(0)
        chain, cur_status = impacts[cur].because, impacts[cur].status
        for dep, how in _dependents(store, cur):
            if cur_status == "unjustified" and how == "necessary" and dep.type != "decision":
                status = "unjustified"
            elif cur_status == "unjustified" and how == "support" and dep.type == "claim" \
                    and _live_supports(store, dep, dead | {cur}):
                status = "weakened"
            else:
                status = "needs_review"
            if status == "unjustified":
                dead.add(dep.ref)
            if _raise(impacts, dep.ref, status, chain + [dep.ref]) and status in PROPAGATES | {"needs_review"}:
                queue.append(dep.ref)

    conclusions = [r for r in store.latest.values() if r.type in {"claim", "decision", "requirement", "evaluation", "evidence"}]
    unaffected = sum(1 for r in conclusions if r.ref not in impacts)
    return ImpactReport(changes, impacts, findings, unaffected)


def render(store: Store, rep: ImpactReport) -> str:
    lines = ["# aec impact", ""]
    for ch in rep.changes:
        lines.append(f"- change: {ch['change']} {ch['target']}" + (f" -> {ch['new']}" if ch.get("new") else "")
                     + f" (by {ch.get('by')}, authorized_by {ch.get('authorized_by')})")
    lines.append("")
    for status, items in rep.by_status().items():
        for i in items:
            r = store.by_ref.get(i.ref)
            lines.append(f"[{status}] {i.ref}: {r.text if r else ''}")
            lines.append(f"    via {' -> '.join(i.because)}")
    for f in rep.findings:
        lines.append(f"[finding] {f}")
    lines.append(f"\n{len(rep.impacts)} affected, {rep.unaffected} conclusions unaffected")
    return "\n".join(lines)
