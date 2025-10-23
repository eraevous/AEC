"""Three-by-three corrgram comparing numeric features against readmission."""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.metrics import roc_auc_score

from viz.shared import theme


def _ensure_three(numerics: Sequence[str]) -> Tuple[str, str, str]:
    if len(numerics) != 3:
        raise ValueError("corrgram requires exactly three numeric columns")
    return tuple(numerics)  # type: ignore[return-value]


def _ensure_boolean(series: pd.Series) -> pd.Series:
    if series.dropna().isin({0, 1}).all():
        return series.astype(int)
    if series.dropna().isin({False, True}).all():
        return series.astype(int)
    return (series == series.max()).astype(int)


def _pair_metrics(x: pd.Series, y: pd.Series) -> Dict[str, float]:
    metrics: Dict[str, float] = {}
    if x.nunique() <= 1 or y.nunique() <= 1:
        return {"pearson": float("nan"), "spearman": float("nan"), "kendall": float("nan")}
    pearson, _ = stats.pearsonr(x, y)
    spearman, _ = stats.spearmanr(x, y)
    kendall, _ = stats.kendalltau(x, y)
    metrics.update({"pearson": float(pearson), "spearman": float(spearman), "kendall": float(kendall)})
    return metrics


def _readmission_metrics(feature: pd.Series, readmit: pd.Series) -> Dict[str, float]:
    metrics: Dict[str, float] = {"pointbiserial": float("nan"), "auc": float("nan")}
    if feature.nunique() <= 1:
        return metrics
    try:
        r, _ = stats.pointbiserialr(readmit, feature)
        metrics["pointbiserial"] = float(r)
    except Exception:  # pragma: no cover - scipy may raise
        pass
    try:
        metrics["auc"] = float(roc_auc_score(readmit, feature))
    except Exception:  # pragma: no cover - degenerate label distribution
        pass
    return metrics


def build_corrgram(
    df: pd.DataFrame,
    numerics: Sequence[str],
    readmit_col: str = "Has_Readmission_30_Days",
    sample: int | None = None,
) -> tuple[plt.Figure, pd.DataFrame]:
    """Produce a 3×3 corrgram contrasting numeric features and readmission."""

    if readmit_col not in df:
        raise ValueError(f"Readmission column '{readmit_col}' missing from dataframe")

    cols = _ensure_three(numerics)
    working = df[list(cols) + [readmit_col]].dropna()
    if sample is not None and len(working) > sample:
        working = working.sample(sample, random_state=42)

    readmit = _ensure_boolean(working[readmit_col])
    palette = theme.readmit_palette(readmit.unique())
    base_rate = readmit.mean()

    theme.apply_base_theme(font_scale=0.9)
    fig, axes = plt.subplots(3, 3, figsize=(12, 12))

    metrics_rows: List[Dict[str, object]] = []

    for i, row_col in enumerate(cols):
        for j, col_col in enumerate(cols):
            ax = axes[i, j]
            if i == j:
                sns.kdeplot(
                    data=working,
                    x=row_col,
                    hue=readmit_col,
                    ax=ax,
                    fill=True,
                    common_norm=False,
                    warn_singular=False,
                    palette=palette,
                )
                ax.set_ylabel("Density")
                readmit_metrics = _readmission_metrics(working[row_col], readmit)
                ax.text(
                    0.02,
                    0.88,
                    f"r_pb={readmit_metrics['pointbiserial']:.2f}\nAUC={readmit_metrics['auc']:.2f}",
                    transform=ax.transAxes,
                    ha="left",
                    va="top",
                )
                metrics_rows.append(
                    {
                        "pair": f"{row_col}|{readmit_col}",
                        "metric": "pointbiserial",
                        "value": readmit_metrics["pointbiserial"],
                    }
                )
                metrics_rows.append(
                    {
                        "pair": f"{row_col}|{readmit_col}",
                        "metric": "auc",
                        "value": readmit_metrics["auc"],
                    }
                )
            elif i > j:
                sns.scatterplot(
                    data=working,
                    x=col_col,
                    y=row_col,
                    hue=readmit_col,
                    palette=palette,
                    ax=ax,
                    alpha=0.6,
                    edgecolor="none",
                )
                ax.set_xlabel(col_col)
                ax.set_ylabel(row_col)
                theme.annotate_base_rate(ax, base_rate)
            else:
                ax.axis("off")
                pair = (cols[j], cols[i])
                pair_metrics = _pair_metrics(working[pair[0]], working[pair[1]])
                metrics_rows.extend(
                    {
                        "pair": f"{pair[0]}|{pair[1]}",
                        "metric": metric,
                        "value": value,
                    }
                    for metric, value in pair_metrics.items()
                )
                text = "\n".join(f"{m}: {v:.2f}" for m, v in pair_metrics.items())
                ax.text(0.5, 0.5, text, ha="center", va="center", transform=ax.transAxes)

    for ax in axes.flat:
        if not ax.has_data():
            ax.axis("off")

    fig.suptitle("Readmission corrgram", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    metrics_df = pd.DataFrame(metrics_rows)
    return fig, metrics_df


__all__ = ["build_corrgram"]
