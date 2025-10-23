"""Small-multiple panels for diagnosis-level exploration."""

from __future__ import annotations

import math
from typing import Dict, Iterable, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import numpy as np
import pandas as pd
import seaborn as sns

from viz.shared import binning, theme

REQUIRED_COLUMNS = [
    "Primary_Diagnosis",
    "Length_of_Stay",
    "Distance_to_Closest_Hospital",
    "Num_Prior_Admissions_Last_6_Months",
    "Num_Comorbidities",
    "Discharge_Status",
    "Has_Readmission_30_Days",
]

COMORBIDITY_COLUMNS = [
    "Has_Hypertension",
    "Has_Diabetes",
    "Has_COPD",
    "Has_CHF",
]


def _ensure_boolean(series: pd.Series) -> pd.Series:
    if series.dropna().isin({0, 1}).all():
        return series.astype(int)
    if series.dropna().isin({False, True}).all():
        return series.astype(int)
    return (series == series.max()).astype(int)


def _top_diagnoses(
    df: pd.DataFrame, top_k: int, diagnosis_col: str = "Primary_Diagnosis"
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


def _setup_grid(n_items: int) -> Tuple[int, int]:
    ncols = min(3, max(1, n_items))
    nrows = math.ceil(max(1, n_items) / ncols)
    return nrows, ncols


def build_small_multiples(
    df: pd.DataFrame,
    top_k_diag: int = 9,
    bin_specs: Dict[str, Dict[str, object]] | None = None,
    readmit_col: str = "Has_Readmission_30_Days",
    diagnosis_col: str = "Primary_Diagnosis",
    gender_col: str = "Gender",
) -> Tuple[Dict[str, plt.Figure], Dict[str, pd.DataFrame]]:
    """Create bubble, heatmap, and mosaic small multiples by diagnosis."""

    missing = set(REQUIRED_COLUMNS + [diagnosis_col]) - set(df.columns)
    if missing:
        raise ValueError(f"Dataframe missing required columns: {sorted(missing)}")

    theme.apply_base_theme(font_scale=0.9)
    specs = binning.resolve_bin_specs(bin_specs)
    readmit = _ensure_boolean(df[readmit_col])
    df = df.assign(**{readmit_col: readmit})
    filtered, diagnoses = _top_diagnoses(df, top_k_diag, diagnosis_col=diagnosis_col)

    figures: Dict[str, plt.Figure] = {}
    tables: Dict[str, pd.DataFrame] = {}

    if filtered.empty:
        return figures, tables

    # ------------------------------------------------------------------
    # Rate heatmap (Age × Distance × Gender)
    age_heatmap = _build_age_distance_heatmap(
        filtered,
        diagnoses,
        specs.get("Distance_to_Closest_Hospital"),
        readmit_col=readmit_col,
        diagnosis_col=diagnosis_col,
        gender_col=gender_col,
    )
    if age_heatmap is not None:
        fig_age, summary_age = age_heatmap
        figures["age_distance_rate"] = fig_age
        tables["age_distance_rate"] = summary_age

    # Bubble chart ---------------------------------------------------------
    los_bins, los_info = binning.bin_series(
        filtered["Length_of_Stay"],
        **specs["Length_of_Stay"].to_kwargs(),
    )
    dist_bins, dist_info = binning.bin_series(
        filtered["Distance_to_Closest_Hospital"],
        **specs["Distance_to_Closest_Hospital"].to_kwargs(),
    )

    bubble_summary = (
        filtered.assign(_los=los_bins, _dist=dist_bins)
        .groupby([diagnosis_col, "_los", "_dist"], dropna=False)
        .agg(count=(readmit_col, "size"), rate=(readmit_col, "mean"))
        .reset_index()
    )
    tables["bubble"] = bubble_summary

    nrows, ncols = _setup_grid(len(diagnoses))
    fig_bubble, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4.5, nrows * 4.2), squeeze=False)
    vmax_count = bubble_summary["count"].max() or 1
    cmap = sns.color_palette("viridis", as_cmap=True)
    scatter = None
    for ax, diag in zip(axes.flatten(), diagnoses):
        diag_data = bubble_summary[bubble_summary[diagnosis_col] == diag]
        if diag_data.empty:
            ax.axis("off")
            continue
        x_codes = diag_data["_dist"].cat.codes
        y_codes = diag_data["_los"].cat.codes
        sizes = 200 * (diag_data["count"] / vmax_count) + 40
        scatter = ax.scatter(
            x_codes,
            y_codes,
            s=sizes,
            c=diag_data["rate"],
            cmap=cmap,
            vmin=0,
            vmax=1,
            edgecolor="none",
        )
        x_labels = dist_info["labels"] or diag_data["_dist"].cat.categories.astype(str).tolist()
        y_labels = los_info["labels"] or diag_data["_los"].cat.categories.astype(str).tolist()
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize="small")
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize="small")
        ax.set_xlabel("Distance")
        ax.set_ylabel("LOS")
        ax.set_title(str(diag))
    for ax in axes.flatten()[len(diagnoses):]:
        ax.axis("off")
    if scatter is not None:
        fig_bubble.colorbar(scatter, ax=axes, shrink=0.7, label="Readmission rate")
    figures["bubble"] = fig_bubble

    # Heatmap ---------------------------------------------------------------
    prior_bins, prior_info = binning.bin_series(
        filtered["Num_Prior_Admissions_Last_6_Months"],
        **specs["Num_Prior_Admissions_Last_6_Months"].to_kwargs(),
    )
    heatmap_summary = (
        filtered.assign(_prior=prior_bins)
        .groupby([diagnosis_col, "_prior", "Discharge_Status"], dropna=False)
        .agg(count=(readmit_col, "size"), rate=(readmit_col, "mean"))
        .reset_index()
    )
    tables["heatmap"] = heatmap_summary

    fig_heat, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4.5, nrows * 4.2), squeeze=False)
    heatmap_drawn = False
    for ax, diag in zip(axes.flatten(), diagnoses):
        diag_data = heatmap_summary[heatmap_summary[diagnosis_col] == diag]
        if diag_data.empty:
            ax.axis("off")
            continue
        pivot = diag_data.pivot(index="_prior", columns="Discharge_Status", values="rate")
        sns.heatmap(
            pivot,
            ax=ax,
            vmin=0,
            vmax=1,
            cmap="mako",
            cbar=False,
            annot=True,
            fmt=".2f",
        )
        ax.set_xlabel("Discharge")
        ax.set_ylabel("Prior Admissions")
        ax.set_title(str(diag))
        heatmap_drawn = True
    for ax in axes.flatten()[len(diagnoses):]:
        ax.axis("off")
    if heatmap_drawn:
        fig_heat.colorbar(plt.cm.ScalarMappable(cmap="mako", norm=mcolors.Normalize(0, 1)), ax=axes, shrink=0.7, label="Readmission rate")
    figures["heatmap"] = fig_heat

    # Mosaic (counts heatmap) ----------------------------------------------
    comorb_bins, comorb_info = binning.bin_series(
        filtered["Num_Comorbidities"],
        **specs["Num_Comorbidities"].to_kwargs(),
    )
    mosaic_summary = (
        filtered.assign(_comorb=comorb_bins)
        .groupby([diagnosis_col, "_comorb", "Discharge_Status"], dropna=False)
        .agg(count=(readmit_col, "size"), rate=(readmit_col, "mean"))
        .reset_index()
    )
    tables["mosaic"] = mosaic_summary

    fig_mosaic, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4.5, nrows * 4.2), squeeze=False)
    mosaic_drawn = False
    for ax, diag in zip(axes.flatten(), diagnoses):
        diag_data = mosaic_summary[mosaic_summary[diagnosis_col] == diag]
        if diag_data.empty:
            ax.axis("off")
            continue
        pivot = diag_data.pivot(index="_comorb", columns="Discharge_Status", values="count")
        sns.heatmap(
            pivot,
            ax=ax,
            cmap="Blues",
            cbar=False,
            annot=True,
            fmt=".0f",
        )
        ax.set_xlabel("Discharge")
        ax.set_ylabel("Comorbidities")
        ax.set_title(str(diag))
        mosaic_drawn = True
    for ax in axes.flatten()[len(diagnoses):]:
        ax.axis("off")
    if mosaic_drawn:
        fig_mosaic.colorbar(plt.cm.ScalarMappable(cmap="Blues"), ax=axes, shrink=0.7, label="Patient count")
    figures["mosaic"] = fig_mosaic

    # Bubble grid (Comorbidities × Prior Admissions) --------------------
    bubble_grid = _build_comorbidity_prior_bubble(
        filtered,
        diagnoses,
        prior_bins,
        comorb_bins,
        prior_info,
        comorb_info,
        readmit_col=readmit_col,
        diagnosis_col=diagnosis_col,
    )
    if bubble_grid is not None:
        fig_grid, summary_grid = bubble_grid
        figures["comorbidity_prior_bubble"] = fig_grid
        tables["comorbidity_prior_bubble"] = summary_grid

    # UpSet plot for comorbidities --------------------------------------
    upset_result = _build_comorbidity_upset(
        df,
        readmit_col=readmit_col,
        columns=COMORBIDITY_COLUMNS,
    )
    if upset_result is not None:
        fig_upset, table_upset = upset_result
        figures["comorbidity_upset"] = fig_upset
        tables["comorbidity_upset"] = table_upset

    return figures, tables


def _build_age_distance_heatmap(
    df: pd.DataFrame,
    diagnoses: Sequence[str],
    distance_spec: binning.BinSpec | None,
    readmit_col: str,
    diagnosis_col: str,
    gender_col: str,
    age_col: str = "Age",
    age_bins: int = 5,
) -> Tuple[plt.Figure, pd.DataFrame] | None:
    needed = {diagnosis_col, gender_col, age_col, "Distance_to_Closest_Hospital", readmit_col}
    missing = needed - set(df.columns)
    if missing:
        return None

    working = df.copy()
    working[gender_col] = working[gender_col].fillna("Unknown")

    age_cats, age_info = binning.bin_series(
        working[age_col], method="quantile", bins=age_bins, precision=0
    )
    distance_spec = distance_spec or binning.BINNING_PRESETS["Distance_to_Closest_Hospital"]
    dist_cats, dist_info = binning.bin_series(
        working["Distance_to_Closest_Hospital"], **distance_spec.to_kwargs()
    )

    grouped = (
        working.assign(_age=age_cats, _dist=dist_cats)
        .groupby([diagnosis_col, gender_col, "_age", "_dist"], dropna=False)
        .agg(count=(readmit_col, "size"), rate=(readmit_col, "mean"))
        .reset_index()
    )
    if grouped.empty:
        return None

    genders = (
        working[gender_col]
        .fillna("Unknown")
        .value_counts()
        .index.tolist()
    )
    if not genders:
        return None

    age_labels = age_info.get("labels") or [str(label) for label in age_cats.categories]
    dist_labels = dist_info.get("labels") or [str(label) for label in dist_cats.categories]

    nrows = len(diagnoses)
    ncols = len(genders)
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(max(ncols, 1) * 3.6, max(nrows, 1) * 3.4),
        squeeze=False,
    )
    norm = mcolors.Normalize(0, 1)
    cmap = sns.color_palette("viridis", as_cmap=True)

    for row_idx, diag in enumerate(diagnoses):
        for col_idx, gender in enumerate(genders):
            ax = axes[row_idx, col_idx]
            panel = grouped[
                (grouped[diagnosis_col] == diag) & (grouped[gender_col] == gender)
            ]
            if panel.empty:
                ax.axis("off")
                continue
            pivot = panel.pivot(index="_age", columns="_dist", values="rate")
            sns.heatmap(
                pivot,
                ax=ax,
                cmap=cmap,
                norm=norm,
                cbar=False,
                annot=True,
                fmt=".2f",
            )
            ax.set_xticks(range(len(dist_labels)))
            ax.set_xticklabels(dist_labels, rotation=45, ha="right", fontsize="small")
            ax.set_yticks(range(len(age_labels)))
            ax.set_yticklabels(age_labels, fontsize="small")
            if row_idx == nrows - 1:
                ax.set_xlabel("Distance (quantile)")
            else:
                ax.set_xlabel("")
            if col_idx == 0:
                ax.set_ylabel("Age (quantile)")
            else:
                ax.set_ylabel("")
            title = f"{diag} — {gender}"
            ax.set_title(title, fontsize="medium")

    fig.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=cmap),
        ax=axes,
        shrink=0.7,
        label="Readmission rate",
    )
    fig.tight_layout()

    summary = grouped.rename(columns={"_age": "Age_bin", "_dist": "Distance_bin"})
    return fig, summary


def _build_comorbidity_prior_bubble(
    df: pd.DataFrame,
    diagnoses: Sequence[str],
    prior_bins: pd.Categorical,
    comorb_bins: pd.Categorical,
    prior_info: Dict[str, object],
    comorb_info: Dict[str, object],
    readmit_col: str,
    diagnosis_col: str,
) -> Tuple[plt.Figure, pd.DataFrame] | None:
    if df.empty:
        return None

    summary = (
        df.assign(_prior=prior_bins, _comorb=comorb_bins)
        .groupby([diagnosis_col, "_prior", "_comorb"], dropna=False)
        .agg(count=(readmit_col, "size"), rate=(readmit_col, "mean"))
        .reset_index()
    )
    if summary.empty:
        return None

    nrows, ncols = _setup_grid(len(diagnoses))
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(max(ncols, 1) * 4.2, max(nrows, 1) * 4.0),
        squeeze=False,
    )
    cmap = sns.color_palette("rocket", as_cmap=True)
    norm = mcolors.Normalize(0, 1)

    x_labels = prior_info.get("labels") or [str(label) for label in prior_bins.categories]
    y_labels = comorb_info.get("labels") or [str(label) for label in comorb_bins.categories]

    max_count = summary["count"].max() or 1
    scatter = None
    for ax, diag in zip(axes.flatten(), diagnoses):
        diag_data = summary[summary[diagnosis_col] == diag]
        if diag_data.empty:
            ax.axis("off")
            continue
        x_codes = diag_data["_prior"].cat.codes
        y_codes = diag_data["_comorb"].cat.codes
        sizes = 220 * (diag_data["count"] / max_count) + 40
        scatter = ax.scatter(
            x_codes,
            y_codes,
            s=sizes,
            c=diag_data["rate"],
            cmap=cmap,
            norm=norm,
            edgecolor="none",
        )
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize="small")
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize="small")
        ax.set_xlabel("Prior admissions")
        ax.set_ylabel("Comorbidities")
        ax.set_title(str(diag))

    for ax in axes.flatten()[len(diagnoses):]:
        ax.axis("off")
    if scatter is not None:
        fig.colorbar(
            plt.cm.ScalarMappable(norm=norm, cmap=cmap),
            ax=axes,
            shrink=0.7,
            label="Readmission rate",
        )
    fig.tight_layout()

    return fig, summary.rename(
        columns={"_prior": "Prior_bin", "_comorb": "Comorbidity_bin"}
    )


def _build_comorbidity_upset(
    df: pd.DataFrame,
    readmit_col: str,
    columns: Iterable[str],
    max_sets: int = 12,
) -> Tuple[plt.Figure, pd.DataFrame] | None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        return None

    working = df[list(columns) + [readmit_col]].copy()
    for col in columns:
        series = working[col].fillna(0)
        if series.dropna().isin({0, 1}).all():
            working[col] = series.astype(int)
        else:
            working[col] = (series > 0).astype(int)
    working[readmit_col] = _ensure_boolean(working[readmit_col])

    grouped = (
        working.groupby(list(columns), dropna=False)[readmit_col]
        .agg([("count", "size"), ("rate", "mean")])
        .reset_index()
    )
    if grouped.empty:
        return None

    grouped = grouped.sort_values("count", ascending=False).head(max_sets)
    labels = []
    for _, row in grouped.iterrows():
        active = [name.replace("Has_", "") for name, flag in row[list(columns)].items() if int(flag) == 1]
        labels.append(" + ".join(active) if active else "None")
    grouped = grouped.assign(intersection=labels)

    counts = grouped["count"].to_numpy()
    rates = grouped["rate"].to_numpy()
    cmap = sns.color_palette("mako", as_cmap=True)
    norm = mcolors.Normalize(0, 1)

    fig = plt.figure(figsize=(max(6, 0.8 * len(grouped)), 6))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1.4], hspace=0.05)
    ax_bar = fig.add_subplot(gs[0])
    ax_matrix = fig.add_subplot(gs[1], sharex=ax_bar)

    bar_colors = cmap(norm(rates))
    bars = ax_bar.bar(range(len(grouped)), counts, color=bar_colors)
    ax_bar.set_ylabel("Patients")
    ax_bar.set_xticks([])
    ax_bar.set_title("Comorbidity intersections")
    for idx, bar in enumerate(bars):
        height = bar.get_height()
        ax_bar.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{rates[idx]:.1%}",
            ha="center",
            va="bottom",
            fontsize="small",
        )

    matrix_rows = list(columns)[::-1]
    ax_matrix.set_yticks(range(len(matrix_rows)))
    ax_matrix.set_yticklabels([col.replace("Has_", "") for col in matrix_rows])
    ax_matrix.set_xlabel("Intersection")
    ax_matrix.set_xlim(-0.5, len(grouped) - 0.5)
    ax_matrix.set_xticks(range(len(grouped)))
    ax_matrix.set_xticklabels(grouped["intersection"], rotation=45, ha="right")

    for row_idx, col in enumerate(matrix_rows):
        values = grouped[col].astype(int).to_numpy()
        y = row_idx
        ax_matrix.scatter(
            range(len(grouped)),
            [y] * len(grouped),
            s=np.where(values == 1, 120, 18),
            c=np.where(values == 1, "#2a9d8f", "#d0d0d0"),
        )
        ax_matrix.hlines(y, -0.5, len(grouped) - 0.5, color="#cccccc", linewidth=0.5)

    ax_matrix.set_ylim(-0.5, len(matrix_rows) - 0.5)
    fig.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=cmap),
        ax=ax_bar,
        pad=0.01,
        fraction=0.05,
        label="Readmission rate",
    )
    fig.tight_layout()

    summary = grouped.rename(columns={col: f"intersection_{col}" for col in columns})
    return fig, summary


__all__ = ["build_small_multiples"]
