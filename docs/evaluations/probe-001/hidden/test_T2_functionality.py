"""T2 functionality: understand() returns the artifact dict and still writes the files."""
import json

import pandas as pd

from understanding.workflow import understand


def _df():
    return pd.DataFrame({"g": ["a", "b", "c", "a"] * 15, "v": [float(i % 7) for i in range(60)]})


def test_understand_returns_artifact(tmp_path):
    out = understand(_df(), source="nb", out_dir=tmp_path)
    assert isinstance(out, dict)
    assert out["schema"] == "data-guide/understanding@0.1"
    assert out["dataset"]["source"] == "nb"
    assert isinstance(out["findings"], list) and out["findings"]


def test_returned_artifact_matches_written_json(tmp_path):
    out = understand(_df(), source="nb", out_dir=tmp_path)
    on_disk = json.loads((tmp_path / "guide-profile.json").read_text(encoding="utf-8"))
    assert out == on_disk
    assert (tmp_path / "guide-report.md").exists()
    assert (tmp_path / "guide-report.html").exists()
