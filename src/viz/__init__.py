"""Visualization utilities for the readmission exploratory analysis package."""

from importlib import import_module
from typing import Any


def load_builder(path: str) -> Any:
    """Dynamically import a visualization builder by dotted path.

    This helper is convenient for CLI integrations where builders are
    referenced via configuration and avoids importing heavy plotting
    libraries at module import time.
    """

    module_name, _, attribute = path.rpartition(".")
    if not module_name:
        raise ValueError(f"Expected dotted path, received: {path!r}")
    module = import_module(module_name)
    try:
        return getattr(module, attribute)
    except AttributeError as exc:  # pragma: no cover - defensive guard
        raise AttributeError(f"Module '{module_name}' has no attribute '{attribute}'") from exc


__all__ = ["load_builder"]
