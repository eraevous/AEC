"""AEC edges: deterministic structural facts from Python source (the bedrock, Constitution VI).

Edge kinds: defines, calls, imports, inherits, references. Standard library only.

  snapshot(root) -> {"header": {...}, "edges": [...]}
  dumps(snapshot) / loads(text)  - JSON lines, header first, edges stably sorted
  diff(old, new)                 - added/removed edges + added/removed/changed definitions
  legacy_csv(snapshot)           - the 2025 extractor's Source,Call format, for comparison

Resolution rules (research R1): a call or read resolves through local bindings (unresolved),
module-level definitions, imports (explicit and star, in statement order), and `self.x` against the
enclosing class and its known bases. Builtins are dropped. Anything else that is called is kept as
an unresolved `?expr` target, never guessed. Reads that don't resolve are not edges.
"""
from __future__ import annotations

import ast
import builtins
import hashlib
import fnmatch
import json
import sys
import tokenize
import warnings
from pathlib import Path

TOOL_VERSION = "0.4.0"
KINDS = ("defines", "imports", "inherits", "calls", "references")
BUILTINS = set(dir(builtins))
DEFAULT_IGNORE = {".git", ".venv", "venv", "env", "__pycache__", ".tox", "node_modules", "build", "dist",
                  ".specify", ".claude", "site-packages"}


def sort_key(e: dict):
    return (KINDS.index(e["kind"]) if e["kind"] in KINDS else 99, e["src"], e["dst"], e["file"], e["line"])


def ignored(rel: Path, patterns) -> bool:
    return any(part.endswith(".egg-info") for part in rel.parts[:-1]) or any(
        fnmatch.fnmatchcase(rel.as_posix(), pattern) or any(fnmatch.fnmatchcase(part, pattern) for part in rel.parts)
        for pattern in patterns)


def _module_name(rel: Path) -> str:
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _sha(node: ast.AST) -> str:
    return hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()[:12]


def _dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


def _expr_label(node: ast.AST) -> str:
    d = _dotted(node)
    if d:
        return d
    if isinstance(node, ast.Call):
        return _expr_label(node.func) + "(...)"
    if isinstance(node, ast.Attribute):
        return _expr_label(node.value) + "." + node.attr
    if isinstance(node, ast.Subscript):
        return _expr_label(node.value) + "[...]"
    return type(node).__name__.lower()


class _Module:
    """A parsed module's lightweight index. The AST itself is not kept (memory stays bounded): it is
    re-parsed once for the body scan."""

    def __init__(self, name: str, rel: str, path: Path, is_pkg: bool):
        self.name, self.rel, self.path, self.is_pkg = name, rel, path, is_pkg
        self.top_defs: dict[str, str] = {}   # bare name -> symbol (classes, functions, assigned names)
        self.order: list = []                # module-level ('imp', node) | ('name', bare) in statement order
        self.class_bases: list = []          # (class symbol, [base expr nodes], class node line)
        self.exports = None
        self.bindings: dict[str, str] = {}   # final module namespace: name -> dotted target


class _Extractor:
    def __init__(self, root: Path, ignore: set[str], source_roots="auto"):
        self.root, self.ignore = root, ignore
        self.source_root_config = source_roots
        self.modules: dict[str, _Module] = {}
        self.skipped: list[dict] = []
        self.file_hashes: list[str] = []
        self.edges: dict[tuple, tuple] = {}  # (kind, src, dst) -> (file, line); compact for large trees
        self._all_def_names: set[str] = set()
        self._class_syms: set[str] = set()
        self.defs: dict[str, str] = {}       # symbol -> body sha
        self.class_bases: dict[str, list[str]] = {}
        self.import_modules = {}

    # ---------- pass 0: files ----------
    def files(self):
        out = []
        for p in sorted(self.root.rglob("*.py")):
            rel = p.relative_to(self.root)
            if ignored(rel, self.ignore):
                continue
            if p.is_symlink() or not p.is_file():
                self.skipped.append({"file": rel.as_posix(), "reason": "non-regular source not parsed"})
                continue
            out.append((p, rel))
        return out

    @staticmethod
    def parse(path: Path, rel: Path):
        with tokenize.open(path) as f:
            src = f.read()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # e.g. SyntaxWarning for invalid escapes in analysed code
            return ast.parse(src, filename=str(rel))

    def load(self):
        """Pass 1: parse each file once, index it, and drop the tree."""
        for p, rel in self.files():
            raw = p.read_bytes()
            self.file_hashes.append(f"{rel.as_posix()}:{hashlib.sha256(raw).hexdigest()}")
            try:
                tree = self.parse(p, rel)
            except (SyntaxError, UnicodeDecodeError, LookupError, ValueError) as ex:
                self.skipped.append({"file": rel.as_posix(), "reason": f"{type(ex).__name__}: {ex}".replace(str(p), rel.as_posix()).splitlines()[0][:200]})
                continue
            m = _Module(_module_name(rel), rel.as_posix(), p, rel.name == "__init__.py")
            self.modules[m.name] = m
            self.index(m, tree)
            del tree

    def index(self, m: _Module, tree: ast.Module):
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                m.order.append(("imp", node))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                m.top_defs[node.name] = f"{m.name}.{node.name}"
                m.order.append(("name", node.name))
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name):
                        m.top_defs[t.id] = f"{m.name}.{t.id}"
                        m.order.append(("name", t.id))
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(t, ast.Name) and t.id == "__all__" for t in targets):
                    try:
                        names = ast.literal_eval(node.value)
                        m.exports = list(names) if isinstance(names, (list, tuple)) and all(isinstance(n, str) for n in names) else None
                    except (ValueError, TypeError, SyntaxError):
                        m.exports = None
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == "__all__":
                m.exports = None
        # A literal is useful only while other writes/uses do not make it uncertain.
        all_targets = {id(t) for node in tree.body if isinstance(node, (ast.Assign, ast.AnnAssign))
                       for t in (node.targets if isinstance(node, ast.Assign) else [node.target])
                       if isinstance(t, ast.Name) and t.id == "__all__"}
        if any((isinstance(node, ast.Name) and node.id == "__all__" and id(node) not in all_targets)
               or (isinstance(node, ast.alias) and (node.asname or node.name.split(".")[0]) == "__all__")
               for node in ast.walk(tree)):
            m.exports = None
        self.collect_all_defs(m, tree)

    # ---------- helpers ----------
    def edge(self, kind, src, dst, mod: _Module, node, why=None):
        key = (kind, src, dst)
        line = getattr(node, "lineno", 0)
        cur = self.edges.get(key)
        if cur is None or line < cur[1]:
            self.edges[key] = (mod.rel, line, why)

    def _abs_module(self, mod: _Module, node: ast.ImportFrom) -> str:
        if not node.level:
            return node.module or ""
        pkg = mod.name.split(".") if mod.is_pkg else mod.name.split(".")[:-1]
        if node.level > 1:
            pkg = pkg[: len(pkg) - (node.level - 1)]
        return ".".join([p for p in pkg + ([node.module] if node.module else []) if p])

    def _import_bindings(self, mod: _Module, node, src: str, bind: dict):
        if isinstance(node, ast.Import):
            for a in node.names:
                target = self._alias(a.name)
                self.edge("imports", src, target, mod, node)
                self.import_modules.setdefault((src, target), target)
                if a.asname:
                    bind[a.asname] = target
                else:
                    top = a.name.split(".")[0]
                    bind[top] = self._alias(top)
        else:
            base = self._abs_module(mod, node)
            if not node.level:
                base = self._alias(base)
            for a in node.names:
                if a.name == "*":
                    self.edge("imports", src, f"{base}.*", mod, node)
                    self.import_modules.setdefault((src, f"{base}.*"), base)
                    target = self.modules.get(base)
                    if target:
                        for n, sym in target.top_defs.items():
                            if not n.startswith("_"):
                                bind[n] = sym
                    continue
                full = f"{base}.{a.name}" if base else a.name
                self.edge("imports", src, full, mod, node)
                self.import_modules.setdefault((src, full), full if full in self.modules else base)
                bind[a.asname or a.name] = full

    def build_source_root_aliases(self):
        """Code run with a source directory on sys.path imports `src/x.py` as `x`. Map such bare
        top-level imports to the module that exists (`x` -> `src.x`), only when unambiguous and not a
        stdlib name. Recorded in the header as `source_roots` so the mapping is visible."""
        tops = {name.split(".")[0] for name in self.modules}
        cand: dict[str, set[str]] = {}
        for name in self.modules:
            parts = name.split(".")
            if len(parts) >= 2:
                cand.setdefault(parts[1], set()).add(parts[0])
        stdlib = getattr(sys, "stdlib_module_names", frozenset())
        self.root_alias = {x: f"{next(iter(roots))}.{x}" for x, roots in cand.items()
                           if len(roots) == 1 and x not in tops and x not in stdlib}
        if self.source_root_config != "auto":
            candidates = {}
            for prefix in self.source_root_config:
                dotted = _module_name(Path(prefix + "/__init__.py"))
                for name in self.modules:
                    if name.startswith(dotted + "."):
                        suffix = name[len(dotted)+1:]
                        top = suffix.split(".")[0]
                        if top not in tops and top not in stdlib:
                            candidates.setdefault(top, set()).add(dotted + "." + top)
            self.root_alias = {name: next(iter(values)) for name, values in candidates.items() if len(values) == 1}
        self.source_roots_used: set[str] = set()

    def _alias(self, dotted: str) -> str:
        top, _, rest = dotted.partition(".")
        target = self.root_alias.get(top)
        if not target:
            return dotted
        self.source_roots_used.add(target.split(".")[0])
        return f"{target}.{rest}" if rest else target

    def build_module_bindings(self):
        self.build_source_root_aliases()
        for m in self.modules.values():
            bind: dict[str, str] = {}
            for kind, item in m.order:   # statement order: later bindings win, like Python
                if kind == "imp":
                    self._import_bindings(m, item, m.name, bind)
                else:
                    bind[item] = f"{m.name}.{item}"
            m.bindings = bind
            m.order = []

    def resolve(self, dotted: str, mod: _Module, local_bind: dict, locals_: set, cls: str | None):
        """Return (target, resolved) or (None, None) if it should be dropped (builtin)."""
        root, _, rest = dotted.partition(".")
        if root in ("self", "cls") and cls:
            attr = rest.split(".")[0] if rest else ""
            found = self._lookup_class_attr(cls, attr) if attr else None
            if found:
                tail = rest.split(".", 1)[1] if "." in rest else ""
                return (f"{found}.{tail}" if tail else found), True
            return f"?{dotted}", False
        if root in locals_:
            return f"?{dotted}", False
        if root in local_bind:
            base = local_bind[root]
        elif root in mod.bindings:
            base = mod.bindings[root]
        elif root in BUILTINS:
            return None, None
        else:
            return f"?{dotted}", False
        return (f"{base}.{rest}" if rest else base), True

    def _lookup_class_attr(self, cls_sym: str, attr: str, seen=None) -> str | None:
        seen = seen or set()
        if cls_sym in seen:
            return None
        seen.add(cls_sym)
        if f"{cls_sym}.{attr}" in self._all_def_names:
            return f"{cls_sym}.{attr}"
        for b in self.class_bases.get(cls_sym, []):
            hit = self._lookup_class_attr(b, attr, seen)
            if hit:
                return hit
        return None

    # ---------- pass 2: definitions (all levels), then bodies ----------
    def collect_all_defs(self, m: _Module, tree: ast.Module):
        def walk(body, scope_sym, mod, in_function):
            for node in body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    sep = ".<locals>." if in_function else "."
                    sym = f"{scope_sym}{sep}{node.name}"
                    self.defs[sym] = _sha(node)
                    self._all_def_names.add(sym)
                    self.edge("defines", scope_sym, sym, mod, node)
                    if isinstance(node, ast.ClassDef):
                        self._class_syms.add(sym)
                        mod.class_bases.append((sym, list(node.bases), node))
                    walk(node.body, sym, mod, not isinstance(node, ast.ClassDef))
                elif not in_function and isinstance(node, (ast.Assign, ast.AnnAssign)) and scope_sym == mod.name:
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    for t in targets:
                        if isinstance(t, ast.Name):
                            sym = f"{mod.name}.{t.id}"
                            self.defs[sym] = _sha(node)
                            self._all_def_names.add(sym)
                            self.edge("defines", mod.name, sym, mod, node)
        walk(tree.body, m.name, m, False)

    def collect_bases(self):
        for m in self.modules.values():
            for sym, bases, node in m.class_bases:
                for b in bases:
                    d = _dotted(b)
                    if not d:
                        continue
                    tgt, ok = self.resolve(d, m, {}, set(), None)
                    if tgt:
                        self.class_bases.setdefault(sym, []).append(tgt)
                        self.edge("inherits", sym, tgt, m, node)
            m.class_bases = []

    def scan_bodies(self):
        """Pass 2: re-parse one file at a time for the body scan, so only one tree is alive."""
        for m in self.modules.values():
            tree = self.parse(m.path, Path(m.rel))
            self._scan_scope(m, tree.body, m.name, {}, set(), None)
            del tree

    def _scan_scope(self, mod, body, scope_sym, inherited_bind, inherited_locals, cls):
        local_bind = dict(inherited_bind)
        locals_ = set(inherited_locals)
        nested = []
        stmts = []
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                nested.append(node)
                # decorators and class bases/keywords are evaluated in this scope
                stmts.extend(node.decorator_list)
                if isinstance(node, ast.ClassDef):
                    stmts.extend(node.keywords)
                else:
                    stmts.extend([d for d in node.args.defaults + node.args.kw_defaults if d is not None])
            else:
                stmts.append(node)
        # imports and local names first (function-local imports become local bindings)
        for st in stmts:
            for n in ast.walk(st):
                if isinstance(n, (ast.Import, ast.ImportFrom)) and scope_sym != mod.name:
                    self._import_bindings(mod, n, scope_sym, local_bind)
                elif scope_sym != mod.name and isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                    locals_.add(n.id)
        for st in stmts:
            self._scan_expr(mod, st, scope_sym, local_bind, locals_, cls)
        for node in nested:
            in_cls = isinstance(node, ast.ClassDef)
            sep = "." if (scope_sym == mod.name or scope_sym in self._class_syms) else ".<locals>."
            sym = f"{scope_sym}{sep}{node.name}"
            if in_cls:
                self._scan_scope(mod, node.body, sym, local_bind, set(), sym)
            else:
                a = node.args
                params = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
                params |= {x.arg for x in (a.vararg, a.kwarg) if x}
                self._scan_scope(mod, node.body, sym, local_bind, (locals_ if scope_sym != mod.name else set()) | params,
                                 cls if cls and scope_sym == cls else None)

    def reflective(self, expr, mod, local_bind, locals_, cls):
        if isinstance(expr, ast.Call):
            d = _dotted(expr.func)
            if d:
                target, ok = self.resolve(d, mod, local_bind, locals_, cls)
                return (d == "getattr" and target is None) or target == "builtins.getattr"
            return False
        d = _dotted(expr)
        if not d:
            return False
        target, ok = self.resolve(d, mod, local_bind, locals_, cls)
        return target in {"importlib.import_module", "builtins.__import__", "builtins.eval", "builtins.exec"} or (
            target is None and d in {"__import__", "eval", "exec"})

    def _scan_expr(self, mod, st, src, local_bind, locals_, cls):
        call_funcs = set()
        for n in ast.walk(st):
            if isinstance(n, ast.Call):
                call_funcs.add(id(n.func))
                d = _dotted(n.func)
                if self.reflective(n.func, mod, local_bind, locals_, cls):
                    self.edge("calls", src, "?" + _expr_label(n.func), mod, n, "reflective")
                elif d:
                    tgt, ok = self.resolve(d, mod, local_bind, locals_, cls)
                    if tgt:
                        root = d.split(".")[0]
                        why = ("self_attr_unknown" if root in ("self", "cls") and cls else
                               "local_value" if root in locals_ else "unbound_name") if not ok else None
                        self.edge("calls", src, tgt, mod, n, why)
                else:
                    self.edge("calls", src, "?" + _expr_label(n.func), mod, n, "computed_callee")
        # references: outermost Name/Attribute loads that are not call targets
        inner = set()
        for n in ast.walk(st):
            if isinstance(n, ast.Attribute):
                inner.add(id(n.value))
        for n in ast.walk(st):
            if not isinstance(n, (ast.Name, ast.Attribute)) or id(n) in call_funcs or id(n) in inner:
                continue
            if not isinstance(getattr(n, "ctx", None), ast.Load):
                continue
            d = _dotted(n)
            if not d:
                continue
            tgt, ok = self.resolve(d, mod, local_bind, locals_, cls)
            if tgt and ok:
                self.edge("references", src, tgt, mod, n)

    def run(self):
        self.load()
        self.build_module_bindings()
        self.collect_bases()
        self.scan_bodies()
        return self


def extract(root: str | Path, method: dict) -> dict:
    root = Path(root)
    ex = _Extractor(root, set(method["ignore"]), method["source_roots"]).run()
    edges = []
    for (kind, src, dst), (file, line, why) in ex.edges.items():
        e = {"kind": kind, "src": src, "dst": dst, "resolved": not dst.startswith("?"), "file": file, "line": line}
        if kind == "calls" and not e["resolved"]:
            e["why"] = why
        if kind == "defines":
            e["body_sha"] = ex.defs.get(dst, "")
        edges.append(e)
    ex.edges = {}
    edges.sort(key=sort_key)
    header = {"aec_edges": 1, "tool_version": TOOL_VERSION, "files": len(ex.file_hashes),
              "files_sha": hashlib.sha256("\n".join(sorted(ex.file_hashes)).encode()).hexdigest()[:16],
              "skipped": sorted(ex.skipped, key=lambda s: s["file"]),
              "modules": {name: m.rel for name, m in sorted(ex.modules.items())},
              "source_roots": sorted(ex.source_roots_used),
              "classes": sorted(ex._class_syms),
              "bindings": {name: dict(sorted(m.bindings.items())) for name, m in sorted(ex.modules.items())},
              "exports": {name: m.exports for name, m in sorted(ex.modules.items()) if m.exports is not None},
              "import_modules": [{"src": src, "dst": dst, "module": module}
                                 for (src, dst), module in sorted(ex.import_modules.items())]}
    return {"header": header, "edges": edges}


def snapshot(root: str | Path, ignore: set[str] | None = None, *, rev=None, method=None, source_roots=None) -> dict:
    from .snapshots import snapshot as take_snapshot
    return take_snapshot(root, ignore, rev=rev, method=method, source_roots=source_roots)


def dumps(snap: dict) -> str:
    lines = [json.dumps(snap["header"], sort_keys=True)]
    lines += [json.dumps(e, sort_keys=True) for e in snap["edges"]]
    return "\n".join(lines) + "\n"


def loads(text: str) -> dict:
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    if not rows[0].get("method") or rows[0].get("tool_version") != TOOL_VERSION:
        rows[0]["revision_kind"] = "unknown"
    return {"header": rows[0], "edges": rows[1:]}


def load(path: str | Path) -> dict:
    return loads(Path(path).read_text(encoding="utf-8"))


def diff(old: dict, new: dict, *, allow_method_mismatch=False) -> dict:
    from .snapshots import method_differences
    fields = method_differences(old, new)
    if fields and not allow_method_mismatch:
        raise ValueError("method mismatch: " + ", ".join(fields))
    ident = lambda e: (e["kind"], e["src"], e["dst"])
    o = {ident(e): e for e in old["edges"]}
    n = {ident(e): e for e in new["edges"]}
    od = {e["dst"]: e.get("body_sha") for e in old["edges"] if e["kind"] == "defines"}
    nd = {e["dst"]: e.get("body_sha") for e in new["edges"] if e["kind"] == "defines"}
    # modules count as definitions too (a module with no functions can still be referenced and deleted);
    # snapshots from tool_version < 0.3.0 have no module map, so this adds nothing for them
    for d, snap in ((od, old), (nd, new)):
        for m in snap["header"].get("modules", {}):
            d.setdefault(m, None)
    return {
        "method_comparison": bool(fields), "method_differences": fields,
        "modules_added": sorted(set(new["header"].get("modules", {})) - set(old["header"].get("modules", {}))),
        "modules_removed": sorted(set(old["header"].get("modules", {})) - set(new["header"].get("modules", {}))),
        "added": sorted((n[k] for k in n.keys() - o.keys()), key=sort_key),
        "removed": sorted((o[k] for k in o.keys() - n.keys()), key=sort_key),
        "defs_added": sorted(nd.keys() - od.keys()),
        "defs_removed": sorted(od.keys() - nd.keys()),
        "defs_changed": sorted(s for s in od.keys() & nd.keys() if od[s] != nd[s]),
    }


def legacy_csv(snap: dict) -> str:
    rows = ["Source,Call"] + [f"{e['src']},{e['dst']}" for e in snap["edges"] if e["kind"] == "calls"]
    return "\n".join(rows) + "\n"


def render_diff(d: dict) -> str:
    out = (["METHOD COMPARISON: compares methods, not just code"] if d.get("method_comparison") else []) + ["# aec edges --diff (structural)"]
    for e in d["added"]:
        out.append(f"+ {e['kind']}: {e['src']} -> {e['dst']}  ({e['file']}:{e['line']})")
    for e in d["removed"]:
        out.append(f"- {e['kind']}: {e['src']} -> {e['dst']}  ({e['file']}:{e['line']})")
    for k in ("defs_added", "defs_removed", "defs_changed"):
        if d[k]:
            out.append(f"{k}: {', '.join(d[k])}")
    if len(out) == 1:
        out.append("no structural change")
    return "\n".join(out)
