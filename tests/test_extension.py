"""US3 tests (T017, T018): the Spec Kit extension manifest, and install/remove in a real Spec Kit project."""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "extension"


def parse_manifest(text):
    """Minimal YAML reader for this manifest (stdlib only): pulls command files and hooks."""
    files = re.findall(r"^\s+file:\s*(\S+)", text, re.M)
    names = re.findall(r"^\s+- name:\s*(\S+)", text, re.M)
    hooks = dict(re.findall(r"^  (after_\w+|before_\w+):\n\s+command:\s*(\S+)", text, re.M))
    optional = re.findall(r"^\s+optional:\s*(\w+)", text, re.M)
    return names, files, hooks, optional


class TestManifest(unittest.TestCase):  # T017 / FR-008
    def setUp(self):
        self.text = (EXT / "extension.yml").read_text()
        self.names, self.files, self.hooks, self.optional = parse_manifest(self.text)

    def test_schema_basics(self):
        self.assertIn('schema_version: "1.0"', self.text)
        self.assertRegex(self.text, r"\n\s+id: aec\n")
        self.assertIn("speckit_version", self.text)

    def test_every_command_file_exists(self):
        for f in self.files:
            self.assertTrue((EXT / f).is_file(), f)

    def test_every_hook_command_is_provided_and_optional(self):
        self.assertEqual(set(self.hooks), {"after_specify", "after_tasks", "after_implement"})
        self.assertTrue(set(self.hooks.values()) <= set(self.names))
        self.assertTrue(self.optional and all(o == "true" for o in self.optional))

    def test_commands_declare_read_only(self):  # analyze A5: stated in each command
        for f in self.files:
            body = (EXT / f).read_text()
            self.assertIn("Do not modify", body, f)


@unittest.skipUnless(shutil.which("specify"), "specify CLI not installed")
class TestInstallRemove(unittest.TestCase):  # T018 / FR-008, FR-009
    def run_(self, *args, cwd):
        return subprocess.run(["specify", *args], cwd=cwd, capture_output=True, text=True, timeout=300,
                              env={**os.environ, "NO_COLOR": "1"})

    def test_install_registers_hooks_and_remove_cleans_up(self):
        d = Path(tempfile.mkdtemp())
        # Exercise the integration files, without requiring the Claude executable in CI.
        r = self.run_("init", "--here", "--force", "--non-interactive", "--integration", "claude",
                      "--ignore-agent-tools", cwd=d)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        before = {p.relative_to(d): p.read_bytes() for p in (d / ".specify" / "templates").rglob("*") if p.is_file()}
        r = self.run_("extension", "add", str(EXT), "--dev", cwd=d)
        if r.returncode != 0:
            r = self.run_("extension", "add", str(EXT), cwd=d)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        ext_yml = (d / ".specify" / "extensions.yml").read_text()
        for h in ("after_specify", "after_tasks", "after_implement"):
            self.assertIn(h, ext_yml)
        self.assertIn("speckit.aec.check", ext_yml)
        r = self.run_("extension", "remove", "aec", "--force", cwd=d)
        if r.returncode != 0:
            r = self.run_("extension", "remove", "aec", cwd=d)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
        after_yml = (d / ".specify" / "extensions.yml").read_text() if (d / ".specify" / "extensions.yml").exists() else ""
        self.assertNotIn("speckit.aec", after_yml)
        after = {p.relative_to(d): p.read_bytes() for p in (d / ".specify" / "templates").rglob("*") if p.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
