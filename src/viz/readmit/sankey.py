"""Sankey diagram representing patient journey toward readmission."""

from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd
import plotly.graph_objects as go

from viz.shared import theme


REQUIRED_COLUMNS = [
    "Prior_Admission",
    "Primary_Diagnosis",
    "Discharge_Status",
    "Has_Readmission_30_Days",
]


def _compress_categories(series: pd.Series, top_k: int, min_count: int) -> pd.Series:
    counts = series.value_counts(dropna=False)
    top = counts.nlargest(top_k).index
    mask = series.isin(top) | series.isin(counts[counts >= min_count].index)
    return series.where(mask, other="Other")


def _normalize_prior(series: pd.Series) -> pd.Series:
    clean = series.fillna(0)
    if clean.dropna().isin({0, 1, False, True}).all():
        return clean.astype(int).map({0: "Prior: No", 1: "Prior: Yes"})
    return clean.astype(str)


def _normalize_readmit(series: pd.Series) -> pd.Series:
    clean = series.fillna(0)
    if clean.dropna().isin({0, 1, False, True}).all():
        return clean.astype(int).map({0: "Readmit: No", 1: "Readmit: Yes"})
    return clean.astype(str)


def _palette_for_stage(stage: str) -> str:
    fallback = "#adb5bd"
    if stage.startswith("Prior"):
        return theme.ACCENT_PALETTE.get("diagnosis", fallback)
    if stage.startswith("Primary"):
        return "#577590"
    if stage.startswith("Discharge"):
        return "#f4a261"
    return fallback


def build_sankey(
    df: pd.DataFrame,
    top_k: int = 10,
    min_count: int = 25,
    palette: Dict[str, str] | None = None,
    readmit_col: str = "Has_Readmission_30_Days",
) -> Tuple[go.Figure, Dict[str, str], Dict[str, pd.DataFrame]]:
    """Build Sankey data for the readmission journey."""

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Dataframe missing required columns: {sorted(missing)}")

    palette = palette or {}
    prior = _normalize_prior(df["Prior_Admission"])
    diagnosis = _compress_categories(df["Primary_Diagnosis"].fillna("Unknown"), top_k, min_count)
    discharge = _compress_categories(df["Discharge_Status"].fillna("Unknown"), top_k, min_count)
    readmit = _normalize_readmit(df[readmit_col])

    stages = ["Prior Admission", "Primary Diagnosis", "Discharge Status", "Readmission"]
    labels_frame = pd.DataFrame(
        {
            stages[0]: prior,
            stages[1]: diagnosis.apply(lambda v: f"Diag: {v}"),
            stages[2]: discharge.apply(lambda v: f"Discharge: {v}"),
            stages[3]: readmit,
        }
    )
    grouped = labels_frame.value_counts().reset_index(name="count")

    node_labels: List[str] = []
    node_colors: List[str] = []
    node_stage: List[str] = []
    node_index: Dict[Tuple[int, str], int] = {}

    for stage_idx, stage in enumerate(stages):
        labels = grouped[stage].unique()
        for label in labels:
            key = (stage_idx, label)
            if key in node_index:
                continue
            node_index[key] = len(node_labels)
            node_labels.append(label)
            if stage == "Readmission":
                color = theme.READMISSION_PALETTE.get(1 if "Yes" in label else 0)
            else:
                color = palette.get(label, _palette_for_stage(stage))
            node_colors.append(color)
            node_stage.append(stage)

    sources: List[int] = []
    targets: List[int] = []
    values: List[float] = []
    link_colors: List[str] = []

    for _, row in grouped.iterrows():
        path = [row[stage] for stage in stages]
        count = float(row["count"])
        for stage_idx in range(len(stages) - 1):
            source_key = (stage_idx, path[stage_idx])
            target_key = (stage_idx + 1, path[stage_idx + 1])
            sources.append(node_index[source_key])
            targets.append(node_index[target_key])
            values.append(count)
            link_colors.append(node_colors[node_index[source_key]])

    nodes_df = pd.DataFrame(
        {
            "id": range(len(node_labels)),
            "label": node_labels,
            "stage": node_stage,
            "color": node_colors,
        }
    )
    links_df = pd.DataFrame(
        {
            "source": sources,
            "target": targets,
            "value": values,
            "color": link_colors,
        }
    )

    sankey = go.Sankey(
        node=dict(label=node_labels, color=node_colors, pad=18, thickness=16),
        link=dict(source=sources, target=targets, value=values, color=link_colors),
        arrangement="snap",
    )
    fig = go.Figure(data=[sankey])
    fig.update_layout(title="Patient flow toward 30-day readmission", margin=dict(l=40, r=40, t=60, b=40))

    return fig, {}, {"nodes": nodes_df, "links": links_df}


__all__ = ["build_sankey"]
