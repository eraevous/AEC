"""Local git-addressed extraction. Never checks out, imports or executes target code."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path, PureWindowsPath

from . import edges as E

CONFIG = '.aec/extraction.json'


def git(root, *args, input=None, optional=False):
    command = ['git', '--no-pager', '--no-replace-objects', '-c', 'core.hooksPath=/dev/null',
               '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false',
               '-C', str(root), *args]
    try:
        result = subprocess.run(command, input=input, capture_output=True,
                                env={**os.environ, 'GIT_OPTIONAL_LOCKS':'0', 'GIT_NO_LAZY_FETCH':'1',
                                     'GIT_ALLOW_PROTOCOL':'', 'GIT_TERMINAL_PROMPT':'0'})
    except OSError as error:
        if optional:
            return None
        raise ValueError('local git is unavailable') from error
    if result.returncode:
        if optional:
            return None
        # Do not leak checkout/temporary absolute paths from git diagnostics.
        raise ValueError('local git operation failed: ' + args[0])
    return result.stdout


def configuration(root, ignore=None, source_roots=None):
    path = Path(root) / CONFIG
    try:
        if path.is_symlink() or not path.resolve().is_relative_to(Path(root).resolve()):
            raise ValueError('extraction config must remain within the snapshot root')
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    except (OSError, ValueError) as error:
        raise ValueError('invalid ' + CONFIG) from error
    if not isinstance(data, dict) or set(data) - {'ignore', 'source_roots'}:
        raise ValueError('extraction config accepts ignore and source_roots only')
    ignored = data.get('ignore', [])
    roots = source_roots if source_roots is not None else data.get('source_roots', 'auto')
    if not isinstance(ignored, list) or any(not isinstance(x, str) or not x for x in ignored):
        raise ValueError('ignore must be a list of relative patterns')
    ignored = sorted(E.DEFAULT_IGNORE | set(ignored) | set(ignore or []))
    if any(Path(x).is_absolute() or PureWindowsPath(x).drive or '..' in Path(x).parts or '\\' in x for x in ignored):
        raise ValueError('ignore patterns must be repo-relative')
    if roots != 'auto':
        if not isinstance(roots, list) or any(not isinstance(x, str) or not x or
                Path(x).is_absolute() or PureWindowsPath(x).drive or '..' in Path(x).parts or '\\' in x for x in roots):
            raise ValueError('source_roots must be auto or relative directories')
        roots = sorted(set(roots))
    return {'tool_version': E.TOOL_VERSION, 'ignore': ignored, 'source_roots': roots,
            'python_ast':f'{sys.version_info.major}.{sys.version_info.minor}',
            'resolution_names_sha':hashlib.sha256('\n'.join(sorted(E.BUILTINS | set(sys.stdlib_module_names))).encode()).hexdigest()}


def method_sha(method):
    return hashlib.sha256(json.dumps(method, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def materialize(root, revision, destination):
    """Read regular Python/config blobs with local git show; skip links."""
    sha = git(root, 'rev-parse', '--verify', '--end-of-options', revision + '^{commit}').decode().strip()
    prefix = git(root, 'rev-parse', '--show-prefix').decode().rstrip('\n')
    listing = git(root, 'ls-tree', '-rz', '--full-tree', sha)
    entries, skipped = [], []
    for row in listing.split(b'\0'):
        if not row:
            continue
        metadata, name = row.split(b'\t', 1)
        mode, kind, oid = metadata.decode().split()
        name = name.decode('utf-8', errors='surrogateescape')
        if prefix and not name.startswith(prefix):
            continue
        name = name[len(prefix):]
        if mode == '160000':
            skipped.append({'file':name, 'reason':'gitlink tree not expanded'})
            continue
        if name != CONFIG and not name.endswith('.py'):
            continue
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('unsafe path in git tree')
        if mode not in ('100644', '100755') or kind != 'blob':
            if name.endswith('.py'):
                skipped.append({'file': name, 'reason': 'non-regular git entry not parsed'})
            continue
        entries.append((name, oid))
    for name, oid in entries:
        body = git(root, 'show', '--no-ext-diff', '--no-textconv', '--no-color', oid)
        path = Path(destination) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    return sha, prefix or '.', skipped


def working_state(root, head, seen=None):
    """Compare raw Git blobs/index/files without status, filters, hooks or refresh."""
    seen = set() if seen is None else seen
    resolved_root = Path(root).resolve()
    if resolved_root in seen:
        return True, '.'
    seen.add(resolved_root)
    prefix = git(root, 'rev-parse', '--show-prefix').decode().rstrip('\n')
    committed = {}
    for row in git(root, 'ls-tree', '-rz', '--full-tree', head).split(b'\0'):
        if not row:
            continue
        metadata, name = row.split(b'\t', 1)
        name = os.fsdecode(name)
        if prefix and not name.startswith(prefix):
            continue
        mode, kind, oid = metadata.decode().split()
        committed[name[len(prefix):]] = (mode, oid)
    indexed = {}
    for row in git(root, 'ls-files', '--stage', '-z', '--', '.').split(b'\0'):
        if not row:
            continue
        metadata, name = row.split(b'\t', 1)
        mode, oid, stage = metadata.decode().split()
        if stage != '0':
            return True, prefix or '.'
        indexed[os.fsdecode(name)] = (mode, oid)
    if indexed != committed or git(root, 'ls-files', '--others', '--exclude-standard', '-z', '--', '.'):
        return True, prefix or '.'
    algorithm = git(root, 'rev-parse', '--show-object-format').decode().strip()
    base = Path(root).resolve()
    for name, (mode, oid) in committed.items():
        path = base / name
        try:
            if mode == '120000':
                if not path.is_symlink():
                    return True, prefix or '.'
                raw = os.fsencode(os.readlink(path))
            elif mode == '160000':
                if path.is_symlink() or not path.resolve().is_relative_to(base):
                    return True, prefix or '.'
                # An uninitialized submodule contributes no checked-out source.
                if not path.exists() or not any(path.iterdir()):
                    continue
                sub_head = git(path, 'rev-parse', '--verify', 'HEAD', optional=True)
                if sub_head is None or sub_head.decode().strip() != oid or working_state(path, oid, seen)[0]:
                    return True, prefix or '.'
                continue
            else:
                if path.is_symlink() or not path.resolve().is_relative_to(base) or not path.is_file():
                    return True, prefix or '.'
                raw = path.read_bytes()
                if os.name != 'nt' and bool(path.stat().st_mode & 0o111) != (mode == '100755'):
                    return True, prefix or '.'
            digest = hashlib.new(algorithm, b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            if digest != oid:
                return True, prefix or '.'
        except (OSError, RuntimeError):
            return True, prefix or '.'
    return False, prefix or '.'


def snapshot(root, ignore=None, *, rev=None, method=None, source_roots=None):
    root = Path(root)
    if not root.is_dir():
        raise ValueError('snapshot root is not a directory')
    if rev is not None:
        with tempfile.TemporaryDirectory(prefix='aec-snapshot-') as directory:
            sha, scope, skipped = materialize(root, rev, directory)
            chosen = method or configuration(directory, ignore, source_roots)
            snap = E.extract(directory, chosen)
            ignored = chosen['ignore']
            snap['header']['skipped'].extend(s for s in skipped if not E.ignored(Path(s['file']), ignored))
            snap['header']['skipped'].sort(key=lambda s: s['file'])
            snap['header'].update(revision=sha, revision_kind='commit', scope=scope)
    else:
        chosen = method or configuration(root, ignore, source_roots)
        snap = E.extract(root, chosen)
        head = git(root, 'rev-parse', '--verify', 'HEAD', optional=True)
        dirty, scope = working_state(root, head.decode().strip()) if head else (True, '.')
        snap['header'].update(revision_kind='working-tree', base_revision=head.decode().strip() if head else None,
                              dirty=dirty, scope=scope)
    snap['header']['method'] = chosen
    snap['header']['method_sha'] = method_sha(chosen)
    return snap


def method_differences(old, new):
    a, b = old['header'].get('method'), new['header'].get('method')
    if not isinstance(a, dict) or not isinstance(b, dict):
        return ['legacy/unknown method']
    fields = sorted(key for key in a.keys() | b.keys() if a.get(key) != b.get(key))
    if any(s['header'].get('tool_version') != E.TOOL_VERSION or s['header'].get('revision_kind') == 'unknown'
           for s in (old,new)):
        fields.append('legacy/unknown method')
    if any(s['header'].get('tool_version') != s['header']['method'].get('tool_version') for s in (old,new)):
        fields.append('tool_version')
    if old['header'].get('method_sha') != method_sha(a) or new['header'].get('method_sha') != method_sha(b):
        fields.append('method_sha')
    return fields


def annotate_edge(snapshot, edge):
    from .graph import canonical_symbol, module_of, symbol_file
    result = edge.copy()
    src_file, dst_file = symbol_file(snapshot, edge['src']), symbol_file(snapshot, edge['dst'])
    result['cross_module'] = src_file != dst_file if src_file and dst_file else None
    result['cross_class'] = False
    result['crosses_public_surface'] = False
    if result['cross_module']:
        source, target = Path(src_file).parent.parts, Path(dst_file).parent.parts
        common = []
        for a, b in zip(source, target):
            if a != b:
                break
            common.append(a)
        result['boundary'] = {'directory': '/'.join(common) or '.',
                              'src_depth':len(source)-len(common), 'dst_depth':len(target)-len(common)}
        module = module_of(snapshot, edge['dst'])
        exported = snapshot['header'].get('exports', {}).get(module)
        suffix = canonical_symbol(snapshot, edge['dst'])[len(module):].lstrip('.')
        if exported is not None and suffix:
            result['crosses_public_surface'] = suffix.split('.')[0] not in exported
    elif src_file and src_file == dst_file:
        classes = snapshot['header'].get('classes', [])
        def owner(symbol):
            return next((c for c in sorted(classes, key=lambda n:(-len(n),n)) if symbol==c or symbol.startswith(c+'.')),None)
        a, b = owner(canonical_symbol(snapshot, edge['src'])), owner(canonical_symbol(snapshot, edge['dst']))
        result['cross_class'] = bool(a and b and a != b)
    return result


def structural_diff(old, new, *, allow_method_mismatch=False):
    from .graph import WHY, visibility
    report = E.diff(old, new, allow_method_mismatch=allow_method_mismatch)
    report['label'] = 'structural'
    report['comparison'] = 'methods, not just code' if report['method_comparison'] else 'code with one method'
    for change, snap in [('added', new), ('removed', old)]:
        report[change] = [annotate_edge(snap, e) for e in report[change]]
    report['edges_by_kind'] = {kind:{change:[e for e in report[change] if e['kind']==kind]
                                   for change in ('added','removed')} for kind in E.KINDS}
    report['cross_module_changes'] = {change:[e for e in report[change] if e['kind'] in ('imports','calls') and e['cross_module']]
                                      for change in ('added','removed')}
    report['within_module_changes'] = {change:[e for e in report[change] if e['kind'] in ('imports','calls') and e['cross_module'] is False]
                                       for change in ('added','removed')}
    report['unresolved_changes'] = {change:{why:[e for e in report[change] if e['kind']=='calls' and not e['resolved'] and e.get('why')==why]
                                                   for why in WHY} for change in ('added','removed')}
    touched = {e['src'] for change in ('added','removed') for e in report[change]} | set(report['defs_changed'])
    report['visibility'] = {side:{projection:visibility(snap,projection,region=touched)
                                for projection in ('calls','imports','inherits')}
                            for side,snap in [('base',old),('head',new)]}
    return report


def compare_revisions(root, *, base='origin/main', head='HEAD'):
    head_sha = git(root,'rev-parse','--verify','--end-of-options',head+'^{commit}').decode().strip()
    base_sha = git(root,'rev-parse','--verify','--end-of-options',base+'^{commit}').decode().strip()
    common = git(root,'merge-base',base_sha,head_sha).decode().strip()
    # Read effective configurations independently, then use head's method on BOTH sides.
    with tempfile.TemporaryDirectory(prefix='aec-method-') as head_dir, tempfile.TemporaryDirectory(prefix='aec-method-') as base_dir:
        materialize(root,head_sha,head_dir)
        materialize(root,common,base_dir)
        method, prior = configuration(head_dir), configuration(base_dir)
    old, new = E.snapshot(root,rev=common,method=method), E.snapshot(root,rev=head_sha,method=method)
    report = structural_diff(old,new)
    report.update(base_revision=common, requested_base_revision=base_sha, head_revision=head_sha,
                  base_method_sha=old['header']['method_sha'], head_method_sha=new['header']['method_sha'])
    changed = sorted(key for key in prior if prior[key] != method[key])
    report['method_change'] = {'message':'method change in this PR', 'fields':changed,
                               'before':prior,'after':method} if changed else None
    return report
