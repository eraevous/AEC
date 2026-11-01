"""Per-projection structural queries; unknown targets are never guessed."""
from __future__ import annotations

WHY = ('local_value', 'self_attr_unknown', 'unbound_name', 'computed_callee', 'reflective')
CAVEAT = 'Known structural reachability is not runtime impact; an unresolved or dynamic call is invisible here.'


def canonical_symbol(snapshot, symbol, seen=None, origin=None):
    """Follow only explicit module-level AST import/re-export bindings, never values."""
    seen = set() if seen is None else seen
    origin = symbol if origin is None else origin
    if symbol in seen:
        return origin
    seen.add(symbol)
    modules = snapshot['header'].get('modules', {})
    defined = {e['dst'] for e in snapshot['edges'] if e['kind']=='defines'}
    if symbol in modules or symbol in defined:
        return symbol
    for module in sorted(modules, key=lambda n:(-len(n),n)):
        if not symbol.startswith(module + '.'):
            continue
        suffix = symbol[len(module)+1:]
        name, sep, tail = suffix.partition('.')
        target = snapshot['header'].get('bindings', {}).get(module, {}).get(name)
        if target and target != module + '.' + name:
            binding = (module, name)
            if binding in seen:
                return origin
            seen.add(binding)
            return canonical_symbol(snapshot, target + (sep+tail if sep else ''), seen, origin)
    return symbol


def module_of(snapshot, symbol):
    symbol = canonical_symbol(snapshot, symbol)
    modules = snapshot['header'].get('modules', {})
    if symbol in modules:
        return symbol
    file = next((e['file'] for e in snapshot['edges'] if e['kind']=='defines' and e['dst']==symbol),None)
    return next((module for module, path in modules.items() if path==file),None)


def symbol_file(snapshot, symbol):
    module = module_of(snapshot, symbol)
    return snapshot['header'].get('modules', {}).get(module)


def unresolved(snapshot, *, why=None, scope=None):
    if why and set(why) - set(WHY):
        raise ValueError('unknown unresolved reason')
    rows = [e.copy() for e in snapshot['edges'] if e['kind']=='calls' and not e['resolved']
            and (not why or e.get('why') in why)
            and (not scope or e['file']==scope or e['file'].startswith(scope.rstrip('/')+'/')
                 or e['src']==scope or e['src'].startswith(scope+'.'))]
    return sorted(rows, key=lambda e:(e['file'], e['line'], e['src'], e['dst'], e.get('why','')))


def visibility(snapshot, projection, region=None):
    selected = [e for e in snapshot['edges'] if e['kind']==projection]
    files = None if region is None else {symbol_file(snapshot, symbol) for symbol in region}
    def counts(rows):
        reasons = {why:sum(not e['resolved'] and e.get('why')==why for e in rows) for why in WHY}
        return {'resolved':sum(bool(e['resolved']) for e in rows), 'total':len(rows),
                'unresolved_by_why':reasons,
                'external':sum(e['kind']=='calls' and e['resolved'] and symbol_file(snapshot,e['dst']) is None for e in rows)}
    regional = selected if files is None else [e for e in selected if e['src'] in region or e['dst'] in region
        or e['file'] in files or symbol_file(snapshot,e['dst']) in files-{None}]
    return {'projection':counts(selected), 'region':counts(regional),
            'region_scope':'files containing known region nodes',
            'skipped':snapshot['header'].get('skipped',[])}


NODE_TYPES = {'calls':'functions/classes (module bodies and external labels where present)',
              'imports':'modules', 'inherits':'classes'}


def projection_edges(snapshot, projection):
    if projection not in NODE_TYPES:
        raise ValueError('unknown graph projection')
    imported = {(e['src'],e['dst']):e['module'] for e in snapshot['header'].get('import_modules',[])}
    arcs = set()
    for edge in snapshot['edges']:
        if edge['kind'] != projection or not edge['resolved']:
            continue
        src, dst = edge['src'], edge['dst']
        if projection == 'imports':
            src = module_of(snapshot, src) or src
            dst = imported.get((edge['src'],edge['dst'])) or module_of(snapshot, dst) or dst.removesuffix('.*')
        else:
            src, dst = canonical_symbol(snapshot, src), canonical_symbol(snapshot, dst)
        arcs.add((src,dst))
    return sorted(arcs)


def reach(snapshot, symbol, *, direction='callers', projection='calls', depth=1):
    if direction not in ('callers','callees') or depth < 0:
        raise ValueError('direction must be callers/callees and depth nonnegative')
    arcs = projection_edges(snapshot,projection)
    requested = symbol
    if projection != 'imports':
        symbol = canonical_symbol(snapshot, symbol)
    known = set(snapshot['header'].get('modules',{})) | {e['dst'] for e in snapshot['edges'] if e['kind']=='defines'}
    endpoints = {n for edge in arcs for n in edge}
    if symbol not in known | endpoints:
        raise ValueError('symbol is not present in the snapshot')
    adjacency = {}
    for src,dst in arcs:
        a,b = (dst,src) if direction=='callers' else (src,dst)
        adjacency.setdefault(a,set()).add(b)
    seen, frontier = {symbol}, {symbol}
    for _ in range(depth):
        frontier = {n for current in frontier for n in adjacency.get(current,set())} - seen
        if not frontier:
            break
        seen |= frontier
    return {'label':'structural', 'symbol':requested, 'canonical_symbol':symbol, 'projection':projection, 'direction':direction,
            'depth':depth, 'node_type':NODE_TYPES[projection], 'origin_in_projection':symbol in endpoints,
            'reachable':sorted(seen-{symbol}), 'visibility':visibility(snapshot,projection,seen), 'caveat':CAVEAT}


def fan(snapshot, *, projection='calls', top=20):
    if projection not in ('calls','imports') or top < 0:
        raise ValueError('fan projection must be calls/imports and top nonnegative')
    incoming, outgoing = {}, {}
    for src,dst in projection_edges(snapshot,projection):
        outgoing.setdefault(src,set()).add(dst)
        incoming.setdefault(dst,set()).add(src)
    nodes = [{'symbol':symbol,'fan_in':len(incoming.get(symbol,set())), 'fan_out':len(outgoing.get(symbol,set()))}
             for symbol in sorted(incoming.keys() | outgoing.keys())]
    nodes.sort(key=lambda row:(-(row['fan_in']+row['fan_out']),row['symbol']))
    return {'label':'structural','projection':projection,'node_type':NODE_TYPES[projection],
            'degree_unit':'distinct neighbors','nodes':nodes[:top], 'omitted':max(0,len(nodes)-top),
            'visibility':visibility(snapshot,projection), 'caveat':CAVEAT}


def render_query(report):
    import json
    return '# aec graph (structural)\n' + json.dumps(report,sort_keys=True,indent=2) + '\n' + CAVEAT
