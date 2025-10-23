"""Binning utilities shared across readmission visualizations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Sequence, Tuple

import numpy as np
import pandas as pd


@dataclass
class BinSpec:
    method: str
    bins: int | Sequence[float]
    labels: Sequence[str] | None = None
    precision: int = 2
    include_lowest: bool = True

    def to_kwargs(self) -> Dict[str, Any]:
        return {
            "method": self.method,
            "bins": self.bins,
            "labels": self.labels,
            "precision": self.precision,
            "include_lowest": self.include_lowest,
        }


BINNING_PRESETS: Dict[str, BinSpec] = {
    "Length_of_Stay": BinSpec(method="quantile", bins=5, precision=1),
    "Distance_to_Closest_Hospital": BinSpec(method="quantile", bins=5, precision=1),
    "Num_Prior_Admissions_Last_6_Months": BinSpec(method="edges", bins=[0, 1, 2, 4, np.inf]),
    "Num_Comorbidities": BinSpec(method="edges", bins=[0, 2, 4, 6, np.inf]),
}


def _compute_edges(series: pd.Series, method: str, bins: int | Sequence[float]) -> np.ndarray:
    if method == "equal":
        return np.linspace(series.min(), series.max(), int(bins) + 1)
    if method == "quantile":
        quantiles = np.linspace(0, 1, int(bins) + 1)
        return series.quantile(quantiles, interpolation="linear").to_numpy()
    if method == "edges":
        return np.asarray(bins, dtype=float)
    raise ValueError(f"Unknown binning method: {method}")


def bin_series(
    series: pd.Series,
    method: str,
    bins: int | Sequence[float],
    labels: Sequence[str] | None = None,
    precision: int = 2,
    include_lowest: bool = True,
) -> Tuple[pd.Categorical, Dict[str, Any]]:
    """Bin a numeric series using the configured strategy."""

    clean = series.dropna()
    if clean.empty:
        categories = pd.Categorical([])
        return categories, {"edges": [], "labels": [], "counts": {}, "method": method}

    edges = _compute_edges(clean, method, bins)
    edges[0] = np.floor(edges[0]) if np.isfinite(edges[0]) else edges[0]
    edges[-1] = np.ceil(edges[-1]) if np.isfinite(edges[-1]) else edges[-1]
    labels = list(labels) if labels is not None else None
    binned = pd.cut(
        series,
        bins=edges,
        labels=labels,
        include_lowest=include_lowest,
        precision=precision,
        duplicates="drop",
    )
    info = {
        "edges": edges.tolist(),
        "labels": list(binned.cat.categories) if hasattr(binned, "cat") else [],
        "counts": binned.value_counts(dropna=False).to_dict(),
        "method": method,
    }
    return binned, info


def cross_agg(
    df: pd.DataFrame,
    x_bins: pd.Series | str,
    y_bins: pd.Series | str,
    value: str,
    agg: str = "mean",
) -> pd.DataFrame:
    """Aggregate values across two categorical binnings."""

    x = df[x_bins] if isinstance(x_bins, str) else x_bins
    y = df[y_bins] if isinstance(y_bins, str) else y_bins
    working = df.copy()
    working["_x"] = pd.Categorical(x)
    working["_y"] = pd.Categorical(y)
    grouping = working.groupby(["_y", "_x"], dropna=False)

    if agg == "count":
        table = grouping.size().unstack(fill_value=0)
    else:
        table = grouping[value].agg(agg).unstack()
    return table


def resolve_bin_specs(overrides: Mapping[str, Mapping[str, Any]] | None = None) -> Dict[str, BinSpec]:
    specs: Dict[str, BinSpec] = {key: value for key, value in BINNING_PRESETS.items()}
    if overrides:
        for key, payload in overrides.items():
            base = specs.get(key)
            if base:
                merged = {**base.to_kwargs(), **payload}
            else:
                merged = dict(payload)
            specs[key] = BinSpec(**merged)
    return specs


__all__ = ["BINNING_PRESETS", "BinSpec", "bin_series", "cross_agg", "resolve_bin_specs"]
