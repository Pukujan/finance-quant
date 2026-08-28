"""Tiny deterministic executors used by lab smoke tests/examples."""
from __future__ import annotations

from .core import ArmContext, LabError


def weighted_signal(context: ArmContext) -> float:
    config = context.config
    weights = config.get("weights", {}) if isinstance(config, dict) else {}
    field = config.get("field", "signal") if isinstance(config, dict) else "signal"
    total = 0.0
    for lane in context.lanes:
        payload = lane.payload
        if not isinstance(payload, dict) or field not in payload:
            raise LabError(f"lane {lane.lane!r} lacks numeric field {field!r}")
        total += float(weights.get(lane.lane, 1.0)) * float(payload[field])
    return total
