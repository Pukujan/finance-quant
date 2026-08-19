"""Split/dividend adjustment: raw prices stay raw; adjustment is an explicit run-record mode."""
from __future__ import annotations

from finance_quant.pit.model import BitemporalRecord


def apply_split_if_total_return(price: float, ratio: float, mode: str) -> float:
    if mode == "Raw":
        return price
    if mode == "SplitAdjusted":
        return price / ratio
    raise ValueError(f"unknown adjustment mode {mode}")


def split_ratio_as_of(actions: list[BitemporalRecord], instrument: str, vt: str, kt: str) -> float:
    known = [a for a in actions
             if a.instrument_id == instrument and a.vt <= vt and a.kt <= kt
             and a.payload.get("kind") == "split"]
    ratio = 1.0
    for a in known:
        ratio *= float(a.payload["ratio"])
    return ratio
