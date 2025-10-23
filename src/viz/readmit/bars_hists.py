"""Bar and histogram visualizations split by readmission."""

from __future__ import annotations

import math
from typing import Dict, List, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from viz.shared import theme


def _ensure_boolean(series: pd.Series) -> pd.Series:
    if series.dropna().isin({0, 1}).all():
        return series.astype(int)
    if series.dropna().isin({False, True}).all():
        return series.astype(int)
    return (series == series.max()).astype(int)


def build_bars_and_hists(
    df: pd.DataFrame,
    categoricals: Sequence[str],
    numerics: Sequence[str],
    readmit_col: str = "Has_Readmission_30_Days",
    bins: int = 12,
) -> tuple[plt.Figure, pd.DataFrame]:
    """Build small-multiple bars/histograms grouped by readmission."""

    if readmit_col not in df:
        raise ValueError(f"Readmission column '{readmit_col}' missing from dataframe")

    theme.apply_base_theme()
    readmit = _ensure_boolean(df[readmit_col])
    palette = theme.readmit_palette(readmit.unique())
    base_rate = readmit.mean()

    panels = list(categoricals) + list(numerics)
    n_panels = max(len(panels), 1)
    ncols = min(2, n_panels)
    nrows = math.ceil(n_panels / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5.5, nrows * 4), squeeze=False)
    axes_iter = iter(axes.flatten())

    summary_records: List[Dict[str, object]] = []

    for col in categoricals:
        ax = next(axes_iter)
        sns.countplot(data=df, x=col, hue=readmit_col, ax=ax, palette=palette)
        ax.set_title(f"{col} by Readmission")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=30, ha="right")
        theme.annotate_base_rate(ax, base_rate)
        counts = (
            df.groupby([col, readmit_col])
            .size()
            .rename("count")
            .reset_index()
        )
        totals = counts.groupby(col)["count"].transform("sum")
        counts["rate"] = counts["count"] / totals
        for _, row in counts.iterrows():
            summary_records.append(
                {
                    "feature": col,
                    "bin": row[col],
                    "readmission": int(row[readmit_col]),
                    "count": int(row["count"]),
                    "rate": float(row["rate"]),
                }
            )

    for col in numerics:
        ax = next(axes_iter)
        sns.histplot(
            data=df,
            x=col,
            hue=readmit_col,
            ax=ax,
            kde=len(df) >= 50,
            stat="density",
            common_norm=False,
            bins=bins,
            palette=palette,
        )
        ax.set_title(f"{col} distribution")
        ax.set_ylabel("Density")
        theme.annotate_base_rate(ax, base_rate)
        binned = pd.cut(df[col], bins=bins)
        grouped = (
            df.assign(_bin=binned, _readmit=readmit)
            .groupby(["_bin", "_readmit"], dropna=False)
            .size()
            .rename("count")
            .reset_index()
        )
        totals = grouped.groupby("_bin")["count"].transform("sum")
        grouped["rate"] = grouped["count"] / totals.replace(0, np.nan)
        for _, row in grouped.iterrows():
            summary_records.append(
                {
                    "feature": col,
                    "bin": str(row["_bin"]),
                    "readmission": int(row["_readmit"]),
                    "count": int(row["count"]),
                    "rate": float(row["rate"]) if not pd.isna(row["rate"]) else np.nan,
                }
            )

    for ax in axes_iter:
        ax.axis("off")

    fig.tight_layout()
    summary = pd.DataFrame(summary_records)
    return fig, summary


__all__ = ["build_bars_and_hists"]
