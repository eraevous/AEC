"""Parallel coordinates rendering for readmission analysis."""

from __future__ import annotations

from typing import Sequence

import pandas as pd
import plotly.graph_objects as go

from viz.shared import theme


def _scale_columns(frame: pd.DataFrame, cols: Sequence[str], scaling: str) -> pd.DataFrame:
    scaled = frame.copy()
    if scaling == "raw":
        return scaled
    if scaling == "zscore":
        for col in cols:
            series = scaled[col].astype(float)
            scaled[col] = (series - series.mean()) / (series.std(ddof=0) or 1)
        return scaled
    if scaling == "rank":
        for col in cols:
            scaled[col] = scaled[col].rank(method="average", pct=True)
        return scaled
    raise ValueError(f"Unsupported scaling '{scaling}'")


def build_parallel_coordinates(
    df: pd.DataFrame,
    cols: Sequence[str],
    diagnosis_col: str = "Primary_Diagnosis",
    readmit_col: str = "Has_Readmission_30_Days",
    top_k_diag: int = 6,
    scaling: str = "raw",
) -> go.Figure:
    """Render an interactive parallel coordinates figure."""

    if len(cols) < 2:
        raise ValueError("Parallel coordinates require at least two numeric columns")

    required = set(cols) | {readmit_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataframe missing required columns: {sorted(missing)}")

    working = df[list(required)].dropna().copy()
    if diagnosis_col in df:
        diagnoses = df[diagnosis_col].fillna("Unknown")
        top = diagnoses.value_counts().nlargest(top_k_diag).index
        working[diagnosis_col] = diagnoses.where(diagnoses.isin(top), other="Other")
    else:
        working[diagnosis_col] = "All"

    scaled = _scale_columns(working, cols, scaling)
    readmit = working[readmit_col].astype(int)
    palette = theme.readmit_palette(readmit.unique())

    diag_categorical = pd.Categorical(working[diagnosis_col])
    diag_codes = diag_categorical.codes

    dimensions = []
    for col in cols:
        values = scaled[col].astype(float)
        dim = {
            "label": col,
            "values": values,
            "range": [float(values.min()), float(values.max())],
        }
        if scaling == "rank":
            dim["tickvals"] = [0.0, 0.5, 1.0]
            dim["ticktext"] = ["0%", "50%", "100%"]
        dimensions.append(dim)

    dimensions.append(
        {
            "label": diagnosis_col,
            "values": diag_codes,
            "tickvals": list(range(len(diag_categorical.categories))),
            "ticktext": [str(c) for c in diag_categorical.categories],
        }
    )

    colorscale = [[0.0, palette.get(0, "#264653")], [1.0, palette.get(1, "#e76f51")]]
    fig = go.Figure(
        data=[
            go.Parcoords(
                line=dict(
                    color=readmit,
                    colorscale=colorscale,
                    cmin=0,
                    cmax=1,
                    showscale=True,
                    colorbar=dict(title="Readmission"),
                ),
                dimensions=dimensions,
                labelfont=dict(size=12),
            )
        ]
    )
    fig.update_layout(
        title=f"Parallel coordinates ({scaling})",
        margin=dict(l=60, r=40, t=80, b=40),
    )
    return fig


__all__ = ["build_parallel_coordinates"]
