"""Centralized styling primitives and export helpers for visual modules."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping, Sequence

import matplotlib.pyplot as plt
import seaborn as sns


READMISSION_PALETTE = {0: "#264653", 1: "#e76f51"}
ACCENT_PALETTE = {
    "diagnosis": "#2a9d8f",
    "distance": "#287271",
    "los": "#b56576",
}


def apply_base_theme(font_scale: float = 1.0) -> None:
    """Apply a consistent seaborn/matplotlib theme."""

    sns.set_theme(context="talk", style="whitegrid", font_scale=font_scale)
    sns.set_palette(list(READMISSION_PALETTE.values()))


def readmit_palette(values: Iterable[int | bool]) -> Dict[int, str]:
    """Return palette mapping for the provided readmission values."""

    resolved = {}
    for value in values:
        key = int(value)
        resolved[key] = READMISSION_PALETTE.get(key, sns.color_palette("Set2")[key % 8])
    return resolved


def annotate_base_rate(ax: plt.Axes, rate: float, label: str = "Base rate") -> None:
    """Annotate subplot with the dataset readmission base rate."""

    ax.text(
        0.98,
        0.92,
        f"{label}: {rate:.1%}",
        ha="right",
        va="top",
        transform=ax.transAxes,
        fontsize="small",
        bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "none"},
    )


def ensure_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_figure(
    fig: plt.Figure,
    name: str,
    output_dir: str | Path,
    formats: Sequence[str] = ("png", "svg"),
    dpi: int = 300,
    metadata: Mapping[str, str] | None = None,
) -> Dict[str, str]:
    """Persist a figure to disk in the requested formats."""

    out_dir = ensure_output_dir(output_dir)
    saved: Dict[str, str] = {}
    meta: MutableMapping[str, str] = dict(metadata or {})
    for fmt in formats:
        path = out_dir / f"{name}.{fmt}"
        fig.savefig(path, dpi=dpi, bbox_inches="tight", metadata=meta)
        saved[fmt] = str(path)
    return saved


__all__ = [
    "ACCENT_PALETTE",
    "READMISSION_PALETTE",
    "annotate_base_rate",
    "apply_base_theme",
    "ensure_output_dir",
    "readmit_palette",
    "save_figure",
]
