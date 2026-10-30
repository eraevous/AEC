"""Offline source integrity and retrieval (WP-S); never semantic attestation.

Sources are read in place. Only metadata/observations are retained in memory;
no source files, derived index, or persistent cache are written.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

OUTPUT_TEMPLATES = {
    'heading': '# aec source {mode} (structural)',
    'status': 'record-directed {ref} anchor[{index}] for={field} state={state} source={path} locator={locator}',
    'warning': 'WARNING: {detail}',
    'verified': 'artifact bytes and locator match',
    'missing': 'source file not found in an available root; no inference about earlier existence',
    'mismatch': 'file bytes changed; the earlier observation is not falsified; applicability needs review',
    'locator_invalid': 'locator does not resolve in the matching artifact',
    'unavailable': "source can't be checked here; root or file is unavailable or outside the read boundary",
    'no_passage': 'No resolved passage to display.',
    'truncated': '[truncated: {count} line(s) omitted; max-lines={limit}]',
    'hit': 'fallback root={root} path={path} line={line} sha256={sha256} records={records}: {text}',
    'chars_omitted': '…[+{count} chars]',
    'tiny_excerpt': '…',
    'summary': '{shown} hit(s) shown; limit={limit}; {omitted} hit(s) omitted; {total} matching line(s).',
}


def anchor_errors(anchor) -> list[str]:
    if not isinstance(anchor, dict):
        return ['anchor must be an object']
    errors = []
    path = anchor.get('path')
    if (not isinstance(path, str) or not path or '\x00' in path or '\n' in path or '\r' in path
            or Path(path).is_absolute() or PureWindowsPath(path).root or PureWindowsPath(path).drive
            or '..' in Path(path).parts or '..' in PureWindowsPath(path).parts or '://' in path):
        errors.append('path must be a nonempty relative file path without parent traversal')
    root = anchor.get('root')
    if 'root' in anchor and (not isinstance(root, str) or not root or any(c in root for c in '\x00\r\n')):
        errors.append('root must be a nonempty alias string')
    sha = anchor.get('sha256')
    if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', sha):
        errors.append('sha256 must be 64 hexadecimal characters')
    if anchor.get('for', 'text') not in ('text', 'rationale'):
        errors.append('for must be text or rationale')
    if parse_locator(anchor.get('locator')) is None:
        errors.append('locator must be L<n>, L<start>-<end>, or q:<nonempty single-line text>')
    return errors


def parse_locator(locator):
    if not isinstance(locator, str):
        return None
    match = re.fullmatch(r'L([1-9][0-9]*)(?:-([1-9][0-9]*))?', locator)
    if match:
        start, end = int(match[1]), int(match[2] or match[1])
        return ('lines', start, end) if end >= start else None
    if locator.startswith('q:') and len(locator) > 2 and not any(c in locator for c in '\r\n\v\f\x1c\x1d\x1e\x85\u2028\u2029'):
        return ('quote', locator[2:])
    return None


def locate(locator, lines):
    parsed = parse_locator(locator)
    if parsed is None:
        return None
    if parsed[0] == 'lines':
        return (parsed[1], parsed[2]) if parsed[2] <= len(lines) else None
    return next(((i, i) for i, line in enumerate(lines, 1) if parsed[1] in line), None)


@dataclass(frozen=True)
class SourceRoot:
    name: str
    base: Path
    display: str

    def label(self, path):
        return (Path(self.display) / path).as_posix()


@dataclass(frozen=True)
class Inspection:
    ref: str
    index: int
    field: str
    path: str
    locator: str
    state: str | None
    detail: str
    lines: tuple[str, ...] = ()
    span: tuple[int, int] | None = None
    errors: tuple[str, ...] = ()


def render_status(item: Inspection) -> str:
    return OUTPUT_TEMPLATES['status'].format(ref=item.ref, index=item.index, field=item.field,
        state=item.state or 'malformed', path=json.dumps(item.path, ensure_ascii=False),
        locator=json.dumps(item.locator, ensure_ascii=False))


class SourceContext:
    def __init__(self, repo):
        self.repo = Path(repo).absolute()
        self._roots = None
        self._inspections = {}

    @property
    def roots(self) -> dict[str, SourceRoot]:
        if self._roots is None:
            config = self.repo / '.aec/sources.json'
            try:
                data = json.loads(config.read_text(encoding='utf-8')) if config.exists() else {'roots': {}}
            except (OSError, ValueError) as error:
                raise ValueError('cannot read .aec/sources.json: ' + str(error)) from error
            if not isinstance(data, dict) or not isinstance(data.get('roots'), dict):
                raise ValueError('.aec/sources.json must contain a roots object')
            roots = {}
            for name, path in sorted(data['roots'].items()):
                if (not isinstance(name, str) or not name or name == '.' or any(c in name for c in '\x00\r\n')
                        or not isinstance(path, str) or not path or any(c in path for c in '\x00\r\n')
                        or '://' in path or path.startswith(('//', '\\\\'))):
                    raise ValueError('source roots must map aliases (other than .) to local paths')
                roots[name] = SourceRoot(name, self.repo / path, Path(path).as_posix())
            self._roots = roots
        return self._roots

    def root(self, name=None):
        if name is None or name == '.':
            return SourceRoot('.', self.repo, '.')
        return self.roots.get(name)

    def read(self, root: SourceRoot | None, path: str):
        if root is None:
            return 'unavailable', None
        try:
            base = root.base.resolve()
            if not base.is_dir():
                return 'unavailable', None
            target = (base / path).resolve()
            if not target.is_relative_to(base):
                return 'unavailable', None
            if not target.is_file():
                return 'missing', None
            return None, target.read_bytes()
        except (OSError, RuntimeError, ValueError):
            return 'unavailable', None

    def inspect_record(self, record) -> list[Inspection]:
        key = id(record)
        if key not in self._inspections:
            anchors = record.get('anchors', [])
            if not isinstance(anchors, list):
                result = [Inspection(record.ref, 0, 'text', '', '', None, '', errors=('anchors must be an array',))]
            else:
                result = [self.inspect(anchor, record.ref, index) for index, anchor in enumerate(anchors)]
            self._inspections[key] = result
        return self._inspections[key]

    def inspect(self, anchor, ref, index) -> Inspection:
        errors = anchor_errors(anchor)
        if errors:
            return Inspection(ref, index, 'text', '', '', None, '', errors=tuple(errors))
        root = self.root(anchor.get('root'))
        path = root.label(anchor['path']) if root else anchor['path']
        state, raw = self.read(root, anchor['path'])
        lines, span = (), None
        if raw is not None:
            lines = tuple(raw.decode('utf-8', errors='replace').splitlines())
            span = locate(anchor['locator'], lines)
            state = ('mismatch' if hashlib.sha256(raw).hexdigest() != anchor['sha256'].lower()
                     else 'locator_invalid' if span is None else 'verified')
        return Inspection(ref, index, anchor.get('for', 'text'), path, anchor['locator'], state,
                          OUTPUT_TEMPLATES[state], lines, span)


def record_findings(record, context: SourceContext):
    from .records import Finding
    out = []
    for item in context.inspect_record(record):
        for error in item.errors:
            out.append(Finding('error', 'anchor-shape', record.ref, f'anchor[{item.index}]: {error}'))
        if item.state not in (None, 'verified'):
            out.append(Finding('warning', 'anchor-' + item.state, record.ref,
                               render_status(item) + ': ' + item.detail))
    return out


def render_show(store, ref, sources: SourceContext, *, context=3, max_lines=80) -> str:
    if context < 0 or max_lines < 1:
        raise ValueError('context must be nonnegative and max-lines positive')
    record = store.by_ref.get(ref)
    if record is None:
        raise ValueError('record reference not found: ' + ref)
    out = [OUTPUT_TEMPLATES['heading'].format(mode='show')]
    items = sources.inspect_record(record)
    if not items:
        out.append(f'record-directed {ref}: no anchors.')
    for item in items:
        if item.errors:
            raise ValueError(f'{ref} anchor[{item.index}]: ' + '; '.join(item.errors))
        out.append(render_status(item))
        if item.state != 'verified':
            out.append(OUTPUT_TEMPLATES['warning'].format(detail=item.detail))
        if item.state in ('missing', 'unavailable'):
            continue
        if item.span is None:
            out.append(OUTPUT_TEMPLATES['no_passage'])
            continue
        start, end = max(1, item.span[0] - context), min(len(item.lines), item.span[1] + context)
        stop = min(end, start + max_lines - 1)
        out.extend(f'{number} | {item.lines[number - 1]}' for number in range(start, stop + 1))
        if stop < end:
            out.append(OUTPUT_TEMPLATES['truncated'].format(count=end - stop, limit=max_lines))
    return '\n'.join(out) + '\n'


def anchored_files(store, sources: SourceContext) -> dict[Path, list[str]]:
    """Associate files with recorded anchors, irrespective of pinned digest freshness."""
    refs = {}
    for record in store.records:
        anchors = record.get('anchors', [])
        if not isinstance(anchors, list):
            continue
        for anchor in anchors:
            if anchor_errors(anchor):
                continue
            root = sources.root(anchor.get('root'))
            if root is None:
                continue
            try:
                base = root.base.resolve()
                path = (base / anchor['path']).resolve()
                if path.is_relative_to(base):
                    refs.setdefault(path, set()).add(record.ref)
            except (OSError, RuntimeError, ValueError):
                continue
    return {path: sorted(values) for path, values in refs.items()}


def search_excerpt(line: str, match_start: int, match_end: int, max_chars: int) -> str:
    """Bound the rendered hit text, including omission markers, around its first match."""
    if len(line) <= max_chars:
        return line
    width = max_chars
    while width > 0:
        padding = max(0, width - (match_end - match_start)) // 2
        start = max(0, match_start - padding)
        end = min(len(line), start + width)
        start = max(0, end - width)
        prefix = OUTPUT_TEMPLATES['chars_omitted'].format(count=start) if start else ''
        suffix = OUTPUT_TEMPLATES['chars_omitted'].format(count=len(line)-end) if end < len(line) else ''
        overflow = end - start + len(prefix) + len(suffix) - max_chars
        if overflow <= 0:
            return prefix + line[start:end] + suffix
        width -= overflow
    # A tiny explicit limit cannot fit a useful window and detailed count markers.
    return OUTPUT_TEMPLATES['tiny_excerpt']


def render_search(store, pattern: str, sources: SourceContext, *, root=None, regex=False,
                  max_hits=20, max_chars=240) -> str:
    if max_hits < 0:
        raise ValueError('max must be nonnegative')
    if max_chars < 1:
        raise ValueError('max-chars must be positive')
    try:
        compiled = re.compile(pattern) if regex else None
    except re.error as error:
        raise ValueError('invalid regex: ' + str(error)) from error
    if root is None:
        roots = list(sources.roots.values())
    else:
        chosen = sources.root(root)
        if chosen is None:
            raise ValueError('root is not configured: ' + root)
        roots = [chosen]
    refs = anchored_files(store, sources)
    hits, notes = [], []
    for selected in roots:
        try:
            base = selected.base.resolve()
            if not base.is_dir():
                raise OSError('root is not an available directory')
        except (OSError, RuntimeError):
            notes.append(f'unavailable root={json.dumps(selected.name)} path={json.dumps(selected.display)}')
            continue
        def walk_error(error):
            notes.append(f'unavailable traversal in root={json.dumps(selected.name)}')
        for directory, dirs, files in os.walk(base, followlinks=False, onerror=walk_error):
            dirs[:] = sorted(d for d in dirs if not (Path(directory) / d).is_symlink())
            for filename in sorted(files):
                relative = (Path(directory) / filename).relative_to(base).as_posix()
                state, raw = sources.read(selected, relative)
                display = selected.label(relative)
                if raw is None:
                    notes.append(f'{state} root={json.dumps(selected.name)} path={json.dumps(display)} (not read)')
                    continue
                sha = hashlib.sha256(raw).hexdigest()
                path = (base / relative).resolve()
                linked = refs.get(path, [])
                for number, line in enumerate(raw.decode('utf-8', errors='replace').splitlines(), 1):
                    if compiled is not None:
                        match = compiled.search(line)
                        span = match.span() if match else None
                    else:
                        position = line.find(pattern)
                        span = (position, position + len(pattern)) if position >= 0 else None
                    if span is not None:
                        excerpt = search_excerpt(line, span[0], span[1], max_chars)
                        hits.append((display, number, selected.name, sha, linked, excerpt))
    hits.sort(key=lambda hit: (hit[0], hit[1], hit[2]))
    shown = hits[:max_hits]
    out = [OUTPUT_TEMPLATES['heading'].format(mode='search')]
    if not roots:
        out.append('No named source roots configured.')
    out.extend(OUTPUT_TEMPLATES['warning'].format(detail=note) for note in sorted(set(notes)))
    out.extend(OUTPUT_TEMPLATES['hit'].format(root=json.dumps(name, ensure_ascii=False),
        path=json.dumps(path, ensure_ascii=False), line=line, sha256=sha,
        records=json.dumps(linked, ensure_ascii=False), text=text)
        for path, line, name, sha, linked, text in shown)
    out.append(OUTPUT_TEMPLATES['summary'].format(shown=len(shown), limit=max_hits,
                                                omitted=len(hits)-len(shown), total=len(hits)))
    return '\n'.join(out) + '\n'
