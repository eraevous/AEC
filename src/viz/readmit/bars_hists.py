"""Bar and histogram visualizations split by readmission."""

from __future__ import annotations

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

    features = list(categoricals) + list(numerics)
    has_features = bool(features)
    nrows = max(len(features), 1)
    ncols = 2 if has_features else 1
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(ncols * 5.5, nrows * 4),
        squeeze=False,
    )

    summary_records: List[Dict[str, object]] = []
    hue_order = sorted(palette)
    palette_list = [palette[val] for val in hue_order]

    if not has_features:
        ax = axes[0, 0]
        ax.text(
            0.5,
            0.5,
            "No categorical or numeric columns provided.",
            ha="center",
            va="center",
            fontsize="large",
        )
        ax.axis("off")
    else:
        row_idx = 0
        for col in categoricals:
            clustered_ax, stacked_ax = axes[row_idx]
            sns.countplot(
                data=df,
                x=col,
                hue=readmit_col,
                hue_order=hue_order,
                ax=clustered_ax,
                palette=palette,
            )
            clustered_ax.set_title(f"{col} by Readmission (clustered)")
            clustered_ax.set_ylabel("Count")
            clustered_ax.tick_params(axis="x", rotation=30, ha="right")
            theme.annotate_base_rate(clustered_ax, base_rate)

            counts = (
                df.groupby([col, readmit_col])
                .size()
                .rename("count")
                .reset_index()
            )
            totals = counts.groupby(col)["count"].transform("sum")
            counts["rate"] = counts["count"] / totals.replace(0, np.nan)

            category_order = counts[col].drop_duplicates().tolist()
            stacked_data = (
                counts.pivot(index=col, columns=readmit_col, values="count")
                .fillna(0)
                .reindex(category_order)
            )
            stacked_data = stacked_data.reindex(columns=hue_order, fill_value=0)
            stacked_data.plot(
                kind="bar",
                stacked=True,
                ax=stacked_ax,
                color=palette_list,
            )
            stacked_ax.set_title(f"{col} by Readmission (stacked)")
            stacked_ax.set_ylabel("Count")
            stacked_ax.tick_params(axis="x", rotation=30, ha="right")
            stacked_ax.legend(title="Readmission", loc="upper right")
            theme.annotate_base_rate(stacked_ax, base_rate)

            for _, row in counts.iterrows():
                for viz_type in ("bar_clustered", "bar_stacked"):
                    summary_records.append(
                        {
                            "feature": col,
                            "bin": row[col],
                            "readmission": int(row[readmit_col]),
                            "count": int(row["count"]),
                            "rate": (
                                float(row["rate"])
                                if not pd.isna(row["rate"])
                                else np.nan
                            ),
                            "viz_type": viz_type,
                        }
                    )

            row_idx += 1

        for col in numerics:
            clustered_ax, stacked_ax = axes[row_idx]
            sns.histplot(
                data=df,
                x=col,
                hue=readmit_col,
                hue_order=hue_order,
                ax=clustered_ax,
                kde=len(df) >= 50,
                stat="density",
                common_norm=False,
                bins=bins,
                palette=palette,
            )
            clustered_ax.set_title(f"{col} distribution (overlaid)")
            clustered_ax.set_ylabel("Density")
            theme.annotate_base_rate(clustered_ax, base_rate)

            sns.histplot(
                data=df,
                x=col,
                hue=readmit_col,
                hue_order=hue_order,
                multiple="stack",
                ax=stacked_ax,
                stat="count",
                bins=bins,
                palette=palette,
            )
            stacked_ax.set_title(f"{col} distribution (stacked)")
            stacked_ax.set_ylabel("Count")
            theme.annotate_base_rate(stacked_ax, base_rate)

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
                for viz_type in ("hist_overlaid", "hist_stacked"):
                    summary_records.append(
                        {
                            "feature": col,
                            "bin": str(row["_bin"]),
                            "readmission": int(row["_readmit"]),
                            "count": int(row["count"]),
                            "rate": (
                                float(row["rate"])
                                if not pd.isna(row["rate"])
                                else np.nan
                            ),
                            "viz_type": viz_type,
                        }
                    )

            row_idx += 1

    fig.tight_layout()
    summary_columns = ["feature", "bin", "readmission", "count", "rate", "viz_type"]
    summary = (
        pd.DataFrame(summary_records)
        if summary_records
        else pd.DataFrame(columns=summary_columns)
    )
    return fig, summary


__all__ = ["build_bars_and_hists"]
