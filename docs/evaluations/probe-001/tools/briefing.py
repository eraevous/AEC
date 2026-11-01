#!/usr/bin/env python3
"""probe-001 briefing generator: AEC structural neighbourhood of named symbols, from an
`aec edges` snapshot. Mechanical by design: no hand editing of its output.

Usage:
  briefing.py EDGES.jsonl SYMBOL [SYMBOL ...]          print the briefing block
  briefing.py EDGES.jsonl --decoy-for SYMBOL           print the rule-chosen decoy symbol

Decoy rule (pre-registered): the function or method in a different module whose resolved-caller
count is closest to the task symbol's; ties broken alphabetically.
"""
import json
import sys
from collections import defaultdict


def load(path):
    with open(path, encoding="utf-8") as f:
        header = json.loads(f.readline())
        edges = [json.loads(line) for line in f if line.strip()]
    return header, edges


def index(edges):
    by_dst, by_src, defs = defaultdict(list), defaultdict(list), {}
    for e in edges:
        by_dst[e["dst"]].append(e)
        by_src[e["src"]].append(e)
        if e["kind"] == "defines":
            defs[e["dst"]] = e
    return by_dst, by_src, defs


def module_of(sym, header):
    mods = header.get("modules", {})
    parts = sym.split(".")
    for i in range(len(parts), 0, -1):
        if ".".join(parts[:i]) in mods:
            return ".".join(parts[:i])
    return ".".join(parts[:-1])


def callers(sym, by_dst):
    return sorted({(e["src"], e["file"], e["line"]) for e in by_dst.get(sym, [])
                   if e["kind"] == "calls" and e.get("resolved")}, key=lambda t: (t[1], t[2], t[0]))


def neighbourhood(sym, header, by_dst, by_src, defs):
    out = [f"### `{sym}`"]
    d = defs.get(sym)
    out.append(f"- Defined at: {d['file']}:{d['line']}" if d else "- Defined at: not found in the snapshot")
    cs = callers(sym, by_dst)
    out.append(f"- Resolved callers ({len(cs)}):" if cs else "- Resolved callers: none found")
    out += [f"  - `{s}` ({f}:{l})" for s, f, l in cs]
    mod = module_of(sym, header)
    parts = sym.split(".")
    scopes = [".".join(parts[:i]) for i in range(len(mod.split(".")), len(parts) + 1)]
    imps = sorted({(e["src"], e["file"], e["line"]) for sc in scopes for e in by_dst.get(sc, [])
                   if e["kind"] == "imports"}, key=lambda t: (t[1], t[2]))
    if imps:
        out.append(f"- Imported by ({len(imps)}; this symbol, its class or its module `{mod}`):")
        out += [f"  - {f}:{l}" for _, f, l in imps]
    refs = sorted({(e["src"], e["file"], e["line"]) for e in by_dst.get(sym, []) if e["kind"] == "references"},
                  key=lambda t: (t[1], t[2]))
    if refs:
        out.append(f"- Referenced (not called) by ({len(refs)}):")
        out += [f"  - `{s}` ({f}:{l})" for s, f, l in refs]
    callees = sorted({e["dst"] for e in by_src.get(sym, []) if e["kind"] == "calls"})
    if callees:
        out.append(f"- Calls ({len(callees)}): " + ", ".join(f"`{c}`" for c in callees))
    bases = sorted({e["dst"] for e in by_src.get(sym, []) if e["kind"] == "inherits"})
    derived = sorted({e["src"] for e in by_dst.get(sym, []) if e["kind"] == "inherits"})
    if bases:
        out.append("- Inherits from: " + ", ".join(f"`{b}`" for b in bases))
    if derived:
        out.append("- Inherited by: " + ", ".join(f"`{x}`" for x in derived))
    return "\n".join(out)


def briefing(header, edges, syms):
    by_dst, by_src, defs = index(edges)
    unresolved = sum(1 for e in edges if e["kind"] == "calls" and not e.get("resolved"))
    total_calls = sum(1 for e in edges if e["kind"] == "calls")
    parts = ["## Structural context from AEC",
             "",
             "Generated from a static analysis snapshot of this repository (`aec edges`). It lists "
             "what the code itself shows about the symbols below. It is structural only.",
             ""]
    parts += [neighbourhood(s, header, by_dst, by_src, defs) + "\n" for s in syms]
    parts.append(f"Across the repository, {unresolved} of {total_calls} calls could not be resolved to a "
                 "target (for example method calls on objects whose type the code does not state), so "
                 "the caller lists above may be incomplete. No known caller is not proof of no caller.")
    return "\n".join(parts)


def decoy_for(header, edges, sym, forbidden_files=(), log=None):
    """Rule-chosen decoy, skipping candidates whose briefing names any file on the task's dependency
    path (amendment 3). Rejections are appended to `log`."""
    by_dst, by_src, defs = index(edges)
    for cand in decoy_candidates(header, edges, sym):
        text = neighbourhood(cand, header, by_dst, by_src, defs)
        hits = sorted(f for f in forbidden_files if f in text)
        if hits:
            if log is not None:
                log.append(f"rejected {cand}: briefing names {', '.join(hits)}")
            continue
        return cand
    return None


def decoy_candidates(header, edges, sym):
    by_dst, _, defs = index(edges)
    n = len(callers(sym, by_dst))
    own = module_of(sym, header)
    cands = []
    for d in defs:
        if module_of(d, header) == own or d == sym:
            continue
        de = defs[d]
        # functions and methods only: a defined symbol that is itself the src of some edge or is called
        if not any(e["kind"] == "calls" for e in by_dst.get(d, [])) and n > 0:
            continue
        cands.append((abs(len(callers(d, by_dst)) - n), d))
    cands.sort()
    return [c for _, c in cands]


if __name__ == "__main__":
    h, es = load(sys.argv[1])
    if sys.argv[2] == "--decoy-for":
        log = []
        print(decoy_for(h, es, sys.argv[3], sys.argv[4:], log))
        for line in log:
            print("#", line, file=sys.stderr)
    else:
        print(briefing(h, es, sys.argv[2:]))
