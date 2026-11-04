"""HO-RK-20261104-DN2X: the three code-impact gaps Codex found (A5RR, section B).

Fixture rebuilt from the report: price(x) = min(LIMIT, helper(x)), LIMIT = 10, helper(x) = max(0, x);
one requirement linked to the code, one claim depending on the requirement. Each check has violating
cases and clean decoys, written before the implementation (Constitution III).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from aec import edges as E  # noqa: E402
from aec.code_impact import code_impact  # noqa: E402
from aec.records import Store  # noqa: E402

BASE = '''LIMIT = 10


def deep(x):
    return x


def helper(x):
    return max(0, deep(x))


def price(x):
    return min(LIMIT, helper(x))


def unrelated():
    return 1
'''
OTHER = "def tax(x):\n    return x\n"
EDITS = {
    "comment": lambda s: s.replace("def price(x):", "def price(x):\n    # clamp to the limit"),
    "swap_min": lambda s: s.replace("min(LIMIT, helper(x))", "min(helper(x), LIMIT)"),
    "price_identity": lambda s: s.replace("return min(LIMIT, helper(x))", "return x"),
    "helper_unbounded": lambda s: s.replace("max(0, deep(x))", "deep(x)"),
    "limit_100": lambda s: s.replace("LIMIT = 10", "LIMIT = 100"),
    "deep_changed": lambda s: s.replace("def deep(x):\n    return x", "def deep(x):\n    return -x"),
    "unrelated_changed": lambda s: s.replace("return 1", "return 2"),
    "function_added": lambda s: s + "\n\ndef extra():\n    return 3\n",
}


def tree(pricing: str, package=False) -> Path:
    d = Path(tempfile.mkdtemp())
    pkg = d / "shop" if package else d
    pkg.mkdir(exist_ok=True)
    if package:
        (pkg / "__init__.py").write_text("VERSION = 1\n")
    (pkg / "pricing.py").write_text(pricing)
    (pkg / "other.py").write_text(OTHER)
    return d


def store(link: str) -> Store:
    f = Path(tempfile.mkdtemp()) / "r.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in [
        {"id": "REQ-price", "version": 1, "type": "requirement", "text": "prices stay between 0 and 10",
         "relations": [{"rel": "implemented_by", "to": link}]},
        {"id": "CL-price", "version": 1, "type": "claim", "text": "pricing satisfies REQ-price",
         "relations": [{"rel": "depends_on", "to": "REQ-price@1"}]},
    ]) + "\n")
    return Store.load(f)


def run(link: str, edit: str | None, package=False, **kw):
    old = E.snapshot(tree(BASE, package))
    new = E.snapshot(tree(EDITS[edit](BASE) if edit else BASE, package))
    rep, events = code_impact(store(link), old, new, **kw)
    return {k: v.status for k, v in rep.impacts.items()}, rep.findings, events


class TestModuleLinks(unittest.TestCase):
    """Gap 2: `code:pricing` (what import-purpose writes) passed `check` but no edit ever reached it.
    A module's definitions are part of its body, the same way a class's methods are part of the class."""

    def test_edits_inside_the_module_reach_a_module_link(self):  # violating
        for edit in ("swap_min", "price_identity", "helper_unbounded", "limit_100", "function_added"):
            with self.subTest(edit=edit):
                st, _, _ = run("code:pricing", edit)
                self.assertEqual(st.get("REQ-price@1"), "stale")
                self.assertEqual(st.get("CL-price@1"), "needs_review")

    def test_comment_only_edit_does_not_reach_a_module_link(self):  # decoy
        self.assertEqual(run("code:pricing", "comment")[0], {})

    def test_no_edit_no_module_impact(self):  # decoy
        self.assertEqual(run("code:pricing", None)[0], {})

    def test_sibling_module_link_is_not_reached(self):  # decoy
        self.assertEqual(run("code:other", "helper_unbounded")[0], {})

    def test_package_link_does_not_cover_its_submodules(self):  # decoy: shop.pricing is its own module
        self.assertEqual(run("code:shop", "helper_unbounded", package=True)[0], {})
        st, _, _ = run("code:shop.pricing", "helper_unbounded", package=True)
        self.assertEqual(st.get("REQ-price@1"), "stale")


class TestReachedChanges(unittest.TestCase):
    """Gap 1: a requirement linked to `pricing.price` missed changes to `helper` and `LIMIT`. The fix reports
    them as review pointers; it does not change what a link means (no status is assigned through a callee)."""

    def test_changed_callee_is_reported_without_reclassifying(self):  # violating
        st, findings, events = run("code:pricing.price", "helper_unbounded")
        self.assertEqual(st, {})  # link meaning unchanged: a callee change marks nothing stale
        self.assertEqual(events, [])
        hits = [f for f in findings if "reaches changed code:pricing.helper" in f]
        self.assertEqual(len(hits), 1)
        self.assertIn("REQ-price@1", hits[0])
        self.assertIn("calls", hits[0])

    def test_changed_constant_is_reported(self):  # violating
        _, findings, _ = run("code:pricing.price", "limit_100")
        self.assertTrue(any("reaches changed code:pricing.LIMIT" in f and "references" in f for f in findings))

    def test_unreached_change_is_not_reported(self):  # decoy
        for edit in ("unrelated_changed", "function_added", "comment"):
            with self.subTest(edit=edit):
                self.assertEqual(run("code:pricing.price", edit)[1], [])

    def test_directly_changed_link_is_not_also_reported_as_reached(self):  # decoy
        st, findings, _ = run("code:pricing.price", "price_identity")
        self.assertEqual(st.get("REQ-price@1"), "stale")
        self.assertEqual([f for f in findings if "reaches changed" in f], [])

    def test_depth_bounds_the_report(self):  # decoy at depth 1, violating at depth 2
        self.assertEqual(run("code:pricing.price", "deep_changed")[1], [])
        _, findings, _ = run("code:pricing.price", "deep_changed", reach_depth=2)
        self.assertTrue(any("reaches changed code:pricing.deep" in f and "via code:pricing.helper" in f
                            for f in findings))

    def test_pointer_to_an_already_flagged_record_is_folded(self):  # decoy: the record is already under review
        f = Path(tempfile.mkdtemp()) / "r.jsonl"
        f.write_text("\n".join(json.dumps(r) for r in [
            {"id": "REQ-h", "version": 1, "type": "requirement", "relations": [{"rel": "implemented_by", "to": "code:pricing.helper"}]},
            {"id": "REQ-hp", "version": 1, "type": "requirement", "relations": [
                {"rel": "implemented_by", "to": "code:pricing.helper"}, {"rel": "implemented_by", "to": "code:pricing.price"}]},
            {"id": "REQ-p", "version": 1, "type": "requirement", "relations": [{"rel": "implemented_by", "to": "code:pricing.price"}]},
        ]) + "\n")
        rep, _ = code_impact(Store.load(f), E.snapshot(tree(BASE)), E.snapshot(tree(EDITS["helper_unbounded"](BASE))))
        self.assertEqual(rep.impacts["REQ-hp@1"].status, "stale")
        hits = [x for x in rep.findings if "reaches changed" in x]
        self.assertEqual(len(hits), 1)
        self.assertIn("REQ-p@1", hits[0])  # violating: REQ-p is only reached
        self.assertNotIn("REQ-hp@1", hits[0])  # decoy: already stale, not repeated

    def test_depth_zero_turns_the_report_off(self):
        self.assertEqual(run("code:pricing.price", "helper_unbounded", reach_depth=0)[1], [])

    def test_module_link_gets_no_duplicate_reach_report(self):  # decoy: its contents are already covered
        st, findings, _ = run("code:pricing", "helper_unbounded")
        self.assertEqual(st.get("REQ-price@1"), "stale")
        self.assertEqual([f for f in findings if "reaches changed" in f], [])


@unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "needs git and bash")
class TestDelivery(unittest.TestCase):
    """Gap 3: the generated hook and CI ran `check` only. They now run `code-impact` against HEAD / the PR base
    and surface the report: to the agent (hook stderr, exit 2) and to the reviewer (CI job summary)."""

    def repo(self) -> Path:
        d = tree(BASE)
        env = self.env(d)
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", "-C", str(d), *args], check=True, env=env)
        subprocess.run([sys.executable, "-m", "aec", "init", str(d), "--owner", "t"], check=True, env=env,
                       capture_output=True)
        with (d / ".aec" / "records.jsonl").open("a") as f:
            f.write(json.dumps({"id": "REQ-price", "version": 1, "type": "requirement", "text": "0 <= price <= 10",
                                "relations": [{"rel": "implemented_by", "to": "code:pricing.price"}]}) + "\n")
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True, env=env)
        subprocess.run(["git", "-C", str(d), "commit", "-qm", "base"], check=True, env=env)
        return d

    @staticmethod
    def env(d: Path) -> dict:
        return {**os.environ, "PYTHONPATH": str(ROOT / "src"), "CLAUDE_PROJECT_DIR": str(d),
                "GIT_CONFIG_GLOBAL": os.devnull}

    def hook(self, d: Path):
        cmd = json.loads((d / ".aec" / "snippets" / "claude-settings.json").read_text())
        command = cmd["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
        return subprocess.run(["bash", "-c", command], capture_output=True, text=True, env=self.env(d))

    def test_hook_tells_the_agent_when_linked_code_reaches_a_change(self):  # violating
        d = self.repo()
        (d / "pricing.py").write_text(EDITS["limit_100"](BASE))
        r = self.hook(d)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("reaches changed code:pricing.LIMIT", r.stderr)

    def test_hook_quiet_when_nothing_linked_changed(self):  # decoy
        d = self.repo()
        (d / "pricing.py").write_text(EDITS["unrelated_changed"](BASE))
        r = self.hook(d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr, "")

    def ci(self, d: Path, base: str):
        from aec.init import CI_IMPACT
        summary = d / "summary.md"
        env = {**self.env(d), "GITHUB_STEP_SUMMARY": str(summary), "AEC_BASE": base}
        subprocess.run([sys.executable, "-m", "aec", "edges", ".", "-o", ".aec/edges.jsonl"], cwd=d, check=True,
                       env=env, capture_output=True)  # the job's preceding step
        r = subprocess.run(["bash", "-c", CI_IMPACT], cwd=d, capture_output=True, text=True, env=env)
        return r, summary.read_text() if summary.exists() else ""

    def test_ci_puts_the_report_in_the_job_summary(self):  # violating
        d = self.repo()
        base = subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        (d / "pricing.py").write_text(EDITS["price_identity"](BASE))
        r, summary = self.ci(d, base)
        self.assertEqual(r.returncode, 0, r.stderr)  # report-only: never fails the job
        self.assertIn("[stale] REQ-price@1", summary)

    def test_ci_summary_says_nothing_affected_on_a_clean_change(self):  # decoy
        d = self.repo()
        base = subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        (d / "pricing.py").write_text(EDITS["comment"](BASE))
        r, summary = self.ci(d, base)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("[stale]", summary)
        self.assertIn("0 affected", summary)

    def test_own_ci_runs_the_same_impact_step(self):  # Telosmith's CI dogfoods the generated step
        from aec.init import CI_IMPACT
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
        for line in CI_IMPACT.strip().splitlines():
            self.assertIn(line, ci)

    def test_snippets_run_code_impact(self):
        from aec.init import CI, HOOK
        self.assertIn("code-impact", json.dumps(HOOK))
        self.assertIn("code-impact", CI)
        self.assertIn("fetch-depth: 0", CI)


class TestExitCode(unittest.TestCase):
    def test_exit_code_flag(self):
        from aec.__main__ import main
        d = Path(tempfile.mkdtemp())
        old, new = d / "old.jsonl", d / "new.jsonl"
        old.write_text(E.dumps(E.snapshot(tree(BASE))))
        new.write_text(E.dumps(E.snapshot(tree(EDITS["helper_unbounded"](BASE)))))
        rec = d / "r.jsonl"
        rec.write_text(json.dumps({"id": "R", "version": 1, "type": "requirement",
                                   "relations": [{"rel": "implemented_by", "to": "code:pricing.price"}]}) + "\n")
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["code-impact", str(rec), str(old), str(new)]), 0)
            self.assertEqual(main(["code-impact", str(rec), str(old), str(new), "--exit-code"]), 1)  # violating
            self.assertEqual(main(["code-impact", str(rec), str(old), str(old), "--exit-code"]), 0)  # decoy


# DEC-038 fix round (Kate + Claude reviews of PR #51). Written before the fixes.
FIRST_DELIVERY = (0, 5, 0)  # first release with `aec snapshot`, `code-impact --exit-code`, module/reach logic


def _pinned_ref(ci: str) -> str:
    line = next(x for x in ci.splitlines() if "pip install" in x)
    return line.split("Telosmith.git@", 1)[1].split('"', 1)[0]


class TestFixRoundDelivery(unittest.TestCase):
    def test_generated_ci_pins_nothing_older_than_exit_code(self):
        """v0.4.1 has no `snapshot` or `--exit-code`: a snippet pinned to it reports 'skipped' forever."""
        from aec.init import CI
        ref = _pinned_ref(CI)
        self.assertNotEqual(ref, "v0.4.1")
        if ref.startswith("v"):
            self.assertGreaterEqual(tuple(int(p) for p in ref[1:].split(".")[:3]), FIRST_DELIVERY)

    def test_old_version_falls_back_to_main_loudly(self):
        from aec.init import ci_snippet, install_ref
        ref = install_ref("0.4.1", None)
        self.assertEqual(ref, "main")
        ci = ci_snippet(ref)
        self.assertIn("WARNING", ci)
        self.assertIn("v0.5.0", ci)

    def test_known_commit_is_pinned(self):
        from aec.init import ci_snippet, install_ref
        sha = "0123456789abcdef0123456789abcdef01234567"
        self.assertEqual(install_ref("0.4.1", sha), sha)
        self.assertEqual(_pinned_ref(ci_snippet(sha)), sha)
        self.assertNotIn("WARNING", ci_snippet(sha))

    def test_delivery_release_is_pinned_by_tag(self):
        from aec.init import install_ref
        self.assertEqual(install_ref("0.5.0", None), "v0.5.0")
        self.assertEqual(install_ref("0.5.0.dev1", None), "main")  # not a release

    def test_init_writes_the_resolved_snippet(self):
        from aec.init import init
        d = Path(tempfile.mkdtemp())
        init(d, "t")
        ci = (d / ".aec" / "snippets" / "aec-ci.yml").read_text()
        self.assertNotEqual(_pinned_ref(ci), "v0.4.1")


class TestFixRoundHook(unittest.TestCase):
    repo, env, hook = TestDelivery.repo, staticmethod(TestDelivery.env), TestDelivery.hook

    def test_hook_leaves_the_users_baseline_alone(self):  # violating before the fix
        d = self.repo()
        mine = d / ".aec" / "before.jsonl"
        mine.write_text("my hand-kept baseline\n")
        (d / "pricing.py").write_text(EDITS["limit_100"](BASE))
        r = self.hook(d)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(mine.read_text(), "my hand-kept baseline\n")
        self.assertTrue((d / ".aec" / "hook-before.jsonl").exists())

    def test_hook_baseline_is_git_ignored(self):
        from aec.init import GITIGNORE
        self.assertIn("hook-before.jsonl", GITIGNORE.splitlines())

    def test_hook_says_so_when_the_installed_aec_is_too_old(self):
        """A v0.4.1 install has no `snapshot`: the hook must not pass silently."""
        d = self.repo()
        stub = Path(tempfile.mkdtemp()) / "aec"
        stub.mkdir()
        (stub / "__init__.py").write_text("")
        (stub / "__main__.py").write_text(
            "import sys\nif 'code-impact' in sys.argv: print('usage: code-impact [--json]'); sys.exit(0)\n")
        cmd = json.loads((d / ".aec" / "snippets" / "claude-settings.json").read_text())
        command = cmd["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
        env = {**self.env(d), "PYTHONPATH": str(stub.parent)}
        r = subprocess.run(["bash", "-c", command], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1, r.stderr)  # non-blocking; shown to the user
        self.assertIn("v0.5.0", r.stderr)


class TestFixRoundWording(unittest.TestCase):
    def test_pointer_is_a_candidate_not_an_obligation(self):
        _, findings, _ = run("code:pricing.price", "helper_unbounded")
        ptr = [f for f in findings if "reaches changed" in f]
        self.assertEqual(len(ptr), 1)
        self.assertIn("candidate for attention", ptr[0])
        self.assertIn("no status change", ptr[0])
        self.assertNotIn("review whether", ptr[0])

    def test_summary_does_not_call_a_pointed_record_unaffected(self):
        from aec.__main__ import _print_impact
        import contextlib
        import io
        s = store("code:pricing.price")
        rep, _ = code_impact(s, E.snapshot(tree(BASE)), E.snapshot(tree(EDITS["helper_unbounded"](BASE))))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _print_impact(s, rep, False)
        last = buf.getvalue().strip().splitlines()[-1]
        self.assertNotIn("unaffected", last)
        self.assertIn("no status change", last)
        self.assertIn("1 pointer", last)

    def test_negative_reach_depth_is_rejected(self):
        from aec.__main__ import main
        import contextlib
        import io
        d = Path(tempfile.mkdtemp())
        snap = d / "s.jsonl"
        snap.write_text(E.dumps(E.snapshot(tree(BASE))))
        rec = d / "r.jsonl"
        rec.write_text(json.dumps({"id": "R", "version": 1, "type": "requirement"}) + "\n")
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as cm:
            main(["code-impact", str(rec), str(snap), str(snap), "--reach-depth", "-1"])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("reach-depth", err.getvalue())

    def test_docs_never_say_a_pointer_changes_status(self):
        for rel in ("docs/guide/getting-started.md", "docs/reasoning-vocabulary.md", "CHANGELOG.md",
                    "docs/evaluations/code-impact-qual-001.md"):
            text = (ROOT / rel).read_text()
            self.assertNotIn("review whether", text, rel)
        from aec.init import HOOK_COMMAND
        self.assertIn("candidates for attention", HOOK_COMMAND)


if __name__ == "__main__":
    unittest.main()
