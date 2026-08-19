"""Write a generated LEAN algorithm to disk. Hand edits are forbidden: regenerate."""
from __future__ import annotations

from pathlib import Path

from .lean import StrategyManifest, generate_algorithm


def write_algorithm(manifest: StrategyManifest, out: str | Path) -> Path:
    path = Path(out)
    path.write_text(generate_algorithm(manifest), encoding="utf-8")
    return path
