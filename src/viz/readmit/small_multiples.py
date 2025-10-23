"""Small-multiple panels for diagnosis-level exploration."""

from __future__ import annotations

import math
from typing import Dict, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
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


def _ensure_boolean(series: pd.Series) -> pd.Series:
    if series.dropna().isin({0, 1}).all():
        return series.astype(int)
    if series.dropna().isin({False, True}).all():
        return series.astype(int)
    return (series == series.max()).astype(int)


def _top_diagnoses(df: pd.DataFrame, top_k: int) -> Tuple[pd.DataFrame, Sequence[str]]:
    counts = df["Primary_Diagnosis"].fillna("Unknown").value_counts()
    order = counts.nlargest(top_k).index.tolist()
    filtered = df[df["Primary_Diagnosis"].isin(order)].copy()
    filtered["Primary_Diagnosis"] = pd.Categorical(filtered["Primary_Diagnosis"], categories=order, ordered=True)
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
) -> Tuple[Dict[str, plt.Figure], Dict[str, pd.DataFrame]]:
    """Create bubble, heatmap, and mosaic small multiples by diagnosis."""

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Dataframe missing required columns: {sorted(missing)}")

    theme.apply_base_theme(font_scale=0.9)
    specs = binning.resolve_bin_specs(bin_specs)
    readmit = _ensure_boolean(df[readmit_col])
    df = df.assign(**{readmit_col: readmit})
    filtered, diagnoses = _top_diagnoses(df, top_k_diag)

    figures: Dict[str, plt.Figure] = {}
    tables: Dict[str, pd.DataFrame] = {}

    if filtered.empty:
        return figures, tables

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
        .groupby(["Primary_Diagnosis", "_los", "_dist"], dropna=False)
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
        diag_data = bubble_summary[bubble_summary["Primary_Diagnosis"] == diag]
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
        .groupby(["Primary_Diagnosis", "_prior", "Discharge_Status"], dropna=False)
        .agg(count=(readmit_col, "size"), rate=(readmit_col, "mean"))
        .reset_index()
    )
    tables["heatmap"] = heatmap_summary

    fig_heat, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4.5, nrows * 4.2), squeeze=False)
    heatmap_drawn = False
    for ax, diag in zip(axes.flatten(), diagnoses):
        diag_data = heatmap_summary[heatmap_summary["Primary_Diagnosis"] == diag]
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
        .groupby(["Primary_Diagnosis", "_comorb", "Discharge_Status"], dropna=False)
        .agg(count=(readmit_col, "size"), rate=(readmit_col, "mean"))
        .reset_index()
    )
    tables["mosaic"] = mosaic_summary

    fig_mosaic, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4.5, nrows * 4.2), squeeze=False)
    mosaic_drawn = False
    for ax, diag in zip(axes.flatten(), diagnoses):
        diag_data = mosaic_summary[mosaic_summary["Primary_Diagnosis"] == diag]
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

    return figures, tables


__all__ = ["build_small_multiples"]
