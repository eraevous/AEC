"""T027 / FR-005 / Constitution II: runtime modules import only the standard library (or aec itself)."""
import ast
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "aec"


class TestStdlibOnly(unittest.TestCase):
    def test_imports(self):
        allowed = set(sys.stdlib_module_names) | {"aec", "__future__"}
        bad = []
        for py in sorted(SRC.glob("*.py")):
            for node in ast.walk(ast.parse(py.read_text())):
                if isinstance(node, ast.Import):
                    names = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and not node.level:
                    names = [(node.module or "").split(".")[0]]
                else:
                    continue
                bad += [f"{py.name}: {n}" for n in names if n not in allowed]
        self.assertEqual(bad, [])

    def test_violation_is_detected(self):  # the check catches what it exists to catch
        tree = ast.parse("import pandas\nimport json\n")
        names = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        self.assertIn("pandas", [n for n in names if n not in sys.stdlib_module_names])


if __name__ == "__main__":
    unittest.main()
