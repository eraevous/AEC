"""Orchestrator generating the readmission visualization book."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping

import matplotlib.pyplot as plt
import pandas as pd
import plotly.io as pio

from viz.readmit import (
    build_bars_and_hists,
    build_box_and_violin,
    build_corrgram,
    build_parallel_coordinates,
    build_sankey,
    build_small_multiples,
)
from viz.shared import theme


def _output_dirs(base: Path) -> Dict[str, Path]:
    figures = theme.ensure_output_dir(base / "figures")
    tables = theme.ensure_output_dir(base / "tables")
    html = theme.ensure_output_dir(base / "html")
    return {"figures": figures, "tables": tables, "html": html}


def _maybe_enabled(config: Mapping[str, Any], key: str, default: bool = True) -> bool:
    value = config.get(key)
    if isinstance(value, Mapping):
        return bool(value.get("enabled", default))
    if isinstance(value, bool):
        return value
    return default


def build_readmission_report(
    df: pd.DataFrame, config: Dict[str, Any]
) -> Dict[str, Any]:
    """Build the configured visualization suite and return a manifest."""

    base_dir = Path(config.get("output_dir", "artifacts"))
    dirs = _output_dirs(base_dir)
    manifest: Dict[str, Any] = {"output_dir": str(base_dir)}

    # Sankey ----------------------------------------------------------------
    sankey_cfg = config.get("sankey", {})
    if _maybe_enabled(config, "sankey") and sankey_cfg is not False:
        fig, exports, data = build_sankey(
            df,
            top_k=sankey_cfg.get("top_k", 10),
            min_count=sankey_cfg.get("min_count", 25),
            palette=sankey_cfg.get("palette"),
            readmit_col=sankey_cfg.get("readmit_col", "Has_Readmission_30_Days"),
        )
        html_path = dirs["html"] / "sankey.html"
        pio.write_html(fig, file=html_path, auto_open=False, include_plotlyjs="cdn")
        nodes_path = dirs["tables"] / "sankey_nodes.csv"
        links_path = dirs["tables"] / "sankey_links.csv"
        data["nodes"].to_csv(nodes_path, index=False)
        data["links"].to_csv(links_path, index=False)
        manifest["sankey"] = {
            "html": str(html_path),
            "nodes": str(nodes_path),
            "links": str(links_path),
        }

    # Corrgram --------------------------------------------------------------
    corr_cfg = config.get("corrgram", {})
    if _maybe_enabled(config, "corrgram") and corr_cfg:
        numerics = corr_cfg.get("numerics", [])
        if numerics:
            fig, metrics = build_corrgram(
                df,
                numerics=numerics,
                readmit_col=corr_cfg.get("readmit_col", "Has_Readmission_30_Days"),
                sample=corr_cfg.get("sample"),
            )
            paths = theme.save_figure(fig, "corrgram_3x3", dirs["figures"])
            metrics_path = dirs["tables"] / "corrgram_metrics.csv"
            metrics.to_csv(metrics_path, index=False)
            manifest["corrgram_3x3"] = {"figure": paths, "metrics": str(metrics_path)}
            plt.close(fig)

    # Bars & Histograms -----------------------------------------------------
    bars_cfg = config.get("bars_hists", {})
    if _maybe_enabled(config, "bars_hists") and (
        bars_cfg.get("categoricals") or bars_cfg.get("numerics")
    ):
        fig, summary = build_bars_and_hists(
            df,
            categoricals=bars_cfg.get("categoricals", []),
            numerics=bars_cfg.get("numerics", []),
            readmit_col=bars_cfg.get("readmit_col", "Has_Readmission_30_Days"),
            bins=bars_cfg.get("bins", 12),
        )
        paths = theme.save_figure(fig, "bars_hists", dirs["figures"])
        summary_path = dirs["tables"] / "bars_hists_summary.csv"
        summary.to_csv(summary_path, index=False)
        manifest["bars_hists"] = {"figure": paths, "summary": str(summary_path)}
        plt.close(fig)

    # Boxplots --------------------------------------------------------------
    box_cfg = config.get("boxplots", {})
    if _maybe_enabled(config, "boxplots") and box_cfg.get("numerics"):
        fig, stats_df = build_box_and_violin(
            df,
            numerics=box_cfg.get("numerics", []),
            readmit_col=box_cfg.get("readmit_col", "Has_Readmission_30_Days"),
        )
        paths = theme.save_figure(fig, "boxplots", dirs["figures"])
        stats_path = dirs["tables"] / "boxplots_stats.csv"
        stats_df.to_csv(stats_path, index=False)
        manifest["boxplots"] = {"figure": paths, "stats": str(stats_path)}
        plt.close(fig)

    # Parallel coordinates --------------------------------------------------
    pc_cfg = config.get("parallel_coords", {})
    if _maybe_enabled(config, "parallel_coords") and pc_cfg.get("cols"):
        fig = build_parallel_coordinates(
            df,
            cols=pc_cfg.get("cols", []),
            diagnosis_col=pc_cfg.get("diagnosis_col", "Primary_Diagnosis"),
            readmit_col=pc_cfg.get("readmit_col", "Has_Readmission_30_Days"),
            top_k_diag=pc_cfg.get("top_k_diag", 6),
            scaling=pc_cfg.get("scaling", "raw"),
        )
        html_path = (
            dirs["html"] / f"parallel_coords_{pc_cfg.get('scaling', 'raw')}.html"
        )
        pio.write_html(fig, file=html_path, auto_open=False, include_plotlyjs="cdn")
        manifest["parallel_coords"] = {"html": str(html_path)}

    # Small multiples -------------------------------------------------------
    sm_cfg = config.get("small_multiples", {})
    if _maybe_enabled(config, "small_multiples"):
        figures, tables = build_small_multiples(
            df,
            top_k_diag=sm_cfg.get("top_k_diag", 9),
            bin_specs=sm_cfg.get("bin_specs"),
            readmit_col=sm_cfg.get("readmit_col", "Has_Readmission_30_Days"),
        )
        if figures:
            fig_paths: Dict[str, Dict[str, str]] = {}
            for key, fig in figures.items():
                paths = theme.save_figure(fig, f"small_{key}", dirs["figures"])
                fig_paths[key] = paths
                plt.close(fig)
            table_paths: Dict[str, str] = {}
            for key, table in tables.items():
                path = dirs["tables"] / f"small_{key}.csv"
                table.to_csv(path, index=False)
                table_paths[key] = str(path)
            manifest["small_multiples"] = {"figures": fig_paths, "tables": table_paths}

    manifest_path = base_dir / "viz_manifest.json"
    theme.ensure_output_dir(base_dir)
    manifest["manifest"] = str(manifest_path)
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    return manifest


__all__ = ["build_readmission_report"]


def build_book(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """Compatability wrapper for build_readmission_report."""

    report_manifest = build_readmission_report(df, config)
    return report_manifest
