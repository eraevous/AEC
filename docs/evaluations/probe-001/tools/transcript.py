#!/usr/bin/env python3
"""Summarise a trial's subagent transcript: tool calls (name + key arg), usage, first-edit index,
final text. Writes trials/<id>/transcript_summary.json and REPORT.md (from final text) if absent."""
import json, sys
from pathlib import Path

TASKS = Path("/tmp/claude-0/-home-claude/bc494696-1b8d-58d8-947e-801d4f8541e2/tasks")
ROOT = Path("/tmp/claude-0/probe/trials")
for line in Path("/root/.cache/p001-sealed/agents.tsv").read_text().split("\n"):
    if not line.strip():
        continue
    tid, aid = line.split("\t")
    f = TASKS / f"{aid}.output"
    if not f.exists():
        continue
    calls, usage, final = [], {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}, ""
    for l in f.read_text().splitlines():
        try:
            j = json.loads(l)
        except Exception:
            continue
        if j.get("type") != "assistant":
            continue
        m = j.get("message", {})
        u = m.get("usage") or {}
        usage["input"] += u.get("input_tokens", 0)
        usage["output"] += u.get("output_tokens", 0)
        usage["cache_read"] += u.get("cache_read_input_tokens", 0)
        usage["cache_write"] += u.get("cache_creation_input_tokens", 0)
        texts = []
        for b in m.get("content", []) or []:
            if b.get("type") == "tool_use":
                inp = b.get("input", {})
                arg = inp.get("file_path") or inp.get("path") or inp.get("pattern") or inp.get("command") or ""
                calls.append([b.get("name"), str(arg)[:200]])
            elif b.get("type") == "text":
                texts.append(b.get("text", ""))
        if texts:
            final = "\n".join(texts)
    s = {"trial": tid, "tool_calls": len(calls), "calls": calls, "usage": usage, "complete": bool(final)}
    (ROOT / tid / "transcript_summary.json").write_text(json.dumps(s, indent=1))
    rep = ROOT / tid / "REPORT.md"
    if final and (not rep.exists() or rep.read_text().startswith("<!-- recovered")):
        rep.write_text("<!-- recovered from the agent's final message; it could not write this file itself -->\n" + final)
    print(tid, len(calls), usage["output"], "final" if final else "running")
