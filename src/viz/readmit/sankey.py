"""Sankey diagram representing patient journey toward readmission."""

from __future__ import annotations

from collections import defaultdict
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


def _hex_to_rgb(value: str) -> Tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
    return "#" + "".join(f"{int(round(component)):02x}" for component in rgb)


def _blend_readmit_palette(weight: float) -> str:
    weight = max(0.0, min(1.0, weight))
    low = theme.READMISSION_PALETTE[0]
    high = theme.READMISSION_PALETTE[1]
    low_rgb = _hex_to_rgb(low)
    high_rgb = _hex_to_rgb(high)
    blended = tuple(
        (1 - weight) * low_component + weight * high_component
        for low_component, high_component in zip(low_rgb, high_rgb)
    )
    return _rgb_to_hex(blended)


def _resolve_readmit_flag(value: object) -> int:
    if pd.isna(value):
        return 0
    if isinstance(value, (bool, int)):
        return int(bool(value))
    if isinstance(value, float):
        return int(value > 0)
    text = str(value).strip().lower()
    if text in {"1", "true", "t", "y", "yes"}:
        return 1
    if "yes" in text:
        return 1
    return 0


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
    grouped["readmit_flag"] = grouped[stages[-1]].apply(_resolve_readmit_flag)

    node_labels: List[str] = []
    node_colors: List[str] = []
    node_stage: List[str] = []
    node_rates: List[float] = []
    node_index: Dict[Tuple[int, str], int] = {}
    node_stats: Dict[Tuple[int, str], Dict[str, float]] = defaultdict(lambda: {"total": 0.0, "readmit": 0.0})

    for _, row in grouped.iterrows():
        count = float(row["count"])
        flag = int(row["readmit_flag"])
        for stage_idx, stage in enumerate(stages):
            label = row[stage]
            stats = node_stats[(stage_idx, label)]
            stats["total"] += count
            stats["readmit"] += count * flag

    for stage_idx, stage in enumerate(stages):
        labels = grouped[stage].unique()
        for label in labels:
            key = (stage_idx, label)
            if key in node_index:
                continue
            node_index[key] = len(node_labels)
            node_labels.append(label)
            stats = node_stats.get(key, {"total": 0.0, "readmit": 0.0})
            total = stats["total"]
            rate = stats["readmit"] / total if total else 0.0
            if stage == "Readmission":
                color = theme.READMISSION_PALETTE.get(1 if "yes" in str(label).lower() else 0)
            else:
                base_color = palette.get(label)
                color = base_color or _blend_readmit_palette(rate)
            node_colors.append(color)
            node_stage.append(stage)
            node_rates.append(rate)

    sources: List[int] = []
    targets: List[int] = []
    values: List[float] = []
    link_colors: List[str] = []
    link_readmit: List[int] = []

    for _, row in grouped.iterrows():
        path = [row[stage] for stage in stages]
        count = float(row["count"])
        flag = int(row["readmit_flag"])
        color = theme.READMISSION_PALETTE.get(flag, theme.READMISSION_PALETTE[0])
        for stage_idx in range(len(stages) - 1):
            source_key = (stage_idx, path[stage_idx])
            target_key = (stage_idx + 1, path[stage_idx + 1])
            sources.append(node_index[source_key])
            targets.append(node_index[target_key])
            values.append(count)
            link_colors.append(color)
            link_readmit.append(flag)

    nodes_df = pd.DataFrame(
        {
            "id": range(len(node_labels)),
            "label": node_labels,
            "stage": node_stage,
            "color": node_colors,
            "readmit_rate": node_rates,
        }
    )
    links_df = pd.DataFrame(
        {
            "source": sources,
            "target": targets,
            "value": values,
            "color": link_colors,
            "readmit_flag": link_readmit,
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
