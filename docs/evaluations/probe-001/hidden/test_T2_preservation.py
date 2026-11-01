"""T2 preservation: the CLI `understand` and `demo` commands still tell the user which files they wrote."""
import pandas as pd
from typer.testing import CliRunner

from cli import app

runner = CliRunner()


def test_cli_understand_reports_written_paths(tmp_path):
    src = tmp_path / "t.csv"
    pd.DataFrame({"g": ["a", "b", "c", "a"] * 15, "v": [float(i % 7) for i in range(60)]}).to_csv(src, index=False)
    out = tmp_path / "out"
    r = runner.invoke(app, ["understand", str(src), "--out", str(out)])
    assert r.exit_code == 0, r.output
    for name in ("guide-profile.json", "guide-report.md", "guide-report.html"):
        assert (out / name).exists()
        assert str(out / name) in r.output, f"{name} path not reported:\n{r.output[:500]}"


def test_cli_demo_reports_written_paths(tmp_path):
    out = tmp_path / "demo"
    r = runner.invoke(app, ["demo", "--out", str(out)])
    assert r.exit_code == 0, r.output
    for name in ("guide-profile.json", "guide-report.md", "guide-report.html"):
        assert str(out / name) in r.output, f"{name} path not reported:\n{r.output[:500]}"
