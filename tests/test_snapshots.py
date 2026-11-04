"""WP1A fixtures are authored before implementation; only local git builds history."""
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'src'))
from aec import edges as E
from aec.__main__ import main


def git(root,*args):
    result=subprocess.run(['git','-c','core.hooksPath=/dev/null','-C',str(root),*args],capture_output=True,check=True,text=True)
    return result.stdout.strip()


class History(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'repo'
        self.root.mkdir()
        git(self.root,'init','-q','-b','main')
        git(self.root,'config','user.name','Fixture')
        git(self.root,'config','user.email','fixture@example.invalid')
        files=json.loads((ROOT/'tests/fixtures/commit_snapshots/base.json').read_text())
        for path,content in files.items():
            p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
        self.base=self.commit('base')
        git(self.root,'checkout','-q','-b','topic')
        p=self.root/'src/a/x.py'
        p.write_text(p.read_text()+'\ndef added():\n    return target()\n')
        self.head=self.commit('branch')
        git(self.root,'checkout','-q','main')
        (self.root/'base_only.py').write_text('def base_only():\n    return 2\n')
        self.tip=self.commit('base advances')
        git(self.root,'checkout','-q','topic')

    def commit(self,message):
        git(self.root,'add','.')
        git(self.root,'commit','-qm',message)
        return git(self.root,'rev-parse','HEAD')

    def cli(self,*args):
        out,err=io.StringIO(),io.StringIO()
        with redirect_stdout(out),redirect_stderr(err):
            try:code=main(list(args))
            except SystemExit as e:code=e.code
        return code,out.getvalue(),err.getvalue()


class TestRevisionSnapshots(History):
    def test_revision_repeat_checkout_decoy_and_no_target_execution(self):
        a=E.snapshot(self.root,rev=self.base)
        self.assertEqual(E.dumps(a),E.dumps(E.snapshot(self.root,rev=self.base)))
        self.assertEqual(a['header']['revision'],self.base)
        self.assertEqual(a['header']['revision_kind'],'commit')
        self.assertNotIn('root',a['header'])
        self.assertNotIn(str(self.root),E.dumps(a))
        self.assertNotIn('/tmp/',E.dumps(a))
        git(self.root,'checkout','-q',self.base)
        self.assertEqual(a['edges'],E.snapshot(self.root)['edges'])
        self.assertEqual(git(self.root,'rev-parse','HEAD'),self.base)
        self.assertEqual([x['file'] for x in a['header']['skipped']],['bad.py'])
        self.assertEqual(a['header']['method']['tool_version'],E.TOOL_VERSION)
        self.assertEqual(len(a['header']['method_sha']),64)

    def test_dirty_clean_and_non_git_working_tree(self):
        snap=E.snapshot(self.root)
        self.assertEqual(snap['header']['revision_kind'],'working-tree')
        self.assertFalse(snap['header']['dirty'])
        self.assertEqual(snap['header']['base_revision'],self.head)
        (self.root/'src/a/x.py').write_text('# edited\n')
        self.assertTrue(E.snapshot(self.root)['header']['dirty'])
        plain=Path(self.tmp.name)/'plain';plain.mkdir()
        (plain/'one.py').write_text('X=1\n')
        self.assertIsNone(E.snapshot(plain)['header']['base_revision'])

    def test_method_configuration_and_legacy_mismatch(self):
        original=E.snapshot(self.root)
        ignored=E.snapshot(self.root,ignore={'bad.py'})
        with self.assertRaisesRegex(ValueError,'method mismatch'):E.diff(original,ignored)
        self.assertIn('ignore',str(E.diff(original,ignored,allow_method_mismatch=True)))
        old=copy.deepcopy(original)
        old['header'].pop('method');old['header'].pop('method_sha')
        old['header']['tool_version']='0.3.0'
        loaded=E.loads(E.dumps(old))
        self.assertEqual(loaded['header']['revision_kind'],'unknown')
        with self.assertRaisesRegex(ValueError,'method mismatch'):E.diff(loaded,original)

    def test_commit_does_not_follow_links_or_change_working_tree(self):
        outside=Path(self.tmp.name)/'outside.py';outside.write_text('SECRET=1\n')
        (self.root/'linked.py').symlink_to(outside)
        rev=self.commit('link')
        before=git(self.root,'status','--porcelain')
        snap=E.snapshot(self.root,rev=rev)
        self.assertNotIn('linked',snap['header']['modules'])
        self.assertEqual(git(self.root,'status','--porcelain'),before)
        self.assertNotIn('SECRET',E.dumps(snap))


class TestUnresolvedReasons(History):
    def test_each_reason_filtered_alone_and_external_decoy(self):
        from aec.graph import unresolved, visibility
        snap=E.snapshot(self.root,rev=self.head)
        expected={'local_value','self_attr_unknown','unbound_name','computed_callee','reflective'}
        self.assertEqual({e['why'] for e in unresolved(snap)},expected)
        for why in sorted(expected):
            rows=unresolved(snap,why=[why])
            self.assertTrue(rows)
            self.assertEqual({r['why'] for r in rows},{why})
        self.assertFalse(any(e['dst']=='thirdparty.run' for e in unresolved(snap)))
        self.assertGreater(visibility(snap,'calls')['projection']['external'],0)
        local=unresolved(snap,why=['local_value'],scope='src.a.x.constructed')
        self.assertEqual([e['dst'] for e in local],['?p.profile_dataset'])
        self.assertEqual(unresolved(snap,scope='src/b/y.py'),[])
        self.assertEqual(unresolved(snap),unresolved(E.snapshot(self.root,rev=self.head)))

    def test_bound_calls_are_decoys_and_reflection_aliases_are_retained(self):
        (self.root/'calls.py').write_text('from importlib import import_module as load\n'
            'def f(eval, callback):\n    eval()\n    callback()\n'
            'def g():\n    load("anything")\n    __import__("anything")\n    exec("nothing")\n')
        snap=E.snapshot(self.root)
        rows=[e for e in snap['edges'] if e['kind']=='calls' and e['file']=='calls.py']
        self.assertEqual(next(e['why'] for e in rows if e['dst']=='?eval'),'local_value')
        self.assertEqual({e['why'] for e in rows if e['src']=='calls.g'},{'reflective'})


class TestStructuralDiff(History):
    def test_merge_base_boundary_and_moving_base_decoy(self):
        from aec.snapshots import compare_revisions
        report=compare_revisions(self.root,base='main',head='topic')
        self.assertEqual(report['base_revision'],self.base)
        self.assertEqual(report['head_revision'],self.head)
        cross=report['cross_module_changes']['added']
        self.assertEqual([(e['kind'],e['src'],e['dst']) for e in cross],
                         [('calls','src.a.x.added','src.b.y.target')])
        self.assertEqual(cross[0]['boundary'],{'directory':'src','src_depth':1,'dst_depth':1})
        self.assertTrue(cross[0]['crosses_public_surface'])
        self.assertNotIn('base_only',json.dumps(report))
        self.assertEqual(report,compare_revisions(self.root,base='main',head='topic'))
        self.assertNotIn('/tmp/',json.dumps(report))

    def test_head_configuration_is_symmetric_and_change_is_separate(self):
        from aec.snapshots import compare_revisions
        (self.root/'.aec').mkdir()
        (self.root/'.aec/extraction.json').write_text(json.dumps({'ignore':['src/b/*']}))
        head=self.commit('method changes')
        report=compare_revisions(self.root,base='main',head=head)
        self.assertEqual(report['base_method_sha'],report['head_method_sha'])
        self.assertEqual(report['method_change']['fields'],['ignore'])
        self.assertIn('method change in this PR',report['method_change']['message'])
        self.assertNotIn('src.b.y',report['modules_removed'])  # ignore applied to both sides

    def test_same_file_cross_class_is_not_a_module_boundary(self):
        from aec.snapshots import annotate_edge
        snap=E.snapshot(self.root)
        edge=next(e for e in snap['edges'] if e['kind']=='calls' and e['src']=='src.a.x.B.call')
        annotated=annotate_edge(snap,edge)
        self.assertFalse(annotated['cross_module'])
        self.assertTrue(annotated['cross_class'])
        self.assertNotIn('boundary',annotated)
        # Internal same-class edges and public export calls are clean decoys.
        e={'kind':'calls','src':'src.a.x.A.missing','dst':'src.a.x.A.missing','file':'src/a/x.py','line':1,'resolved':True}
        self.assertFalse(annotate_edge(snap,e)['cross_class'])
        e=dict(e,src='src.a.x.caller',dst='src.b.y.public')
        self.assertFalse(annotate_edge(snap,e)['crosses_public_surface'])


class TestProjectionQueries(History):
    def setUp(self):
        super().setUp()
        (self.root/'region.py').write_text('import thirdparty\ndef target():\n    return 1\n'
            'def direct():\n    return target()\ndef indirect(callback):\n    return callback()\n'
            'class Base: pass\nclass Child(Base): pass\n')
        self.snap=E.snapshot(self.root)

    def test_reach_region_visibility_and_projection_decoys(self):
        from aec.graph import CAVEAT, reach
        report=reach(self.snap,'region.target',direction='callers',depth=1)
        self.assertEqual(report['reachable'],['region.direct'])
        self.assertEqual(report['visibility']['region']['unresolved_by_why']['local_value'],1)
        self.assertEqual(report['caveat'],CAVEAT)
        self.assertIn('functions',report['node_type'])
        self.assertEqual(reach(self.snap,'region.target',depth=0)['reachable'],[])
        imports=reach(self.snap,'src.a.x',projection='imports',direction='callees')
        self.assertEqual(imports['node_type'],'modules')
        self.assertIn('src.b.y',imports['reachable'])
        self.assertNotIn('src.b.y.target',imports['reachable'])
        inheritance=reach(self.snap,'region.Base',projection='inherits')
        self.assertEqual(inheritance['reachable'],['region.Child'])
        self.assertEqual(inheritance['node_type'],'classes')
        with self.assertRaises(ValueError):reach(self.snap,'not_a_symbol')

    def test_fan_agrees_with_hand_counts_and_is_projection_specific(self):
        from aec.graph import CAVEAT, fan
        result=fan(self.snap,top=100)
        rows={r['symbol']:r for r in result['nodes']}
        self.assertEqual((rows['region.target']['fan_in'],rows['region.target']['fan_out']),(1,0))
        self.assertEqual((rows['region.direct']['fan_in'],rows['region.direct']['fan_out']),(0,1))
        self.assertNotIn('?callback',rows)
        self.assertEqual(result['caveat'],CAVEAT)
        self.assertIn('skipped',result['visibility'])
        imports=fan(self.snap,projection='imports',top=100)
        modules={r['symbol']:r for r in imports['nodes']}
        self.assertNotIn('region.direct',modules)
        self.assertEqual(modules['src.a.x']['fan_out'],3)
        self.assertEqual(fan(self.snap,top=0)['nodes'],[])
        with self.assertRaises(ValueError):fan(self.snap,projection='defines')


class TestTopologyCLI(History):
    def test_snapshot_unresolved_and_query_outputs_are_repeatable_and_relative(self):
        from aec.graph import CAVEAT
        commands=[('snapshot',str(self.root),'--rev',self.head),
                  ('unresolved','--repo',str(self.root),'--why','local_value','--in','src/a/x.py','--json'),
                  ('reach','src.b.y.target','--repo',str(self.root),'--rev',self.head,'--json'),
                  ('fan','--repo',str(self.root),'--rev',self.head,'--json'),
                  ('diff','--repo',str(self.root),'--base','main','--head','topic','--json')]
        for args in commands:
            with self.subTest(command=args[0]):
                result=self.cli(*args)
                self.assertEqual(result[0],0,result[2])
                self.assertEqual(result,self.cli(*args))
                self.assertNotIn('/tmp/',result[1])
                if args[0] in ('reach','fan'):
                    self.assertIn(CAVEAT,result[1]);self.assertIn('visibility',result[1])
        result=self.cli('unresolved','--repo',str(self.root),'--why','reflective','local_value','--json')
        self.assertEqual(result[0],0,result[2])
        rows=json.loads(result[1])['edges']
        self.assertEqual({e['why'] for e in rows},{'reflective','local_value'})

    def test_stored_mismatch_refusal_override_and_clean_decoy(self):
        a,b=self.root/'a.jsonl',self.root/'b.jsonl'
        E_snapshot=E.snapshot(self.root)
        a.write_text(E.dumps(E_snapshot));b.write_text(E.dumps(E.snapshot(self.root,ignore={'bad.py'})))
        args=('diff','--base-snapshot',str(a),'--head-snapshot',str(b))
        result=self.cli(*args)
        self.assertEqual(result[0],2)
        self.assertIn('method mismatch',result[2])
        result=self.cli(*args,'--allow-method-mismatch')
        self.assertEqual(result[0],0,result[2])
        self.assertTrue(result[1].startswith('METHOD COMPARISON'))
        b.write_bytes(a.read_bytes())
        self.assertEqual(self.cli(*args)[0],0)

    def test_ci_uploads_report_without_commenting(self):
        text=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('aec diff --base origin/main --head',text)
        self.assertIn('actions/upload-artifact@v4',text)
        self.assertIn('github.event.pull_request.head.sha',text)
        self.assertNotIn('createComment',text)


class TestReviewRegressions(History):
    def test_working_snapshot_never_runs_git_filters_hooks_or_refreshes_index(self):
        import shlex
        marker=Path(self.tmp.name)/'filter-ran'
        hook_marker=Path(self.tmp.name)/'hook-ran'
        (self.root/'.gitattributes').write_text('unsafe.py filter=probe\n')
        self.commit('attributes')
        git(self.root,'config','filter.probe.clean','printf x > '+shlex.quote(str(marker)))
        hook=self.root/'.git/hooks/post-index-change'
        hook.write_text('#!/bin/sh\nprintf x > '+shlex.quote(str(hook_marker))+'\n')
        hook.chmod(0o755)
        (self.root/'unsafe.py').write_text('VALUE=3\n')
        index=(self.root/'.git/index').read_bytes()
        result=E.snapshot(self.root)
        self.assertTrue(result['header']['dirty'])
        self.assertFalse(marker.exists(),'target clean filter ran')
        self.assertFalse(hook_marker.exists(),'target hook ran')
        self.assertEqual(index,(self.root/'.git/index').read_bytes())

    def test_unparsed_submodule_is_external_not_parent_package(self):
        from aec.graph import fan, visibility
        from aec.snapshots import annotate_edge
        (self.root/'pkg').mkdir();(self.root/'pkg/__init__.py').write_text('')
        (self.root/'main.py').write_text('from pkg.plugin import run\ndef caller():\n    run()\n')
        snap=E.snapshot(self.root)
        calls=next(e for e in snap['edges'] if e['kind']=='calls' and e['src']=='main.caller')
        self.assertIsNone(annotate_edge(snap,calls)['cross_module'])
        imports=fan(snap,projection='imports',top=100)
        self.assertIn('pkg.plugin',{r['symbol'] for r in imports['nodes']})
        self.assertEqual(visibility(snap,'calls',region={'main.caller'})['region']['external'],1)
        # A known external node still has touching-edge visibility at depth zero.
        from aec.graph import reach
        self.assertEqual(reach(snap,'pkg.plugin.run',depth=0)['visibility']['region']['external'],1)

    def test_dynamic_export_mutations_do_not_invent_private_surface_findings(self):
        from aec.snapshots import annotate_edge
        (self.root/'exports.py').write_text('__all__ = []\n__all__.append("public")\ndef public(): pass\n')
        (self.root/'use_exports.py').write_text('from exports import public\npublic()\n')
        snap=E.snapshot(self.root)
        edge=next(e for e in snap['edges'] if e['kind']=='calls' and e['file']=='use_exports.py')
        self.assertNotIn('exports',snap['header']['exports'])
        self.assertFalse(annotate_edge(snap,edge)['crosses_public_surface'])


class TestMethodIntegrity(History):
    def test_legacy_header_cannot_borrow_current_method_identity(self):
        current=E.snapshot(self.root)
        old=copy.deepcopy(current);old['header']['tool_version']='0.3.0'
        loaded=E.loads(E.dumps(old))
        self.assertEqual(loaded['header']['revision_kind'],'unknown')
        with self.assertRaisesRegex(ValueError,'method mismatch'):E.diff(loaded,current)
        forged=copy.deepcopy(current);forged['header']['method_sha']='0'*64
        with self.assertRaisesRegex(ValueError,'method mismatch'):E.diff(forged,current)
        self.assertEqual(E.diff(current,current)['added'],[])

    def test_source_root_configuration_and_invalid_config_decoy(self):
        (self.root/'.aec').mkdir()
        config=self.root/'.aec/extraction.json'
        config.write_text(json.dumps({'source_roots':['src']}))
        snap=E.snapshot(self.root)
        self.assertEqual(snap['header']['method']['source_roots'],['src'])
        config.write_text(json.dumps({'source_roots':['/absolute/not_allowed']}))
        with self.assertRaises(ValueError):E.snapshot(self.root)


class TestSecondReviewRegressions(History):
    def test_static_reexport_keeps_definition_owner_and_import_unit_distinct(self):
        from aec.graph import fan, visibility
        from aec.snapshots import annotate_edge
        (self.root/'pkg').mkdir()
        (self.root/'pkg/__init__.py').write_text('from .impl import public\n__all__=["public"]\n')
        (self.root/'pkg/impl.py').write_text('def public(): pass\n')
        (self.root/'use.py').write_text('from pkg import public\npublic()\n')
        snap=E.snapshot(self.root)
        edge=next(e for e in snap['edges'] if e['kind']=='calls' and e['file']=='use.py')
        annotated=annotate_edge(snap,edge)
        self.assertTrue(annotated['cross_module'])
        self.assertEqual(annotated['boundary']['directory'],'.')
        self.assertEqual(visibility(snap,'calls',region={'use'})['region']['external'],0)
        from aec.graph import reach
        self.assertIn('use',reach(snap,'pkg.impl.public')['reachable'])
        imported={row['symbol'] for row in fan(snap,projection='imports',top=100)['nodes']}
        self.assertIn('pkg',imported)

    def test_dirty_initialized_submodule_is_not_reported_clean(self):
        child=self.root/'child';child.mkdir()
        git(child,'init','-q')
        git(child,'config','user.name','Fixture');git(child,'config','user.email','fixture@example.invalid')
        (child/'one.py').write_text('X=1\n')
        git(child,'add','.');git(child,'commit','-qm','child')
        child_sha=git(child,'rev-parse','HEAD')
        git(self.root,'update-index','--add','--cacheinfo','160000,'+child_sha+',child')
        git(self.root,'commit','-qm','gitlink')
        (child/'one.py').write_text('X=2\n')
        self.assertTrue(E.snapshot(self.root)['header']['dirty'])


class TestAliasCycles(History):
    def test_expanding_import_alias_is_bounded_and_remains_external(self):
        from aec.graph import fan, reach
        (self.root/'a.py').write_text('from a.b import c as b\n')
        (self.root/'main.py').write_text('from a import b\nb()\n')
        snap=E.snapshot(self.root)
        result=fan(snap,top=100)
        self.assertIn('a.b',{row['symbol'] for row in result['nodes']})
        self.assertGreater(result['visibility']['projection']['external'],0)
        self.assertIn('a.b',reach(snap,'main',direction='callees')['reachable'])


class TestRuntimeMethod(History):
    def test_parser_method_difference_is_refused(self):
        snap=E.snapshot(self.root)
        self.assertIn('python_ast',snap['header']['method'])
        other=copy.deepcopy(snap)
        other['header']['method']['python_ast']='different-parser'
        from aec.snapshots import method_sha
        other['header']['method_sha']=method_sha(other['header']['method'])
        with self.assertRaisesRegex(ValueError,'python_ast'):E.diff(snap,other)


if __name__ == '__main__':
    unittest.main()
