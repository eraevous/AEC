#!/usr/bin/env python3
"""Decisions and human control: what is waiting on the owner, what each lever does, and what happens by default.

An experiment (DEC-033), not a Telosmith feature yet: it reads the project's records where they already are
and prints one Markdown report. Read-only; standard library; GitHub via the `gh` CLI when available.

    python3 experiments/owner-report/owner_report.py --telosmith . --relay ../relay-kit-private \
        [--repo eraevous/Telosmith --repo eraevous/relay-kit-private] [--owner zach] [--days 7] [-o report.md]

Sections:
  1. Your levers: each item you can act on (merge, decide, route, confirm, investigate), what the choice is,
     and what happens if you do nothing. Ordered so that items blocking other work come first.
  2. Choices you're making by default: things already sitting long enough that "no action" is the decision.
  3. What you decided recently: your own words, so you know what you committed to.
  4. Standing ambitions: directions kept open on purpose (not commitments).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

NOW = datetime.now(timezone.utc)
# Recipients that only the owner can reach: other apps' threads, not sessions that read the shared repo.
OWNER_ROUTED = ("codex:", "chatgpt:", "copilot:", "gemini:")


def jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("//")]


def when(text: str | None) -> datetime | None:
    if not text:
        return None
    try:
        t = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        try:
            t = datetime.strptime(text[:10], "%Y-%m-%d")
        except ValueError:
            return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def age(t: datetime | None) -> str:
    if not t:
        return "?"
    h = (NOW - t).total_seconds() / 3600
    return f"{h:.0f} h" if h < 48 else f"{h / 24:.1f} days"


def gh(path: str):
    if not shutil.which("gh"):
        return None
    r = subprocess.run(["gh", "api", path], check=False, capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


# ---------- sources ----------
def pull_requests(repos: list[str]) -> list[dict]:
    items = []
    for repo in repos:
        prs = gh(f"repos/{repo}/pulls?state=open&per_page=50")
        if prs is None:
            items.append({"lever": "note", "what": f"GitHub not read for {repo} (gh unavailable or no access)"})
            continue
        numbers = {p["head"]["ref"]: p["number"] for p in prs}
        bases = {p["head"]["ref"]: p["base"]["ref"] for p in prs}

        def depth(ref: str) -> int:  # 0 for a PR into the default branch; +1 per open PR it is stacked on
            d = 0
            while bases.get(ref) in bases and d < 50:
                ref, d = bases[ref], d + 1
            return d
        for p in prs:
            runs = gh(f"repos/{repo}/commits/{p['head']['sha']}/check-runs") or {}
            states = {c.get("conclusion") or c.get("status") for c in runs.get("check_runs", [])}
            ci = "failing" if "failure" in states else "running" if states & {"in_progress", "queued"} else \
                "green" if states else "no checks"
            after = numbers.get(p["base"]["ref"])
            stacked = f"; merge after #{after}" if after else ""
            name = repo.split("/")[1]
            if p.get("draft"):
                items.append({"lever": "wait", "where": f"{name}#{p['number']}", "what": p["title"],
                              "choice": "nothing yet: it's a draft", "default": "stays a draft",
                              "age": age(when(p["created_at"])), "blocks": 0})
                continue
            blocks = sum(1 for q in prs if q["base"]["ref"] == p["head"]["ref"])
            items.append({"lever": "merge", "where": f"{name}#{p['number']}", "what": p["title"],
                          "choice": f"merge, or ask for changes (CI {ci}{stacked})",
                          "default": "stays unmerged" + (f"; {blocks} stacked PR(s) wait on it" if blocks else ""),
                          "age": age(when(p["created_at"])), "blocks": blocks, "url": p["html_url"],
                          "stack": (repo, depth(p["head"]["ref"]), p["number"])})
    return items


def stranded_merges(repos: list[str], days: float = 14) -> list[dict]:
    """Merged PRs whose base was another branch that never reached the default branch.

    A stacked PR merges into its base branch. If that base isn't retargeted to the default branch (for
    example, it wasn't deleted when its own PR merged), the work sits merged but unreleased."""
    items = []
    for repo in repos:
        info = gh(f"repos/{repo}") or {}
        default = info.get("default_branch", "main")
        closed = gh(f"repos/{repo}/pulls?state=closed&per_page=50") or []
        bases = {}
        for p in closed:
            merged = when(p.get("merged_at"))
            if merged and p["base"]["ref"] != default and (NOW - merged).days <= days:
                bases.setdefault(p["base"]["ref"], []).append(p["number"])
        open_heads = {p["head"]["ref"] for p in (gh(f"repos/{repo}/pulls?state=open&per_page=50") or [])}
        for base, numbers in sorted(bases.items()):
            cmp = gh(f"repos/{repo}/compare/{default}...{base}")
            if not cmp or cmp.get("ahead_by", 0) == 0 or base in open_heads:
                continue  # already landed, branch gone, or a PR to land it is open
            prs = ", ".join(f"#{n}" for n in sorted(numbers))
            items.append({"lever": "land", "where": f"{repo.split('/')[1]}:{base}",
                          "what": f"{prs} merged into `{base}`, which is {cmp['ahead_by']} commit(s) ahead of {default}",
                          "choice": f"open or merge a PR from `{base}` into {default}",
                          "default": f"the work stays off {default}: merged, but not released or used",
                          "age": "-", "blocks": 0})
    return items


def relay_decisions(relay: Path) -> tuple[list[dict], list[dict]]:
    rows = jsonl(relay / "governance" / "decisions.jsonl")
    superseded = set()
    for r in rows:
        s = r.get("supersedes")
        superseded.update(s if isinstance(s, list) else [s] if s else [])
    open_items = [{"lever": "decide", "where": r["id"], "what": r["decision"],
                   "choice": "adopt, reject or change it (your words get recorded as the basis)",
                   "default": "stays proposed; work that assumes it waits or proceeds without a ruling",
                   "age": age(when(r.get("date"))), "blocks": 0}
                  for r in rows if r.get("status") == "proposed" and r["id"] not in superseded]
    return open_items, rows


def handoffs(relay: Path) -> list[dict]:
    items = []
    for f in sorted((relay / "handoffs").glob("HO-*.md")):
        text = f.read_text(encoding="utf-8")
        head = dict(re.findall(r"^(\w+): (.*)$", text.split("---")[1], re.M)) if text.startswith("---") else {}
        log = re.findall(r"^- (\S+) \| (\w+) \| ([^|]+)\|", text, re.M)
        status, to = head.get("status", "?"), head.get("to", "")
        last = when(log[-1][0]) if log else None
        hid = head.get("id", f.stem)
        if status == "sent" and to.startswith(OWNER_ROUTED):
            items.append({"lever": "route", "where": hid, "what": head.get("title", ""),
                          "choice": f"paste it into {to} (only you can reach that app), or cancel it",
                          "default": f"{to} never sees it; the work doesn't happen",
                          "age": age(last), "blocks": 0})
        elif status == "prepared" and "NOT AUTHORIZED YET" in text:
            items.append({"lever": "authorise", "where": hid, "what": head.get("title", ""),
                          "choice": "approve it in your own words, or drop it",
                          "default": "it stays a draft; no session may start it",
                          "age": age(last), "blocks": 0})
    return items


def owner_held(relay: Path) -> list[dict]:
    path = relay / "governance" / "candidates.md"
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| C-") and re.search(r"owner-held|Owner investigates|owner investigates", line, re.I):
            cid = line.split("|")[1].strip()
            title = re.sub(r"\*\*|\[[^\]]*\]", "", line.split("|")[2]).strip()[:140]
            items.append({"lever": "investigate", "where": cid, "what": title,
                          "choice": "your own investigation (agents prepare inputs, don't close it)",
                          "default": "stays open; related design choices keep deferring to it",
                          "age": "-", "blocks": 0})
    return items


def telosmith_records(root: Path) -> tuple[list[dict], list[dict]]:
    rows = jsonl(root / ".aec" / "records.jsonl")
    latest: dict[str, dict] = {}
    for r in rows:
        if r["id"] not in latest or r["version"] > latest[r["id"]]["version"]:
            latest[r["id"]] = r
    items = []
    for r in latest.values():
        if r["type"] == "decision" and r.get("status") == "proposed":
            items.append({"lever": "confirm", "where": f"{r['id']}@{r['version']}", "what": r.get("text", ""),
                          "choice": "accept (names you as decided_by) or reject",
                          "default": "stays proposed; never treated as your decision", "age": "-", "blocks": 0})
        if r["type"] == "revision" and not r.get("authorized_by"):
            items.append({"lever": "authorise", "where": f"{r['id']}@{r['version']}", "what": r.get("text", ""),
                          "choice": "authorise the revision, or leave it a proposal",
                          "default": "dependants are reported stale, not rebaselined", "age": "-", "blocks": 0})
    ambitions = [r for r in latest.values() if r["type"] == "ambition"]
    return items, ambitions


# ---------- report ----------
def table(items: list[dict]) -> str:
    head = "| # | Lever | Where | What | Your choice | If you do nothing | Age |\n|---|---|---|---|---|---|---|\n"
    rows = []
    for i, x in enumerate(items, 1):
        where = f"[{x['where']}]({x['url']})" if x.get("url") else x.get("where", "")
        what = x.get("what", "").replace("|", "/").replace("\n", " ")
        rows.append(f"| {i} | **{x['lever']}** | {where} | {what[:160]} | {x.get('choice', '')} | "
                    f"{x.get('default', '')} | {x.get('age', '')} |")
    return head + "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--telosmith", type=Path, default=Path("."))
    ap.add_argument("--relay", type=Path)
    ap.add_argument("--repo", action="append", default=[])
    ap.add_argument("--owner", default="zach")
    ap.add_argument("--days", type=float, default=2, help="how far back 'what you decided' reaches (default 2)")
    ap.add_argument("--stale-days", type=float, default=1.0, help="when waiting becomes a default choice")
    ap.add_argument("-o", "--output", type=Path)
    a = ap.parse_args(argv)

    levers = pull_requests(a.repo) + stranded_merges(a.repo)
    notes = [x for x in levers if x["lever"] == "note"]
    levers = [x for x in levers if x["lever"] != "note"]
    decisions: list[dict] = []
    if a.relay:
        open_decisions, decisions = relay_decisions(a.relay)
        levers += open_decisions + handoffs(a.relay) + owner_held(a.relay)
    record_items, ambitions = telosmith_records(a.telosmith)
    levers += record_items
    order = {"land": -1, "merge": 0, "route": 1, "decide": 2, "authorise": 3, "confirm": 4, "investigate": 5, "wait": 6}
    # Merges first, each repository's stack from its base; then routing, decisions and the rest.
    levers.sort(key=lambda x: (order.get(x["lever"], 9), x.get("stack", ("", 0, 0)), x.get("where", "")))
    actionable = [x for x in levers if x["lever"] != "wait"]

    def days(x):
        t = x.get("age", "")
        if t.endswith(" days"):
            return float(t.split()[0])
        if t.endswith(" h"):
            return float(t.split()[0]) / 24
        return 0.0
    defaulting = [x for x in actionable if days(x) >= a.stale_days]
    since = NOW - timedelta(days=a.days)
    recent = [d for d in decisions
              if (when(d.get("date")) or NOW) >= since and d.get("status") in ("adopted", "rejected")]

    out = [f"# Decisions and human control — {NOW.astimezone().strftime('%Y-%m-%d %H:%M %Z')}", ""]
    out.append(f"**{len(actionable)} lever(s) waiting on you**; {len(defaulting)} of them have waited long enough "
               f"that doing nothing is already the choice. Ordered so that items blocking other work come first.")
    out += ["", "## 1. Your levers", "", table(actionable) if actionable else "Nothing is waiting on you.", ""]
    waits = [x for x in levers if x["lever"] == "wait"]
    if waits:
        out += ["Not yet actionable: " + "; ".join(f"{x['where']} ({x['what'][:60]})" for x in waits), ""]
    out += ["## 2. Choices you're making by default", ""]
    out += [f"- **{x['where']}** ({x['age']}): {x['default']}." for x in defaulting] or ["None yet."]
    out += ["", f"## 3. What you decided in the last {a.days} days", ""]
    if recent:
        out += ["| Id | Date | Decision | Your words |", "|---|---|---|---|"]
        for d in sorted(recent, key=lambda d: d["id"], reverse=True):
            basis = d.get("basis", "").replace("|", "/").replace("\n", " ")
            decision = d["decision"][:140].replace("|", "/")
            out.append(f"| {d['id']} | {d.get('date', '')} | {decision}… | {basis[:120]} |")
    else:
        out.append("No recorded decisions in that window.")
    out += ["", "## 4. Standing ambitions (kept open, not commitments)", ""]
    out += [f"- **{r['id']}**: {r.get('text', '')}" for r in ambitions] or ["None recorded."]
    if notes:
        out += ["", "## Not read", ""] + [f"- {x['what']}" for x in notes]
    out += ["", "_Sources: open PRs (GitHub), relay-kit decisions, handoffs and candidates, Telosmith records. "
            "Read-only. Experiment EXP-owner-report (DEC-033)._", ""]
    text = "\n".join(out)
    if a.output:
        a.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
