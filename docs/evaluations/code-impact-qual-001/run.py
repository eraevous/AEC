"""code-impact-qual-001: run the frozen link mappings through Codex's A5RR cases.

Usage: PYTHONPATH=<tool src> python3 run.py   (prints a Markdown table; standard library only)
The fixture is Codex's: price(x) = min(LIMIT, helper(x)), LIMIT = 10, helper(x) = max(0, x).
"""
import tempfile
from pathlib import Path

from aec import edges as E
from aec.code_impact import code_impact
from aec.records import Store

HERE = Path(__file__).resolve().parent
BASE = "LIMIT = 10\n\n\ndef helper(x):\n    return max(0, x)\n\n\ndef price(x):\n    return min(LIMIT, helper(x))\n"
CASES = [
    ("no edit", "preserved", lambda s: s),
    ("add a comment", "preserved", lambda s: s.replace("def price(x):", "def price(x):\n    # clamp")),
    ("swap min arguments", "preserved", lambda s: s.replace("min(LIMIT, helper(x))", "min(helper(x), LIMIT)")),
    ("price returns its input", "broken", lambda s: s.replace("return min(LIMIT, helper(x))", "return x")),
    ("remove helper's lower bound", "broken", lambda s: s.replace("max(0, x)", "x")),
    ("raise LIMIT to 100", "broken", lambda s: s.replace("LIMIT = 10", "LIMIT = 100")),
    ("add an unrelated function", "preserved", lambda s: s + "\n\ndef other():\n    return 1\n"),
]


def snap(src):
    d = Path(tempfile.mkdtemp())
    (d / "pricing.py").write_text(src)
    return E.snapshot(d)


def cell(rep):
    st = ", ".join(f"{k.split('@')[0]} {v.status}" for k, v in sorted(rep.impacts.items()))
    ptr = [f for f in rep.findings if "reaches changed" in f]
    out = st or "none"
    if ptr:
        out += "; pointer: " + ", ".join(f.split("reaches changed ")[1].split(" ")[0] for f in ptr)
    return out


old = snap(BASE)
maps = [("function link", Store.load(HERE / "mapping-function.jsonl")), ("module link", Store.load(HERE / "mapping-module.jsonl"))]
print("| change | sample behaviour | " + " | ".join(m for m, _ in maps) + " |")
print("|---|---|" + "---|" * len(maps))
for name, behaviour, edit in CASES:
    new = snap(edit(BASE))
    print(f"| {name} | {behaviour} | " + " | ".join(cell(code_impact(s, old, new)[0]) for _, s in maps) + " |")
