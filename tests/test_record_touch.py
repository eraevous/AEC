import importlib.util
import pathlib
import unittest

_p = pathlib.Path(__file__).resolve().parents[1] / "tools" / "record_touch.py"
_spec = importlib.util.spec_from_file_location("record_touch", _p)
rt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rt)


class RecordTouch(unittest.TestCase):
    def test_violation_src_change_without_record_or_reason(self):
        ok, msg = rt.evaluate(["src/aec/impact.py", "tests/test_x.py"], ["Fix a bug"])
        self.assertFalse(ok)
        self.assertIn("src/aec/impact.py", msg)

    def test_violation_trailer_without_reason(self):
        ok, _ = rt.evaluate(["src/aec/impact.py"], ["Fix\n\nAEC-Record: none\n"])
        self.assertFalse(ok)

    def test_decoy_records_appended(self):
        ok, _ = rt.evaluate(["src/aec/impact.py", ".aec/records.jsonl"], ["Fix"])
        self.assertTrue(ok)

    def test_decoy_no_src_change(self):
        ok, _ = rt.evaluate(["docs/architecture.md", "tests/test_x.py"], ["Docs"])
        self.assertTrue(ok)

    def test_decoy_trailer_with_reason(self):
        ok, msg = rt.evaluate(["src/aec/cli.py"], ["Rename flag\n\nAEC-Record: none - help text only\n"])
        self.assertTrue(ok)
        self.assertIn("help text only", msg)

    def test_src_prefix_is_exact(self):
        ok, _ = rt.evaluate(["docs/src/notes.md"], ["Docs"])
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
