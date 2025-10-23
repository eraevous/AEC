"""Bar and histogram visualizations split by readmission."""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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


def _top_diagnoses(
    df: pd.DataFrame, top_k: int, diagnosis_col: str
) -> Tuple[pd.DataFrame, Sequence[str]]:
    counts = df[diagnosis_col].fillna("Unknown").value_counts()
    order = counts.nlargest(top_k).index.tolist()
    if not order:
        return df.iloc[0:0].copy(), []
    filtered = df[df[diagnosis_col].isin(order)].copy()
    filtered[diagnosis_col] = pd.Categorical(
        filtered[diagnosis_col], categories=order, ordered=True
    )
    return filtered, order


def build_diagnosis_distribution_panels(
    df: pd.DataFrame,
    measure: str = "Age",
    top_k_diag: int = 6,
    readmit_col: str = "Has_Readmission_30_Days",
    diagnosis_col: str = "Primary_Diagnosis",
    gender_col: str = "Gender",
    bandwidth: float = 1.0,
) -> Tuple[Dict[str, plt.Figure], pd.DataFrame]:
    """Create ridgeline and boxplot panels by diagnosis and gender."""

    required = {measure, diagnosis_col, gender_col, readmit_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataframe missing required columns: {sorted(missing)}")

    theme.apply_base_theme(font_scale=0.9)
    readmit = _ensure_boolean(df[readmit_col])
    working = df.assign(**{readmit_col: readmit})
    filtered, diagnoses = _top_diagnoses(working, top_k_diag, diagnosis_col)
    if filtered.empty:
        summary_cols = [
            diagnosis_col,
            gender_col,
            "readmit",
            "count",
            "mean",
            "median",
            "q1",
            "q3",
        ]
        return {}, pd.DataFrame(columns=summary_cols)

    filtered = filtered.dropna(subset=[measure]).copy()
    filtered[gender_col] = filtered[gender_col].fillna("Unknown")
    filtered["_readmit"] = filtered[readmit_col].astype(int)

    genders = (
        filtered[gender_col]
        .value_counts()
        .index.tolist()
    )
    hue_order = sorted(filtered["_readmit"].unique())
    palette = theme.readmit_palette(hue_order)

    nrows = len(diagnoses)
    ncols = len(genders)
    figures: Dict[str, plt.Figure] = {}

    # Ridgeline -----------------------------------------------------------
    fig_ridge, axes_ridge = plt.subplots(
        max(nrows, 1),
        max(ncols, 1),
        figsize=(max(ncols, 1) * 4.0, max(nrows, 1) * 3.0),
        squeeze=False,
    )
    for row_idx, diag in enumerate(diagnoses):
        for col_idx, gender in enumerate(genders):
            ax = axes_ridge[row_idx, col_idx]
            panel = filtered[
                (filtered[diagnosis_col] == diag) & (filtered[gender_col] == gender)
            ]
            if panel.empty:
                ax.axis("off")
                continue
            for value in hue_order:
                segment = panel[panel["_readmit"] == value][measure].dropna()
                if segment.nunique() >= 2:
                    sns.kdeplot(
                        segment,
                        fill=True,
                        common_norm=False,
                        bw_adjust=bandwidth,
                        alpha=0.6,
                        linewidth=1.2,
                        color=palette[value],
                        ax=ax,
                    )
                elif not segment.empty:
                    ax.axvline(
                        float(segment.iloc[0]),
                        color=palette[value],
                        linestyle="--",
                        linewidth=1.2,
                    )
            if row_idx == nrows - 1:
                ax.set_xlabel(measure)
            else:
                ax.set_xlabel("")
            if col_idx == 0:
                ax.set_ylabel(str(diag))
            else:
                ax.set_ylabel("")
            if row_idx == 0:
                ax.set_title(str(gender))
            ax.grid(False)

    handles = [Line2D([0], [0], color=palette[val], lw=2) for val in hue_order]
    labels = [f"Readmit {val}" for val in hue_order]
    if handles:
        fig_ridge.legend(handles, labels, loc="upper center", ncol=len(handles))
    fig_ridge.tight_layout(rect=[0, 0, 1, 0.94])
    figures["ridgeline"] = fig_ridge

    # Boxplots -----------------------------------------------------------
    fig_box, axes_box = plt.subplots(
        max(nrows, 1),
        max(ncols, 1),
        figsize=(max(ncols, 1) * 4.0, max(nrows, 1) * 3.2),
        squeeze=False,
    )
    readmit_labels = {0: "No", 1: "Yes"}
    for row_idx, diag in enumerate(diagnoses):
        for col_idx, gender in enumerate(genders):
            ax = axes_box[row_idx, col_idx]
            panel = filtered[
                (filtered[diagnosis_col] == diag) & (filtered[gender_col] == gender)
            ]
            if panel.empty:
                ax.axis("off")
                continue
            sns.boxplot(
                data=panel,
                x="_readmit",
                y=measure,
                ax=ax,
                order=hue_order,
                palette=[palette[val] for val in hue_order],
                width=0.6,
            )
            sns.stripplot(
                data=panel,
                x="_readmit",
                y=measure,
                ax=ax,
                order=hue_order,
                palette=[palette[val] for val in hue_order],
                dodge=False,
                jitter=0.12,
                alpha=0.35,
                size=3,
            )
            ax.set_xticklabels([readmit_labels.get(val, str(val)) for val in hue_order])
            if row_idx == nrows - 1:
                ax.set_xlabel("Readmission")
            else:
                ax.set_xlabel("")
            if col_idx == 0:
                ax.set_ylabel(measure)
            else:
                ax.set_ylabel("")
            if row_idx == 0:
                ax.set_title(str(gender))

    fig_box.tight_layout()
    figures["box"] = fig_box

    summary = (
        filtered.groupby([diagnosis_col, gender_col, "_readmit"], dropna=False)[measure]
        .agg(
            count="count",
            mean="mean",
            median="median",
            q1=lambda x: x.quantile(0.25),
            q3=lambda x: x.quantile(0.75),
        )
        .reset_index()
        .rename(columns={"_readmit": "readmit"})
    )
    return figures, summary


__all__ = ["build_bars_and_hists", "build_diagnosis_distribution_panels"]
