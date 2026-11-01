"""T1 functionality: profile_dataset() computes dataset-level numbers only (no per-column plots)."""
import matplotlib
matplotlib.use("Agg")

import pandas as pd

from data_profiler import DataProfiler


def _df():
    return pd.DataFrame({
        "amount": [1.0, 2.5, 3.0, 4.5, 100.0, None],
        "label": ["a", "b", "a", "c", "a", "b"],
        "when": pd.date_range("2024-01-01", periods=6, freq="7D"),
    })


def test_profile_dataset_returns_dataset_level_results(tmp_path):
    p = DataProfiler(_df(), output_dir=str(tmp_path))
    res = p.profile_dataset()
    assert res["metadata"]["row_count"] == 6
    assert res["metadata"]["column_count"] == 3
    assert res["metadata"]["missing_values"] == 1
    assert set(res["column_types"]) == {"amount", "label", "when"}


def test_profile_dataset_does_not_render_column_plots(tmp_path):
    p = DataProfiler(_df(), output_dir=str(tmp_path))
    p.profile_dataset()
    pngs = sorted(x.name for x in tmp_path.rglob("*.png"))
    assert pngs == [], f"profile_dataset() still renders plots: {pngs}"
    assert not p.results.get("numeric_profiles")
    assert not p.results.get("string_profiles")
