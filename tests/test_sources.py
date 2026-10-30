"""WP-S frozen cases, violation/decoy checks; synthetic sources exist only in temp dirs."""
import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from aec.__main__ import main
from aec.records import Record, Store, TYPES, check
from aec.sources import SourceContext

VALID = b'first\nshared needle\nthird\nshared needle\nlast\n'


class SourceFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repo'
        self.corpus = self.base / 'corpus'
        (self.repo / '.aec').mkdir(parents=True)
        self.corpus.mkdir()
        (self.corpus / 'valid.txt').write_bytes(VALID)
        (self.corpus / 'changed.txt').write_bytes(VALID+b'added\n')
        (self.corpus / 'unindexed.txt').write_text('previously unrecorded fact\nshared needle\n')
        (self.repo / '.aec/sources.json').write_text(json.dumps({'roots': {'corpus': '../corpus', 'absent': '../absent'}}))
        self.cases = json.loads((ROOT / 'tests/fixtures/anchors/cases.json').read_text())
        self.records = self.repo / '.aec/records.jsonl'
        self.records.write_text('')

    def anchor(self, **changes):
        return {'root': 'corpus', 'path': 'valid.txt', 'sha256': hashlib.sha256(VALID).hexdigest(),
                'locator': 'L2-3', **changes}

    def record(self, anchors=None, **data):
        return Record('C', 1, 'claim', text='A conclusion', data={'anchors': [self.anchor()] if anchors is None else anchors, **data})

    def findings(self, rec):
        return check(Store([rec]), sources=SourceContext(self.repo))

    def save(self, records):
        rows = [dict(id=r.id, version=r.version, type=r.type, text=r.text, **r.data) for r in records]
        self.records.write_text(''.join(json.dumps(r)+'\n' for r in rows))

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                result = main(list(args))
            except SystemExit as e:
                result = e.code
        return result, out.getvalue(), err.getvalue()


class TestAnchorChecks(SourceFixture):
    def test_frozen_cases_and_clean_decoy(self):
        for case in self.cases:
            with self.subTest(case=case['id']):
                anchor = {k: v for k, v in case.items() if k not in {'id', 'expected'}}
                anchor.setdefault('root', 'corpus')
                r = self.record([anchor])
                ctx = SourceContext(self.repo)
                inspections = ctx.inspect_record(r)
                fs = check(Store([r]), sources=ctx)
                if case['expected'] == 'error':
                    self.assertIsNone(inspections[0].state)
                    self.assertEqual([f.level for f in fs], ['error'])
                else:
                    self.assertEqual(inspections[0].state, case['expected'])
                    self.assertEqual([f.level for f in fs], [] if case['expected']=='verified' else ['warning'])

    def test_shape_violations_with_valid_anchor_decoy(self):
        for field, value in [('sha256', 'a'*63), ('sha256', 'g'*64), ('for', 'authority'),
                             ('locator','L0'), ('locator','L3-2'), ('locator','q:'), ('locator','q:a\nb'),
                             ('path','../secret'), ('path','/etc/passwd'), ('root', 12)]:
            with self.subTest(field=field,value=value):
                fs = self.findings(self.record([self.anchor(**{field:value})]))
                self.assertTrue(fs)
                self.assertTrue(all(f.level=='error' for f in fs))
        self.assertEqual(self.findings(self.record()), [])
        for anchors in [None, {}, 'not an array', [None]]:
            rec = Record('C',1,'claim',data={'anchors': anchors})
            self.assertTrue(any(f.level=='error' for f in self.findings(rec)))
        self.assertEqual(self.findings(self.record([])), [])

    def test_rationale_and_all_record_types_preserve_text(self):
        for kind in sorted(TYPES):
            rec = self.record([self.anchor(**{'for':'rationale'})], rationale='Separate reason')
            rec.type = kind
            self.assertEqual([f for f in self.findings(rec) if f.rule.startswith('anchor')], [])
            self.assertEqual(rec.text, 'A conclusion')
            self.assertEqual(rec.get('rationale'), 'Separate reason')
        self.assertTrue(any(f.level=='error' for f in self.findings(self.record(rationale=[]))))
        legacy = Record('legacy',1,'claim',text='No anchors')
        self.assertEqual(self.findings(legacy), [])
        self.save([self.record(rationale='Separate reason')])
        reloaded = Store.load(self.records).latest['C']
        self.assertEqual((reloaded.text,reloaded.get('rationale')),('A conclusion','Separate reason'))

    def test_raw_bytes_hash_and_default_repo_root(self):
        data = b'one\r\ntwo\r\n'
        (self.repo / 'local.txt').write_bytes(data)
        a = self.anchor(path='local.txt', sha256=hashlib.sha256(data).hexdigest(), locator='L2')
        del a['root']
        self.assertEqual(self.findings(self.record([a])), [])
        a['sha256'] = hashlib.sha256(data.replace(b'\r\n',b'\n')).hexdigest()
        fs=self.findings(self.record([a]))
        self.assertEqual(fs[0].rule,'anchor-mismatch')
        self.assertIn('not falsified',fs[0].msg)
        self.assertIn('applicability',fs[0].msg)

    def test_unavailable_is_distinct_from_missing_and_external_symlink(self):
        (self.corpus / 'outside').symlink_to(self.repo / '.aec/records.jsonl')
        fs=self.findings(self.record([self.anchor(path='outside')]))
        self.assertEqual(fs[0].rule,'anchor-unavailable')
        fs=self.findings(self.record([self.anchor(root='absent')]))
        self.assertEqual(fs[0].rule,'anchor-unavailable')
        self.assertIn("can't be checked here",fs[0].msg)
        self.assertNotIn('source is gone',fs[0].msg)

    def test_check_cli_findings_exit_zero_errors_fail_and_repeat_identically(self):
        for case in self.cases:
            a={k:v for k,v in case.items() if k not in {'id','expected'}}
            a.setdefault('root','corpus')
            self.save([self.record([a])])
            result=self.cli('check',str(self.records))
            self.assertEqual(result,self.cli('check',str(self.records)))
            self.assertEqual(result[0],1 if case['expected']=='error' else 0)
            if case['expected']!='error':self.assertIn(case['expected'],result[1])
        self.save([Record('bad',1,'unknown',data={'anchors':[self.anchor(path='missing')]})])
        self.assertEqual(self.cli('check',str(self.records))[0],1)


class TestSourceShow(SourceFixture):
    def show(self, anchor=None, **kw):
        from aec.sources import render_show
        return render_show(Store([self.record([anchor or self.anchor()])]), 'C@1', SourceContext(self.repo), **kw)

    def numbered(self, output):
        import re
        return [(int(m[1]),m[2]) for line in output.splitlines() if (m:=re.fullmatch(r'(\d+) \| (.*)',line))]

    def test_exact_inclusive_range_context_and_quote_first_match(self):
        self.assertEqual(self.numbered(self.show(context=0)),[(2,'shared needle'),(3,'third')])
        self.assertEqual([n for n,_ in self.numbered(self.show(context=1))],[1,2,3,4])
        self.assertEqual(self.numbered(self.show(self.anchor(locator='q:shared needle'),context=0)),[(2,'shared needle')])
        self.assertIn('for=rationale',self.show(self.anchor(**{'for':'rationale'})))
        self.assertIn('record-directed C@1 anchor[0]',self.show())

    def test_bound_and_warnings_without_substitute_passage(self):
        out=self.show(self.anchor(locator='L1-5'),context=3,max_lines=2)
        self.assertEqual(len(self.numbered(out)),2)
        self.assertIn('truncated: 3 line(s) omitted',out)
        out=self.show(self.anchor(path='changed.txt'),context=0)
        self.assertIn('WARNING:',out)
        self.assertIn('state=mismatch',out)
        self.assertTrue(self.numbered(out))
        for a in [self.anchor(path='missing'),self.anchor(root='absent'),self.anchor(locator='L99')]:
            out=self.show(a)
            self.assertIn('WARNING:',out)
            self.assertEqual(self.numbered(out),[])
        self.assertNotIn('WARNING:',self.show())

    def test_show_cli_repeat_limits_unknown_ref_and_alternate_records(self):
        self.save([self.record()])
        args=('source','show','C@1','--repo',str(self.repo),'--context','0','--max-lines','1')
        first=self.cli(*args)
        self.assertEqual(first,self.cli(*args))
        self.assertEqual(first[0],0)
        self.assertEqual(len(self.numbered(first[1])),1)
        self.assertIn('truncated',first[1])
        self.assertEqual(self.cli('source','show','missing@1','--repo',str(self.repo))[0],2)
        self.assertEqual(self.cli(*args,'--context','-1')[0],2)
        self.assertEqual(self.cli(*args,'--max-lines','0')[0],2)
        other=self.repo/'other.jsonl'
        other.write_bytes(self.records.read_bytes())
        self.records.unlink()
        self.assertEqual(self.cli(*args,'--records',str(other))[0],0)


class TestSourceSearch(SourceFixture):
    def search(self, pattern, *, store=None, **kw):
        from aec.sources import render_search
        return render_search(store or Store([]), pattern, SourceContext(self.repo), **kw)

    def hits(self, out):
        return [line for line in out.splitlines() if line.startswith('fallback ')]

    def test_unindexed_fact_is_recovered_without_any_records(self):
        out=self.search('previously unrecorded fact')
        self.assertEqual(len(self.hits(out)),1)
        self.assertIn('fallback',out)
        self.assertIn('../corpus/unindexed.txt',out)
        self.assertIn('records=[]',out)
        self.assertIn(hashlib.sha256((self.corpus/'unindexed.txt').read_bytes()).hexdigest(),out)
        self.assertNotIn(str(self.base),out)
        self.assertIn('unavailable',out)  # absent configured root remains visible

    def test_stable_path_then_line_order_limit_omissions_and_current_hash(self):
        store=Store([self.record([self.anchor(path='changed.txt')])])
        out=self.search('needle',store=store,max_hits=2)
        self.assertEqual(out,self.search('needle',store=store,max_hits=2))
        hits=self.hits(out)
        self.assertEqual(len(hits),2)
        self.assertIn('changed.txt',hits[0])
        self.assertIn('line=2',hits[0])
        self.assertIn('line=4',hits[1])
        self.assertIn('C@1',hits[0])
        self.assertIn(hashlib.sha256((self.corpus/'changed.txt').read_bytes()).hexdigest(),hits[0])
        self.assertIn('3 hit(s) omitted; 5 matching line(s)',out)
        self.assertIn('5 hit(s) omitted',self.search('needle',max_hits=0))
        self.assertEqual(len(self.hits(self.search('shared.*needle'))),0)
        self.assertEqual(len(self.hits(self.search('shared.*needle',regex=True))),5)

    def test_only_configured_roots_and_explicit_implicit_repo_selection(self):
        (self.repo/'local.txt').write_text('local-only-token\n')
        self.assertEqual(self.hits(self.search('local-only-token')),[])
        self.assertEqual(len(self.hits(self.search('local-only-token',root='.'))),1)
        self.assertNotIn('unavailable',self.search('needle',root='corpus'))
        with self.assertRaises(ValueError):self.search('needle',root=str(self.repo))
        with self.assertRaises(ValueError):self.search('needle',root='not-configured')
        (self.repo/'.aec/sources.json').unlink()
        self.assertEqual(self.hits(self.search('local-only-token')),[])

    def test_symlink_escape_no_execution_network_or_writes(self):
        import os
        before={p:p.read_bytes() for p in self.base.rglob('*') if p.is_file()}
        external=self.repo/'external.py'
        external.write_text("raise RuntimeError('secret-only-token')\n")
        (self.corpus/'outside.py').symlink_to(external)
        (self.corpus/'external-dir').symlink_to(self.repo,target_is_directory=True)
        (self.corpus/'internal-cycle').symlink_to(self.corpus,target_is_directory=True)
        (self.corpus/'inside.txt').symlink_to(self.corpus/'valid.txt')
        os.mkfifo(self.corpus/'pipe')
        from aec.sources import render_search, render_show
        with patch('socket.socket',side_effect=AssertionError('network')), \
             patch('urllib.request.urlopen',side_effect=AssertionError('network')), \
             patch('subprocess.Popen',side_effect=AssertionError('execution')), \
             patch.object(Path,'write_bytes',side_effect=AssertionError('write')), \
             patch.object(Path,'write_text',side_effect=AssertionError('write')):
            self.assertEqual(self.hits(self.search('secret-only-token')),[])
            self.assertTrue(any('inside.txt' in h for h in self.hits(self.search('needle'))))
            rec=self.record()
            ctx=SourceContext(self.repo)
            self.assertEqual(check(Store([rec]),sources=ctx),[])
            self.assertIn('2 | shared needle',render_show(Store([rec]),'C@1',ctx,context=0))
        self.assertTrue(all(p.read_bytes()==raw for p,raw in before.items()))

    def test_search_cli_repeat_and_bad_arguments(self):
        args=('source','search','needle','--repo',str(self.repo),'--max','2')
        a=self.cli(*args)
        self.assertEqual(a[0],0)
        self.assertEqual(a,self.cli(*args))
        self.assertEqual(len(self.hits(a[1])),2)
        self.assertEqual(self.cli(*args,'--max','-1')[0],2)
        self.assertEqual(self.cli('source','search','[','--regex','--repo',str(self.repo))[0],2)
        self.assertEqual(self.cli(*args,'--root','unknown')[0],2)
        for payload in ['[]','{"roots": []}','{"roots": {"remote": "https://example.com"}}']:
            (self.repo/'.aec/sources.json').write_text(payload)
            self.assertEqual(self.cli(*args)[0],2)


class TestSourceEdgeCases(SourceFixture):
    def test_absolute_root_and_permission_failure_do_not_become_missing(self):
        (self.repo/'.aec/sources.json').write_text(json.dumps({'roots': {'corpus':str(self.corpus)}}))
        self.assertEqual(self.findings(self.record()),[])
        self.save([self.record()])
        with patch.object(Path,'read_bytes',side_effect=PermissionError('blocked')):
            fs=self.findings(self.record())
            self.assertEqual(fs[0].rule,'anchor-unavailable')

    def test_mismatch_precedence_and_show_no_invalid_substitute(self):
        from aec.sources import render_show
        r=self.record([self.anchor(path='changed.txt',locator='q:no match')])
        ctx=SourceContext(self.repo)
        self.assertEqual(ctx.inspect_record(r)[0].state,'mismatch')
        out=render_show(Store([r]),'C@1',ctx)
        self.assertIn('WARNING:',out)
        self.assertIn('No resolved passage',out)
        self.assertNotIn('1 |',out)
        self.assertEqual(self.findings(self.record([self.anchor(locator='L1-999')] ))[0].rule,'anchor-locator_invalid')

    def test_snapshot_reads_are_reused_within_one_command(self):
        from aec.sources import render_show
        r=self.record()
        ctx=SourceContext(self.repo)
        self.assertEqual(check(Store([r]),sources=ctx),[])
        (self.corpus/'valid.txt').write_text('new bytes after check\n')
        self.assertIn('2 | shared needle',render_show(Store([r]),'C@1',ctx,context=0))
        self.assertEqual(SourceContext(self.repo).inspect_record(r)[0].state,'mismatch')

    def test_search_records_all_versions_and_missing_default_records_is_not_a_gate(self):
        from aec.sources import render_search
        first=self.record()
        second=self.record()
        second.version=2
        out=render_search(Store([first,second]),'needle',SourceContext(self.repo))
        valid_hit=next(line for line in out.splitlines() if line.startswith('fallback') and 'valid.txt' in line)
        self.assertIn('["C@1", "C@2"]',valid_hit)
        self.records.unlink()
        result=self.cli('source','search','previously unrecorded','--repo',str(self.repo))
        self.assertEqual(result[0],0)
        self.assertIn('records=[]',result[1])


class TestLocatorShape(SourceFixture):
    def test_quote_line_breaks_and_rooted_paths_are_malformed_with_clean_decoy(self):
        for locator in ['q:a\nb','q:a\u2028b']:
            self.assertTrue(any(f.level=='error' for f in self.findings(self.record([self.anchor(locator=locator)]))))
        self.assertTrue(any(f.level=='error' for f in self.findings(self.record([self.anchor(path='\\rooted')]))))
        self.assertEqual(self.findings(self.record([self.anchor(locator='q:shared needle')])),[])


class TestSearchCharacterBound(SourceFixture):
    def long_line(self):
        fixture=json.loads((ROOT/'tests/fixtures/anchors/long-line.json').read_text())
        line='a'*fixture['prefix_chars']+'FIRST '+fixture['term']+' HERE'+'z'*fixture['suffix_chars']+' SECOND '+fixture['term']
        self.assertGreaterEqual(len(line),1024*1024)
        (self.corpus/'long.json').write_text(line+'\n')
        return fixture,line

    def payload(self, output):
        hit=next(line for line in output.splitlines() if line.startswith('fallback '))
        return hit.split('records=[]: ',1)[1]

    def test_megabyte_line_default_and_cli_bounds_keep_first_match(self):
        fixture,line=self.long_line()
        args=('source','search',fixture['term'],'--repo',str(self.repo),'--root','corpus')
        code,out,err=self.cli(*args)
        self.assertEqual(code,0,err)
        payload=self.payload(out)
        self.assertLessEqual(len(payload),240)
        self.assertIn('FIRST Merfolk HERE',payload)
        self.assertNotIn('SECOND',payload)
        import re
        counts=[int(n) for n in re.findall(r'…\[\+(\d+) chars\]',payload)]
        visible=re.sub(r'…\[\+\d+ chars\]','',payload)
        self.assertEqual(sum(counts)+len(visible),len(line))
        self.assertRegex(payload,r'^…\[\+\d+ chars\]')
        self.assertRegex(payload,r'…\[\+\d+ chars\]$')
        code,out,err=self.cli(*args,'--max-chars',str(fixture['max_chars']))
        self.assertEqual(code,0,err)
        self.assertLessEqual(len(self.payload(out)),fixture['max_chars'])
        self.assertIn(fixture['term'],self.payload(out))
        self.assertEqual((code,out,err),self.cli(*args,'--max-chars',str(fixture['max_chars'])))
        self.assertEqual(self.cli(*args,'--max-chars','0')[0],2)
        self.assertEqual(self.cli(*args,'--max-chars','-1')[0],2)

    def test_regex_edges_long_matches_and_short_line_decoy(self):
        from aec.sources import render_search
        for line,pattern,regex in [('Merfolk'+'x'*1000,'Merfolk',False),
                                   ('x'*1000+'Merfolk','Merf.lk',True),
                                   ('x'*1000+'Merfolk'+'y'*1000,'x+Merfolk',True)]:
            (self.corpus/'edge.txt').write_text(line)
            out=render_search(Store([]),pattern,SourceContext(self.repo),root='corpus',regex=regex,max_chars=80)
            self.assertLessEqual(len(self.payload(out)),80)
            self.assertIn('…[+',self.payload(out))
        out=render_search(Store([]),'third',SourceContext(self.repo),root='corpus',max_chars=80)
        self.assertEqual(self.payload(out),'third')
        out=render_search(Store([]),'needle',SourceContext(self.repo),root='corpus',max_chars=1)
        self.assertEqual(self.payload(out),'…')


if __name__ == '__main__':
    unittest.main()
