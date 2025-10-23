"""Parallel coordinates rendering for readmission analysis."""

from __future__ import annotations

from typing import Dict, Mapping, Sequence

import pandas as pd
import plotly.graph_objects as go
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from viz.shared import theme


def _scale_columns(
    frame: pd.DataFrame, cols: Sequence[str], scaling: str
) -> pd.DataFrame:
    scaled = frame.copy()
    numeric_cols = [col for col in cols if is_numeric_dtype(frame[col])]
    if scaling == "raw" or not numeric_cols:
        return scaled
    if scaling == "zscore":
        for col in numeric_cols:
            series = scaled[col].astype(float)
            scaled[col] = (series - series.mean()) / (series.std(ddof=0) or 1)
        return scaled
    if scaling == "rank":
        for col in numeric_cols:
            scaled[col] = scaled[col].rank(method="average", pct=True)
        return scaled
    raise ValueError(f"Unsupported scaling '{scaling}'")


def _categorical_dimension(series: pd.Series, label: str) -> Dict[str, object]:
    prepared = series
    if is_bool_dtype(series):
        prepared = series.map({True: "Yes", False: "No"})
    categorical = pd.Categorical(prepared.fillna("Unknown"))
    return {
        "label": label,
        "values": categorical.codes,
        "tickvals": list(range(len(categorical.categories))),
        "ticktext": [str(cat) for cat in categorical.categories],
    }


def _numeric_dimension(
    original: pd.Series, scaled: pd.Series, label: str, scaling: str
) -> Dict[str, object]:
    values = scaled.astype(float)
    dim: Dict[str, object] = {
        "label": label,
        "values": values,
        "range": [float(values.min()), float(values.max())],
    }
    if scaling == "rank":
        dim["tickvals"] = [0.0, 0.5, 1.0]
        dim["ticktext"] = ["0%", "50%", "100%"]
    elif scaling == "raw":
        uniques = pd.Series(original).dropna().unique()
        if len(uniques) <= 2 and all(val in (0, 1, True, False) for val in uniques):
            dim["tickvals"] = [0.0, 1.0]
            dim["ticktext"] = ["No", "Yes"]
    return dim


def _build_single_parallel_coords(
    df: pd.DataFrame,
    cols: Sequence[str],
    diagnosis_col: str,
    readmit_col: str,
    top_k_diag: int,
    scaling: str,
) -> go.Figure:
    if len(cols) < 2:
        raise ValueError("Parallel coordinates require at least two columns")

    required = set(cols) | {readmit_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataframe missing required columns: {sorted(missing)}")

    subset = list(required)
    if diagnosis_col in df.columns and diagnosis_col not in subset:
        subset.append(diagnosis_col)

    working = df[subset].dropna(subset=list(required)).copy()
    if diagnosis_col in df.columns:
        diagnoses = df[diagnosis_col].fillna("Unknown")
        top = diagnoses.value_counts().nlargest(top_k_diag).index
        working[diagnosis_col] = diagnoses.where(diagnoses.isin(top), other="Other")
    else:
        working[diagnosis_col] = "All"

    scaled = _scale_columns(working, cols, scaling)
    readmit = working[readmit_col].astype(int)
    palette = theme.readmit_palette(readmit.unique())

    dimensions = []
    for col in cols:
        series = working[col]
        if is_numeric_dtype(series) and not is_bool_dtype(series):
            dim = _numeric_dimension(series, scaled[col], col, scaling)
        else:
            dim = _categorical_dimension(series, col)
        dimensions.append(dim)

    if diagnosis_col not in cols:
        dimensions.append(_categorical_dimension(working[diagnosis_col], diagnosis_col))

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


def build_parallel_coordinates(
    df: pd.DataFrame,
    cols: Sequence[str] | None = None,
    *,
    groups: Mapping[str, Sequence[str]] | None = None,
    diagnosis_col: str = "Primary_Diagnosis",
    readmit_col: str = "Has_Readmission_30_Days",
    top_k_diag: int = 6,
    scaling: str = "raw",
) -> Dict[str, go.Figure]:
    """Render one or more interactive parallel coordinates figures."""

    if groups:
        figures: Dict[str, go.Figure] = {}
        for label, group_cols in groups.items():
            if len(group_cols) < 2:
                continue
            figures[label] = _build_single_parallel_coords(
                df,
                group_cols,
                diagnosis_col,
                readmit_col,
                top_k_diag,
                scaling,
            )
        if not figures:
            raise ValueError("No valid column groups supplied for parallel coordinates")
        return figures

    if not cols:
        raise ValueError("Columns must be provided when no groups are configured")

    return {
        "default": _build_single_parallel_coords(
            df,
            cols,
            diagnosis_col,
            readmit_col,
            top_k_diag,
            scaling,
        )
    }


__all__ = ["build_parallel_coordinates"]
