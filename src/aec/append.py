"""Append one record, computing its source anchors (DEC-095 adoption friction).

Writing an anchor by hand means hashing the file and checking the locator; this does both, refuses a record
that `check` would reject or whose id@version already exists, and only ever appends a line.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .records import Store, check
from .sources import SourceContext, anchor_errors, locate


def parse_anchor_spec(spec: str) -> tuple[str | None, str, str]:
    """`[ALIAS=]PATH#LOCATOR` -> (alias or None, path, locator)."""
    alias = None
    head, sep, locator = spec.partition("#")
    if not sep or not locator:
        raise ValueError(f"anchor {spec!r}: expected [ALIAS=]PATH#LOCATOR (locator L<n>, L<a>-<b> or q:<text>)")
    if "=" in head:
        alias, _, head = head.partition("=")
    return alias or None, head, locator


def make_anchor(context: SourceContext, spec: str, field: str = "text") -> dict:
    """An anchor for the file as it is now: its sha256, the locator checked against it, and, for a file declared
    append-only in .aec/sources.json, prefix_bytes so later appends read as `appended` rather than `mismatch`."""
    alias, path, locator = parse_anchor_spec(spec)
    anchor = {"path": Path(path).as_posix(), "sha256": "0" * 64, "locator": locator, "for": field}
    if alias:
        anchor["root"] = alias
    errors = anchor_errors(anchor)
    if errors:
        raise ValueError(f"anchor {spec!r}: " + "; ".join(errors))
    root = context.root(alias)
    if root is None:
        raise ValueError(f"anchor {spec!r}: root {alias!r} is not configured in .aec/sources.json")
    state, raw = context.read(root, anchor["path"])
    if raw is None:
        raise ValueError(f"anchor {spec!r}: {anchor['path']} is {state} under {root.display}")
    if locate(locator, tuple(raw.decode("utf-8", errors="replace").splitlines())) is None:
        raise ValueError(f"anchor {spec!r}: locator {locator!r} does not resolve in {anchor['path']}")
    anchor["sha256"] = hashlib.sha256(raw).hexdigest()
    if context.is_append_only(alias, anchor["path"]):
        anchor["prefix_bytes"] = len(raw)
    return anchor


def build(records: Path, record: dict, anchors: list[str], rationale_anchors: list[str],
          repo: Path) -> tuple[str, list[str]]:
    """The line to append and the reasons it must not be (empty when it may)."""
    if not isinstance(record, dict):
        return "", ["the record must be a JSON object"]
    context = SourceContext(repo)
    made = [make_anchor(context, s, "text") for s in anchors] + [make_anchor(context, s, "rationale")
                                                                for s in rationale_anchors]
    if made:
        record = dict(record)
        record["anchors"] = list(record.get("anchors", [])) + made
    line = json.dumps(record, ensure_ascii=False)
    store = Store.load(records)
    ref = f"{record.get('id')}@{record.get('version')}"
    if ref in store.by_ref:
        return line, [f"{ref} already exists in {records}: append the next version instead"]
    trial = records.with_name(records.name + ".append-check")
    try:
        text = records.read_text(encoding="utf-8")
        trial.write_text(text + ("" if text.endswith("\n") or not text else "\n") + line + "\n", encoding="utf-8")
        new_store = Store.load(trial)
    finally:
        trial.unlink(missing_ok=True)
    before = {(f.rule, f.ref, f.msg) for f in check(store, sources=context) if f.level == "error"}
    problems = [f"{f.rule}: {f.ref}: {f.msg}" for f in check(new_store, sources=context)
                if f.level == "error" and (f.rule, f.ref, f.msg) not in before]
    return line, problems


def append_line(records: Path, line: str) -> None:
    with records.open("rb+") as f:
        f.seek(0, 2)
        if f.tell():
            f.seek(-1, 2)
            if f.read(1) != b"\n":
                f.write(b"\n")
        f.write(line.encode("utf-8") + b"\n")
