"""T1 preservation: the univariate profiler and the CLI `profile` report still carry per-column profiles."""
import matplotlib
matplotlib.use("Agg")

from pathlib import Path

import pandas as pd
from typer.testing import CliRunner

from cli import app
from core.models import GuideDataFrame, SchemaContract
from profilers.univariate import profile

FIXTURE = Path(__file__).parent / "fixtures" / "sample.csv"


def _gdf():
    df = pd.DataFrame({
        "patient_id": ["P1", "P2", "P3", "P4"],
        "value": [150.0, 3.0, 0.0, 1.0],
        "region": ["North", "South", "North", "East"],
    })
    return GuideDataFrame(df=df, schema=SchemaContract(), source_type="csv", origin="mem")


def test_univariate_profile_still_has_column_profiles(tmp_path):
    res = profile(_gdf(), output_dir=str(tmp_path))
    assert res.dataset_stats["metadata"]["row_count"] == 4
    assert "value" in res.column_stats.get("numeric_profiles", {})
    assert res.column_stats["numeric_profiles"]["value"]["statistics"]["max"] == 150.0
    assert "region" in res.column_stats.get("string_profiles", {})


def test_univariate_profile_columns_only(tmp_path):
    res = profile(_gdf(), analyses=["columns"], output_dir=str(tmp_path))
    assert "value" in res.column_stats.get("numeric_profiles", {})


def test_cli_profile_report_contains_column_statistics(tmp_path):
    out = tmp_path / "report.html"
    r = CliRunner().invoke(app, ["profile", str(FIXTURE), "--output", str(out)])
    assert r.exit_code == 0, r.output
    html = out.read_text(encoding="utf-8")
    # The report's column section comes from the profiler's per-column results,
    # not the bare dtype/null fallback the renderer uses when none are present.
    assert "numeric_profiles" in html
    assert "skewness" in html
