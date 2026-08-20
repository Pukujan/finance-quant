"""Static temporal-effect checker.

Effect `max_lookahead_days` answers: how far *after* evaluation t could this node
require data? Accepted programs always have 0; no grammar node can increase it.
The certificate is a data-loader contract: query `as_of(vt, evaluation_kt)`.
"""
from __future__ import annotations

from dataclasses import dataclass

from .ir import Binary, Const, CrossSection, Expr, Field, Fundamental, Lag, Rolling, RollingPair, Unary


class TemporalError(ValueError):
    pass


@dataclass(frozen=True)
class EffectCertificate:
    max_lookahead_days: int
    min_lookback_bars: int
    requires_universe: str | None
    deterministic: bool = True


_UNARY = {"neg", "abs", "log", "sign"}
_BINARY = {"add", "sub", "mul", "div", "signed_power", "min", "max", "gt", "lt"}
_ROLLING = {"mean", "std", "sum", "rank", "slope", "residual", "rsquare", "max", "min", "idxmax", "idxmin", "quantile"}
_ROLLING_PAIR = {"corr", "cov", "slope", "residual", "rsquare"}
_CROSS = {"rank", "zscore"}


def check(expr: Expr) -> EffectCertificate:
    if isinstance(expr, (Const, Field)):
        return EffectCertificate(0, 0, None)
    if isinstance(expr, Fundamental):
        if expr.declared_lag_days < expr.required_lag_days:
            raise TemporalError(
                f"fundamental {expr.name!r} declares {expr.declared_lag_days}d lag; "
                f"source contract requires >= {expr.required_lag_days}d"
            )
        return EffectCertificate(0, 0, None)
    if isinstance(expr, Unary):
        if expr.op not in _UNARY:
            raise TemporalError(f"unsupported unary op {expr.op!r}")
        return check(expr.arg)
    if isinstance(expr, Binary):
        if expr.op not in _BINARY:
            raise TemporalError(f"unsupported binary op {expr.op!r}")
        if expr.op == "div" and isinstance(expr.right, Const) and expr.right.value == 0:
            raise TemporalError("division by literal zero")
        return _combine(check(expr.left), check(expr.right))
    if isinstance(expr, Lag):
        if expr.bars < 0:
            raise TemporalError("negative lag is forward-looking and not in the grammar")
        e = check(expr.arg)
        return EffectCertificate(e.max_lookahead_days, e.min_lookback_bars + expr.bars,
                                 e.requires_universe, e.deterministic)
    if isinstance(expr, Rolling):
        if expr.op not in _ROLLING or expr.window < 1:
            raise TemporalError("rolling op must be supported with window >= 1")
        if expr.op == "quantile" and expr.quantile is not None and not 0 <= expr.quantile <= 1:
            raise TemporalError("rolling quantile must be between zero and one")
        if expr.op != "quantile" and expr.quantile is not None:
            raise TemporalError("only rolling quantile accepts a quantile argument")
        e = check(expr.arg)
        return EffectCertificate(e.max_lookahead_days, e.min_lookback_bars + expr.window - 1,
                                 e.requires_universe, e.deterministic)
    if isinstance(expr, RollingPair):
        if expr.op not in _ROLLING_PAIR or expr.window < 2:
            raise TemporalError("rolling pair op must be corr/cov/slope/residual/rsquare with window >= 2")
        combined = _combine(check(expr.left), check(expr.right))
        return EffectCertificate(combined.max_lookahead_days,
                                 combined.min_lookback_bars + expr.window - 1,
                                 combined.requires_universe, combined.deterministic)
    if isinstance(expr, CrossSection):
        if expr.op not in _CROSS or not expr.universe:
            raise TemporalError("cross-sectional op needs supported op and bitemporal universe")
        e = check(expr.arg)
        if e.requires_universe and e.requires_universe != expr.universe:
            raise TemporalError("expression cannot mix universe identities")
        return EffectCertificate(e.max_lookahead_days, e.min_lookback_bars,
                                 expr.universe, e.deterministic)
    raise TemporalError(f"unrecognized expression node {type(expr)!r}")


def _combine(a: EffectCertificate, b: EffectCertificate) -> EffectCertificate:
    if a.requires_universe and b.requires_universe and a.requires_universe != b.requires_universe:
        raise TemporalError("binary expression mixes bitemporal universe identities")
    return EffectCertificate(
        max(a.max_lookahead_days, b.max_lookahead_days),
        max(a.min_lookback_bars, b.min_lookback_bars),
        a.requires_universe or b.requires_universe,
        a.deterministic and b.deterministic,
    )
