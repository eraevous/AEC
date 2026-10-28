"""T029 / FR-009: the package installs into a clean venv and runs; only `aec` is shipped (T028)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipIf(os.environ.get("AEC_SKIP_INSTALL_TEST"), "install test disabled")
class TestInstall(unittest.TestCase):
    def test_pip_install_and_run(self):
        d = Path(tempfile.mkdtemp())
        subprocess.run([sys.executable, "-m", "venv", str(d / "v")], check=True)
        py = d / "v" / ("Scripts" if os.name == "nt" else "bin") / "python"
        r = subprocess.run([str(py), "-m", "pip", "install", "-q", str(ROOT)], capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        r = subprocess.run([str(py), "-m", "aec", "edges", str(ROOT / "tests" / "fixtures" / "edges_pkg_v1")],
                           capture_output=True, text=True, cwd=d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('"aec_edges": 1', r.stdout.splitlines()[0])
        r = subprocess.run([str(py), "-c", "import core"], capture_output=True, text=True, cwd=d)
        self.assertNotEqual(r.returncode, 0, "legacy top-level 'core' package must not be installed")


if __name__ == "__main__":
    unittest.main()
