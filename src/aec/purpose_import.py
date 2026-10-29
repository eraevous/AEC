"""`aec import-purpose`: Codex++ `.purpose.md` files -> provisional, provenance-linked records (feature 002, US2).

What a purpose file says is what the repository *claimed* about a module, often model-generated and
never verified. It is imported as exactly that: a `source` record for the file (path, content hash,
the file's own generated/verified flags) and a provisional, candidate-tier `claim` holding the declared
text verbatim. Import never creates an authority and never commits anything, so it cannot stand in for
what the code does (the edge snapshot says that) or for what the owner wants now (a purpose record the
owner writes). Where the file's declarations can be compared with the code, differences are reported
as findings and nothing is corrected. Standard library only; records are appended, never rewritten.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .records import CODE, Store

HEADER = re.compile(r"^\s*(?:[-#]\s*)?@([\w-]+):\s*(.*?)\s*$")
PLACEHOLDER = re.compile(r"<[^<>]+>")
PEOPLE = {"developer", "developers", "user", "users", "human", "humans", "analyst", "analysts",
          "maintainer", "maintainers", "stakeholder", "stakeholders", "operator", "operators"}


def _slug(rel: Path) -> str:
    name = rel.as_posix()
    for suffix in (".purpose.md", ".md"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", name).strip("-")


def _strip_comment(v: str) -> str:
    return re.sub(r"\s+#.*$", "", v).strip()


def _list(v: str) -> list[str]:
    v = _strip_comment(v).strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]


def _bool(v: str | None):
    if v is None:
        return None
    return {"true": True, "false": False}.get(_strip_comment(v).lower())


def _title(text: str) -> str:
    """Normalise observed heading/column labels, not their declared content."""
    words = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return re.sub(r"^\d+\s*", "", words).strip()


def _section_kind(title: str) -> str | None:
    if "risk" in title:
        return "risks"
    if "input" in title or "output" in title:
        return "io"
    if "dependenc" in title:
        return "dependencies"
    if "integration" in title or "pipeline" in title:
        return "integration"
    if "test guarantee" in title:
        return "guarantees"
    if "intent" in title or "responsib" in title:
        return "responsibilities"
    return None


def _cells(line: str) -> list[str]:
    # An escaped pipe or a pipe inside code is content, not a column boundary.
    cells, cell, ticks = [], [], False
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    escaped = False
    for char in line:
        if char == "|" and not escaped and not ticks:
            cells.append("".join(cell).strip())
            cell = []
        else:
            cell.append(char)
            if char == "`" and not escaped:
                ticks = not ticks
        escaped = char == "\\" and not escaped
    cells.append("".join(cell).strip())
    return cells


def _io_rows(body: str, title: str) -> list[dict]:
    rows, columns = [], None
    default = "input" if "input" in title and "output" not in title else (
        "output" if "output" in title and "input" not in title else "")
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            columns = None
            continue
        values = _cells(line)
        if all(re.fullmatch(r":?-+:?", value.replace(" ", "")) for value in values):
            continue
        if columns is None:
            columns = [{"brief description": "description"}.get(_title(v), _title(v)) for v in values]
            continue
        if "name" not in columns or len(values) != len(columns):
            continue
        row = dict(zip(columns, values))
        direction = _title(row.get("direction", default))
        row["direction"] = {"in": "input", "out": "output"}.get(direction, direction)
        rows.append({**dict.fromkeys(("direction", "name", "type", "description"), ""), **row})
    return rows


def _contracts(text: str) -> dict:
    lines = text.splitlines(keepends=True)
    sections = []
    for i, line in enumerate(lines):
        match = re.match(r"^\s*(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match and not HEADER.match(line):
            sections.append((i, len(match[1]), _title(match[2])))
    declared = {"declared_sections": {}, "declared_io": []}
    for kind in ("risks", "dependencies", "integration", "guarantees"):
        declared["declared_" + kind] = []
    for pos, (start, level, title) in enumerate(sections):
        end = next((j for j, depth, _ in sections[pos + 1:] if depth <= level), len(lines))
        direct_end = sections[pos + 1][0] if pos + 1 < len(sections) else len(lines)
        direct = "".join(lines[start + 1:direct_end])
        declared["declared_sections"].setdefault(title, []).append(direct)
        kind = _section_kind(title)
        if kind == "io":
            declared["declared_io"].extend(_io_rows(direct, title))
        elif kind in ("risks", "dependencies", "integration", "guarantees"):
            declared["declared_" + kind].append("".join(lines[start + 1:end]))
    return declared


def parse(text: str) -> dict:
    """Header fields (`@ai-*`) and the verbatim declared text (intent plus the Intent & Responsibility section)."""
    headers: dict[str, str] = {}
    fields: dict[str, str | list[str]] = {}
    for line in text.splitlines():
        m = HEADER.match(line)
        if m:
            name, value = m.groups()
            headers.setdefault(name, value)
            if name not in fields:
                fields[name] = value
            elif isinstance(fields[name], list):
                fields[name].append(value)
            else:
                fields[name] = [fields[name], value]
    lines, section, grab = text.splitlines(), [], False
    for line in lines:
        if line.lstrip().startswith("#"):
            grab = "intent" in line.lower() and "responsib" in line.lower()
            continue
        if line.strip() == "---":
            grab = False
            continue
        if grab and line.strip():
            section.append(line.rstrip())
    intent = _strip_comment(headers.get("ai-intent", "")).strip("'\"")
    if headers:
        declared = "\n".join(x for x in [intent] + section if x)
    else:  # no headers: keep the prose itself, verbatim
        declared = "\n".join(l.rstrip() for l in lines if l.strip() and not l.lstrip().startswith("#"))
    return {"headers": headers, "intent": intent, "declared_text": declared,
            "declared_fields": fields, "declared_raw": text, **_contracts(text)}


def _module_maps(edges: dict) -> tuple[dict[str, str], dict[str, list[str]]]:
    by_module = dict(edges["header"].get("modules", {}))
    if not by_module:  # snapshot older than tool_version 0.3.0: derive module names from file paths
        from .edges import _module_name
        for e in edges["edges"]:
            by_module.setdefault(_module_name(Path(e["file"])), e["file"])
    by_file = {f: m for m, f in by_module.items()}
    by_base: dict[str, list[str]] = {}
    for f in by_file:
        by_base.setdefault(Path(f).name, []).append(f)
    return by_file, by_base


def _module_of(sym: str, modules: set[str]) -> str | None:
    parts = sym.split(".")
    for i in range(len(parts), 0, -1):
        cand = ".".join(parts[:i])
        if cand in modules:
            return cand
    return None


def observed_callers(edges: dict, module: str) -> set[str]:
    """Modules that import, or call into, `module` (structural; dynamic use is invisible)."""
    by_file, _ = _module_maps(edges)
    modules = set(by_file.values())
    out = set()
    for e in edges["edges"]:
        dst = e["dst"]
        if not (dst == module or dst.startswith(module + ".")):
            continue
        if e["kind"] not in ("imports", "calls"):
            continue
        caller = _module_of(e["src"], modules)  # function-local imports have a function as src
        if caller and caller != module and not caller.startswith(module + "."):
            out.add(caller)
    return out


def _resolve(name: str, root: Path, by_file: dict, by_base: dict) -> tuple[str | None, dict | None]:
    """(module, None) on an unambiguous match, else (None, finding)."""
    if not name.endswith(".py"):
        return None, {"kind": "not-code", "detail": name}
    if name in by_file:
        return by_file[name], None
    hits = sorted(by_base.get(Path(name).name, []))
    if len(hits) == 1 and "/" not in name:
        return by_file[hits[0]], None
    if len(hits) > 1:
        return None, {"kind": "ambiguous-source", "detail": f"{name}: {', '.join(hits)}"}
    return None, {"kind": "missing-source", "detail": name}


def import_purpose(root: Path, purpose_dir: Path, records_path: Path, edges: dict, dry_run: bool = False) -> dict:
    root, purpose_dir, records_path = Path(root), Path(purpose_dir), Path(records_path)
    store = Store.load(records_path) if records_path.exists() else Store([])
    by_file, by_base = _module_maps(edges)
    module_names = set(by_file.values())
    last = {}
    for m in module_names:
        last.setdefault(m.rsplit(".", 1)[-1], set()).add(m)

    rep = {"imported": [], "unchanged": [], "skipped": [], "findings": [], "appended": 0}
    new_rows: list[dict] = []
    for path in sorted(purpose_dir.rglob("*.md")):
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
        raw = path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        p = parse(raw.decode("utf-8", errors="replace"))
        h = p["headers"]
        note = lambda kind, detail="": rep["findings"].append({"file": rel, "kind": kind, "detail": detail})

        if any(PLACEHOLDER.search(h.get(k, "")) for k in ("ai-path", "ai-source-file", "ai-source-files", "ai-intent")):
            rep["skipped"].append({"file": rel, "reason": "template (placeholder values)"})
            continue
        slug = _slug(path.relative_to(purpose_dir))
        sid, cid = f"PF-{slug}", f"PC-{slug}"
        prev = store.latest.get(sid)
        if prev is not None and prev.get("sha256") == sha:
            rep["unchanged"].append(rel)
            continue
        version = (prev.version + 1) if prev is not None else 1

        if not h:
            note("no-headers")
        code_links, modules = [], []
        source_files = list(dict.fromkeys(_list(h.get("ai-source-file", ""))
                                          + _list(h.get("ai-source-files", ""))))
        if "ai-source-file" in h and "ai-source-files" in h:
            note("duplicate-source-field", "both singular and plural source fields; using their union")
        for name in source_files:
            mod, finding = _resolve(name, root, by_file, by_base)
            if finding:
                note(**finding)
            else:
                modules.append(mod)
                code_links.append(CODE + mod)

        declared_users = _list(h.get("ai-used-by", ""))
        if modules:
            observed = set().union(*(observed_callers(edges, m) for m in modules))
            observed_last = {o.rsplit(".", 1)[-1] for o in observed}
            people = sorted(u for u in declared_users if u.lower() in PEOPLE)
            for u in people:
                note("non-code-consumer", u)
            for u in sorted(set(declared_users) - set(people)):
                if u.rsplit(".", 1)[-1] not in observed_last:
                    note("declared-not-observed", u)
            for o in sorted(observed):
                if o.rsplit(".", 1)[-1] not in {u.rsplit(".", 1)[-1] for u in declared_users}:
                    note("observed-not-declared", o)

        source = {"id": sid, "version": version, "type": "source", "subject": "repo-claims",
                  "text": f"Codex++ purpose file {rel}", "ref": rel, "sha256": sha,
                  "origin": "codex++ purpose file", "imported_by": "aec import-purpose",
                  "ai_generated": _bool(h.get("ai-generated")), "ai_verified": _bool(h.get("ai-verified"))}
        if prev is not None:
            source["relations"] = [{"rel": "supersedes", "to": prev.ref}]
        subject = _strip_comment(h.get("ai-path", "")) or slug
        claim = {"id": cid, "version": version, "type": "claim", "subject": f"module:{subject}",
                 "tier": "candidate", "epistemic": "provisional", "origin": "imported",
                 "text": f"{rel} declares: {p['intent'] or '(no @ai-intent)'}",
                 "declared_text": p["declared_text"],
                 "declared_source_files": source_files,
                 **{k: v for k, v in p.items() if k.startswith("declared_")},
                 "declared_used_by": declared_users,
                 "relations": [{"rel": "depends_on", "to": f"{sid}@{version}"}]
                              + [{"rel": "depends_on", "to": c} for c in code_links]}
        if prev is not None and f"{cid}@{prev.version}" in store.by_ref:
            claim["relations"].append({"rel": "supersedes", "to": f"{cid}@{prev.version}"})
        new_rows += [source, claim]
        rep["imported"].append({"file": rel, "source": f"{sid}@{version}", "claim": f"{cid}@{version}",
                                "code": code_links})

    rep["appended"] = len(new_rows)
    if new_rows and not dry_run:
        records_path.parent.mkdir(parents=True, exist_ok=True)
        existing = records_path.read_text(encoding="utf-8") if records_path.exists() else ""
        sep = "" if not existing or existing.endswith("\n") else "\n"
        with records_path.open("a", encoding="utf-8") as f:
            f.write(sep + "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in new_rows))
    return rep


def render(rep: dict) -> str:
    out = ["# aec import-purpose (structural: what the files declared, compared with the code)", ""]
    for i in rep["imported"]:
        out.append(f"imported  {i['file']} -> {i['claim']}" + (f"  [{', '.join(i['code'])}]" if i["code"] else "  [no code link]"))
    for u in rep["unchanged"]:
        out.append(f"unchanged {u}")
    for s in rep["skipped"]:
        out.append(f"skipped   {s['file']}: {s['reason']}")
    if rep["findings"]:
        out.append("")
        for f in rep["findings"]:
            out.append(f"[{f['kind']}] {f['file']}" + (f": {f['detail']}" if f.get("detail") else ""))
    out.append(f"\n{rep['appended']} record(s) appended. Imported claims are provisional and candidate-tier: "
               "they record what the repository claimed, not what the code does or what the owner wants.")
    return "\n".join(out)
