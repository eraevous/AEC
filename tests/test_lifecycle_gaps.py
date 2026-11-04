"""Lifecycle gaps a docs builder found testing the no-Spec-Kit paths (2026-11-04).

1. superseded references: a claim still pointing at R-1@1 after R-1@2 is appended got no warning, and a
   later code change to R-1@2's linked function never reached the claim.
2. depth-2 silence: a change two calls from a linked function printed "0 affected" with no hint that the
   default depth stopped short of it.
3. moved symbol: a dangling `code:` reference suggested nothing although the same name exists elsewhere.
4. init from a source checkout pinned the not-yet-existing tag `@v0.5.0`.

Each class has violating cases and clean decoys, written failing before the fix (Constitution III).
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from aec import edges as E  # noqa: E402
from aec.code_impact import code_impact  # noqa: E402
from aec.impact import render  # noqa: E402
from aec.records import Store, check  # noqa: E402

# the toy from docs/demo.md: apply_discount calls clamp, which calls round_cents
PRICING = '''def round_cents(x):
    return round(x, 2)


def clamp(x):
    return max(0.0, round_cents(x))


def apply_discount(price, pct):
    return clamp(price * (1 - pct / 100))
'''


def shop(pricing: str = PRICING, extra: dict | None = None) -> dict:
    d = Path(tempfile.mkdtemp())
    (d / "shop").mkdir()
    (d / "shop" / "__init__.py").write_text("")
    (d / "shop" / "pricing.py").write_text(pricing)
    for name, text in (extra or {}).items():
        (d / "shop" / name).write_text(text)
    return E.snapshot(d)


def store_from(lines) -> Store:
    f = Path(tempfile.mkdtemp()) / "r.jsonl"
    f.write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    return Store.load(f)


LINK = "code:shop.pricing.apply_discount"
R1 = {"id": "R-1", "version": 1, "type": "requirement", "text": "never negative",
      "relations": [{"rel": "implemented_by", "to": LINK}]}
R2 = {"id": "R-1", "version": 2, "type": "requirement", "text": "never negative, never above list",
      "relations": [{"rel": "supersedes", "to": "R-1@1"}, {"rel": "implemented_by", "to": LINK}]}
C1 = {"id": "C-1", "version": 1, "type": "claim", "text": "totals are never negative",
      "relations": [{"rel": "depends_on", "to": "R-1@1"}]}
C2 = {"id": "C-1", "version": 2, "type": "claim", "text": "totals are never negative",
      "relations": [{"rel": "supersedes", "to": "C-1@1"}, {"rel": "depends_on", "to": "R-1@2"}]}


class TestSupersededReference(unittest.TestCase):
    def sup(self, lines):
        return [(f.level, f.ref, f.msg) for f in check(store_from(lines)) if f.rule == "superseded-reference"]

    def test_reference_to_older_version_warns(self):  # violating before the fix
        fs = self.sup([R1, R2, C1])
        self.assertEqual([(lvl, ref) for lvl, ref, _ in fs], [("warning", "C-1@1")])
        self.assertIn("R-1@1", fs[0][2])
        self.assertIn("R-1@2", fs[0][2])

    def test_reference_to_latest_is_silent(self):  # decoy
        self.assertEqual(self.sup([R1, R2, C1, C2]), [])

    def test_supersedes_itself_is_not_flagged(self):  # decoy: R-1@2 supersedes R-1@1 by design
        self.assertEqual(self.sup([R1, R2]), [])

    def test_superseded_referrer_is_not_judged(self):  # decoy: only latest versions are judged (as in #53)
        self.assertEqual(self.sup([R1, R2, C1, C2]), [])
        old = dict(C1, relations=[{"rel": "depends_on", "to": "R-1@1"}])
        self.assertEqual(self.sup([R1, R2, old, C2]), [])

    def test_never_an_error(self):
        self.assertEqual([f for f in check(store_from([R1, R2, C1])) if f.level == "error"], [])

    def report(self, lines):
        rep, _ = code_impact(store_from(lines), shop(), shop(PRICING.replace("pct / 100)", "pct / 100.0)")))
        return rep

    def test_code_change_reaches_claim_on_superseded_version(self):  # violating before the fix
        rep = self.report([R1, R2, C1])
        self.assertEqual(rep.impacts["R-1@2"].status, "stale")
        self.assertNotIn("C-1@1", rep.impacts)  # a pointer, not a status change
        ptr = [f for f in rep.findings if "references superseded" in f]
        self.assertEqual(len(ptr), 1, rep.findings)
        self.assertIn("C-1@1 references superseded R-1@1; R-1@2 changed", ptr[0])
        self.assertIn("no status change", ptr[0])
        self.assertIn("1 pointer", render(store_from([R1, R2, C1]), rep).splitlines()[-1])

    def test_claim_on_latest_version_gets_a_status_not_a_pointer(self):  # decoy
        rep = self.report([R1, R2, C1, C2])
        self.assertEqual(rep.impacts["C-1@2"].status, "needs_review")
        self.assertEqual([f for f in rep.findings if "references superseded" in f], [])


class TestDepthDisclosure(unittest.TestCase):
    """docs/demo.md step 3: round_cents is two calls from apply_discount."""
    store = store_from([R1, C1])
    old, new = shop(), shop(PRICING.replace("return round(x, 2)", "return int(x * 100) / 100"))

    def test_default_depth_discloses_what_it_did_not_examine(self):  # violating before the fix
        rep, _ = code_impact(self.store, self.old, self.new)
        self.assertEqual((rep.impacts, rep.findings), ({}, []))  # the default is unchanged (#51)
        out = render(self.store, rep)
        self.assertIn("reach depth 1; 1 further symbol within depth 2 not examined (use --reach-depth 2)", out)

    def test_depth_2_finds_it_and_discloses_nothing_further(self):  # decoy: nothing exists at depth 3
        rep, _ = code_impact(self.store, self.old, self.new, reach_depth=2)
        self.assertEqual(len(rep.findings), 1)
        self.assertNotIn("not examined", render(self.store, rep))

    def test_no_changed_definitions_no_footer(self):  # decoy: nothing changed, nothing to disclose
        rep, _ = code_impact(self.store, self.old, self.old)
        self.assertNotIn("not examined", render(self.store, rep))

    def test_depth_0_discloses_depth_1(self):
        rep, _ = code_impact(self.store, self.old, self.new, reach_depth=0)
        self.assertIn("reach depth 0; 1 further symbol within depth 1 not examined (use --reach-depth 1)",
                      render(self.store, rep))

    def test_footer_is_not_a_finding(self):  # the hook stays quiet: --exit-code looks at findings only
        import contextlib
        import io

        from aec.__main__ import main
        d = Path(tempfile.mkdtemp())
        (d / "o.jsonl").write_text(E.dumps(self.old))
        (d / "n.jsonl").write_text(E.dumps(self.new))
        (d / "r.jsonl").write_text("\n".join(json.dumps(x) for x in [R1, C1]) + "\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(["code-impact", str(d / "r.jsonl"), str(d / "o.jsonl"), str(d / "n.jsonl"), "--exit-code"])
        self.assertEqual(code, 0)
        with contextlib.redirect_stdout(buf):
            main(["code-impact", str(d / "r.jsonl"), str(d / "o.jsonl"), str(d / "n.jsonl"), "--json"])
        self.assertIn('"notes"', buf.getvalue())


class TestMovedSymbol(unittest.TestCase):
    def msgs(self, link, extra):
        lines = [{"id": "R", "version": 1, "type": "requirement", "relations": [{"rel": "implemented_by", "to": link}]}]
        snap = shop(PRICING.split("def apply_discount")[0], extra)
        return [f.msg for f in check(store_from(lines), edges=snap) if f.rule == "code-reference"]

    MOVED = "def apply_discount(price, pct):\n    return price\n"

    def test_moved_function_is_suggested(self):  # violating before the fix
        fs = self.msgs(LINK, {"checkout.py": self.MOVED})
        self.assertEqual(len(fs), 1)
        self.assertIn("did you mean code:shop.checkout.apply_discount?", fs[0])

    def test_ambiguous_name_lists_up_to_three(self):
        extra = {f"m{i}.py": self.MOVED for i in range(4)}
        fs = self.msgs(LINK, extra)
        self.assertIn("code:shop.m0.apply_discount, code:shop.m1.apply_discount or code:shop.m2.apply_discount",
                      fs[0])
        self.assertNotIn("shop.m3", fs[0])
        self.assertIn("1 more", fs[0])

    def test_no_same_name_no_guess(self):  # decoy
        fs = self.msgs(LINK, {"checkout.py": "def total(x):\n    return x\n"})
        self.assertNotIn("did you mean", fs[0])

    def test_sibling_typo_and_same_name_both_offered(self):  # the existing near-miss is kept, first
        lines = [{"id": "R", "version": 1, "type": "requirement",
                  "relations": [{"rel": "implemented_by", "to": "code:shop.pricing.clmap"}]}]
        snap = shop(extra={"other.py": "def clmap(x):\n    return x\n"})
        fs = [f.msg for f in check(store_from(lines), edges=snap) if f.rule == "code-reference"]
        self.assertIn("did you mean code:shop.pricing.clamp or code:shop.other.clmap?", fs[0])

    def test_existing_prefix_rule_unchanged(self):  # decoy: a missing source root still wins alone
        lines = [{"id": "R", "version": 1, "type": "requirement",
                  "relations": [{"rel": "implemented_by", "to": "code:pricing.clamp"}]}]
        snap = shop(extra={"other.py": "def clamp(x):\n    return x\n"})
        fs = [f.msg for f in check(store_from(lines), edges=snap) if f.rule == "code-reference"]
        self.assertIn("did you mean code:shop.pricing.clamp?", fs[0])


class TestInitPinFromSourceCheckout(unittest.TestCase):
    """RELEASING.md step 4: a git install pins its commit; an install with no known commit pins the version's
    tag. A source checkout (PYTHONPATH=src or an editable install) has a commit: pin it, not a tag that
    may not exist yet."""

    def git(self, d, *args):
        return subprocess.run(["git", "-C", str(d), *args], capture_output=True, text=True, check=True,
                              env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                                   "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}).stdout.strip()

    def checkout(self, track=True):
        d = Path(tempfile.mkdtemp())
        self.git(d, "init", "-q")
        (d / "aec").mkdir()
        (d / "aec" / "__init__.py").write_text("")
        (d / "README").write_text("x")
        self.git(d, "add", "aec" if track else "README")
        self.git(d, "commit", "-qm", "c")
        return d, self.git(d, "rev-parse", "HEAD")

    def test_source_checkout_pins_its_commit(self):  # violating before the fix
        from aec.init import resolve_install_ref
        d, sha = self.checkout()
        ref, note = resolve_install_ref("0.5.0", None, d / "aec")
        self.assertEqual(ref, sha)
        self.assertIn("source checkout", note)

    def test_untracked_package_inside_a_repo_is_not_a_checkout(self):  # decoy: e.g. a venv in a user's repo
        from aec.init import resolve_install_ref
        d, _ = self.checkout(track=False)
        self.assertEqual(resolve_install_ref("0.5.0", None, d / "aec"), ("v0.5.0", None))

    def test_non_git_install_keeps_the_tag_rule(self):  # decoy: #51's tested rule for non-git installs
        from aec.init import resolve_install_ref
        self.assertEqual(resolve_install_ref("0.5.0", None, Path(tempfile.mkdtemp())), ("v0.5.0", None))

    def test_git_install_commit_wins(self):  # decoy: a pip git install's recorded commit still comes first
        from aec.init import resolve_install_ref
        d, _ = self.checkout()
        sha = "0123456789abcdef0123456789abcdef01234567"
        self.assertEqual(resolve_install_ref("0.5.0", sha, d / "aec"), (sha, None))

    def test_init_from_this_checkout_pins_head(self):
        """End to end, the way the docs builder ran it: `python -m aec init` with PYTHONPATH=src."""
        try:
            head = self.git(ROOT, "rev-parse", "HEAD")
            self.git(ROOT, "ls-files", "--error-unmatch", "src/aec/__init__.py")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.skipTest("not running from a git checkout")
        d = Path(tempfile.mkdtemp())
        r = subprocess.run([sys.executable, "-m", "aec", "init", str(d), "--owner", "t"], capture_output=True,
                           text=True, env={**os.environ, "PYTHONPATH": str(ROOT / "src")})
        self.assertEqual(r.returncode, 0, r.stderr)
        ci = (d / ".aec" / "snippets" / "aec-ci.yml").read_text()
        self.assertIn(f"Telosmith.git@{head}\"", ci)
        self.assertNotIn("@v0.5.0\"", ci)
        self.assertIn("source checkout", r.stdout)
