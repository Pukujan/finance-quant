"""Small, serializable, deliberately non-Turing-complete numeric expression IR."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Union


class IRValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Const:
    value: float


@dataclass(frozen=True)
class Field:
    """PIT bar field. Value at vt requires knowledge no later than vt."""
    name: str


@dataclass(frozen=True)
class Fundamental:
    """Fundamental field; source lag is declared and statically checked."""
    name: str
    declared_lag_days: int
    required_lag_days: int = 45


@dataclass(frozen=True)
class Unary:
    op: str                 # neg | abs | log | sign
    arg: "Expr"


@dataclass(frozen=True)
class Binary:
    op: str                 # add | sub | mul | div | min | max
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Lag:
    """Historical lookback only. Negative bars are forbidden by construction/checker."""
    arg: "Expr"
    bars: int


@dataclass(frozen=True)
class Rolling:
    op: str                 # mean | std | sum | rank | max | min | idxmax | idxmin
    arg: "Expr"
    window: int


@dataclass(frozen=True)
class RollingPair:
    op: str                 # corr | cov | slope | residual | rsquare
    left: "Expr"
    right: "Expr"
    window: int


@dataclass(frozen=True)
class CrossSection:
    op: str                 # rank | zscore
    arg: "Expr"
    universe: str           # bitemporal universe name, injected into effect


Expr = Union[Const, Field, Fundamental, Unary, Binary, Lag, Rolling, RollingPair, CrossSection]


def to_dict(expr: Expr) -> dict:
    """Canonical JSON-compatible serialization; artifact hash feeds ExperimentLedger."""
    if isinstance(expr, Const):
        return {"node": "const", "value": expr.value}
    if isinstance(expr, Field):
        return {"node": "field", "name": expr.name}
    if isinstance(expr, Fundamental):
        return {"node": "fundamental", "name": expr.name,
                "declared_lag_days": expr.declared_lag_days,
                "required_lag_days": expr.required_lag_days}
    if isinstance(expr, Unary):
        return {"node": "unary", "op": expr.op, "arg": to_dict(expr.arg)}
    if isinstance(expr, Binary):
        return {"node": "binary", "op": expr.op, "left": to_dict(expr.left),
                "right": to_dict(expr.right)}
    if isinstance(expr, Lag):
        return {"node": "lag", "bars": expr.bars, "arg": to_dict(expr.arg)}
    if isinstance(expr, Rolling):
        return {"node": "rolling", "op": expr.op, "window": expr.window,
                "arg": to_dict(expr.arg)}
    if isinstance(expr, RollingPair):
        return {"node": "rolling_pair", "op": expr.op, "window": expr.window,
                "left": to_dict(expr.left), "right": to_dict(expr.right)}
    if isinstance(expr, CrossSection):
        return {"node": "cross_section", "op": expr.op, "universe": expr.universe,
                "arg": to_dict(expr.arg)}
    raise IRValidationError(f"unknown IR node {type(expr)!r}")


def from_dict(raw: Mapping) -> Expr:
    n = raw["node"]
    if n == "const": return Const(float(raw["value"]))
    if n == "field": return Field(str(raw["name"]))
    if n == "fundamental": return Fundamental(str(raw["name"]), int(raw["declared_lag_days"]), int(raw.get("required_lag_days", 45)))
    if n == "unary": return Unary(str(raw["op"]), from_dict(raw["arg"]))
    if n == "binary": return Binary(str(raw["op"]), from_dict(raw["left"]), from_dict(raw["right"]))
    if n == "lag": return Lag(from_dict(raw["arg"]), int(raw["bars"]))
    if n == "rolling": return Rolling(str(raw["op"]), from_dict(raw["arg"]), int(raw["window"]))
    if n == "rolling_pair": return RollingPair(str(raw["op"]), from_dict(raw["left"]), from_dict(raw["right"]), int(raw["window"]))
    if n == "cross_section": return CrossSection(str(raw["op"]), from_dict(raw["arg"]), str(raw["universe"]))
    raise IRValidationError(f"unknown IR node tag {n!r}")
