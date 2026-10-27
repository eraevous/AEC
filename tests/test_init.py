"""Feature 002 US1 (T007): `aec init` scaffolds AEC into any repository without overwriting."""
import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
FIX = Path(__file__).resolve().parent / "fixtures"
from aec import edges as E  # noqa: E402
from aec.init import init  # noqa: E402
from aec.records import Store, check  # noqa: E402


def fresh_repo():
    d = Path(tempfile.mkdtemp()) / "repo"
    shutil.copytree(FIX / "purpose_repo", d)
    return d


class TestInit(unittest.TestCase):
    def test_plain_repo_gets_working_setup(self):  # US1-1, FR-001
        d = fresh_repo()
        rep = init(d, owner="Zach")
        for f in ("records.jsonl", "edges.jsonl", "README.md", "snippets/claude-settings.json", "snippets/aec-ci.yml"):
            self.assertTrue((d / ".aec" / f).is_file(), f)
            self.assertIn(f".aec/{f}", rep["created"])
        st = Store.load(d / ".aec" / "records.jsonl")
        errors = [x for x in check(st, edges=E.load(d / ".aec" / "edges.jsonl")) if x.level == "error"]
        self.assertEqual(errors, [])
        auth = [r for r in st.records if r.type == "authority"]
        self.assertEqual(len(auth), 1)
        self.assertIn("Zach", auth[0].text)
        purpose = [r for r in st.records if r.type == "purpose"]
        self.assertEqual(purpose[0].get("epistemic"), "provisional")  # a stub never authorizes anything

    def test_second_run_overwrites_nothing(self):  # US1-2
        d = fresh_repo()
        init(d, owner="Zach")
        (d / ".aec" / "records.jsonl").write_text((d / ".aec" / "records.jsonl").read_text() + "// edited\n")
        before = {p: p.read_bytes() for p in (d / ".aec").rglob("*") if p.is_file()}
        rep = init(d, owner="Someone else")
        after = {p: p.read_bytes() for p in (d / ".aec").rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(rep["created"], [])
        self.assertIn(".aec/records.jsonl", rep["kept"])

    def test_spec_kit_repo_gets_instructions_not_edits(self):  # US1-3, FR-002
        d = fresh_repo()
        (d / ".specify").mkdir()
        (d / ".specify" / "init-options.json").write_text("{}")
        before = (d / ".specify" / "init-options.json").read_bytes()
        rep = init(d, owner="Zach")
        self.assertTrue(rep["spec_kit"])
        self.assertIn("specify extension add", rep["next_steps"])
        self.assertEqual(sorted(p.name for p in (d / ".specify").iterdir()), ["init-options.json"])
        self.assertEqual((d / ".specify" / "init-options.json").read_bytes(), before)

    def test_cli(self):
        from aec.__main__ import main
        d = fresh_repo()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["init", str(d), "--owner", "Zach"])
        self.assertEqual(rc, 0)
        self.assertIn("created", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
