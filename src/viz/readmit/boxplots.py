"""Box and violin plots with effect size overlays."""

from __future__ import annotations

import math
from typing import Dict, List, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from viz.shared import theme


def _cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    x = x.astype(float)
    y = y.astype(float)
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return float("nan")
    mean_diff = np.nanmean(y) - np.nanmean(x)
    pooled = np.sqrt(
        ((nx - 1) * np.nanvar(x, ddof=1) + (ny - 1) * np.nanvar(y, ddof=1)) / (nx + ny - 2)
    )
    if pooled == 0:
        return float("nan")
    return float(mean_diff / pooled)


def _mann_whitney_p(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) == 0 or len(y) == 0:
        return float("nan")
    try:
        return float(stats.mannwhitneyu(x, y, alternative="two-sided").pvalue)
    except ValueError:
        return float("nan")


def build_box_and_violin(
    df: pd.DataFrame,
    numerics: Sequence[str],
    readmit_col: str = "Has_Readmission_30_Days",
) -> tuple[plt.Figure, pd.DataFrame]:
    """Render violin+boxplots with effect sizes for numeric features."""

    if readmit_col not in df:
        raise ValueError(f"Readmission column '{readmit_col}' missing from dataframe")

    theme.apply_base_theme()
    palette = theme.readmit_palette(df[readmit_col].unique())
    n_panels = max(len(numerics), 1)
    ncols = min(2, n_panels)
    nrows = math.ceil(n_panels / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5.5, nrows * 4.5), squeeze=False)
    axes_iter = iter(axes.flatten())

    stats_rows: List[Dict[str, object]] = []
    readmit = df[readmit_col]
    base_rate = readmit.mean()

    for col in numerics:
        ax = next(axes_iter)
        sns.violinplot(
            data=df,
            x=readmit_col,
            y=col,
            ax=ax,
            palette=palette,
            cut=0,
            inner=None,
        )
        sns.boxplot(
            data=df,
            x=readmit_col,
            y=col,
            ax=ax,
            width=0.2,
            showcaps=True,
            boxprops={"facecolor": "white", "zorder": 3},
            showfliers=False,
        )
        ax.set_title(f"{col} vs Readmission")
        ax.set_xlabel("Readmission")
        theme.annotate_base_rate(ax, base_rate)

        group0 = df.loc[readmit == 0, col].dropna().to_numpy()
        group1 = df.loc[readmit == 1, col].dropna().to_numpy()
        cohens = _cohens_d(group0, group1)
        p_value = _mann_whitney_p(group0, group1)
        annotation = f"d={cohens:.2f}\np={p_value:.3f}"
        ax.text(0.95, 0.95, annotation, transform=ax.transAxes, ha="right", va="top")

        stats_rows.append(
            {
                "feature": col,
                "n0": int(len(group0)),
                "n1": int(len(group1)),
                "mean0": float(np.nanmean(group0)) if group0.size else np.nan,
                "mean1": float(np.nanmean(group1)) if group1.size else np.nan,
                "cohens_d": cohens,
                "mannwhitney_p": p_value,
            }
        )

    for ax in axes_iter:
        ax.axis("off")

    fig.tight_layout()
    stats_df = pd.DataFrame(stats_rows)
    return fig, stats_df


__all__ = ["build_box_and_violin"]
