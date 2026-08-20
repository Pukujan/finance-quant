"""Report Tier-1 coverage of Qlib's public Alpha158 feature configuration.

The fallback names and formulas mirror ``Alpha158DL.get_feature_config`` in
Qlib's public ``qlib.contrib.data.loader``.  When Qlib is available its names
are used as the source list; the local mapping remains explicit so this probe
does not need a Qlib runtime or a Tier-0 expression escape hatch.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# Direct execution (as used by smoke.py) puts scripts/ rather than the project
# root on sys.path.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from finance_quant.dsl.checker import check
from finance_quant.dsl.ir import Binary, Const, CrossSection, Expr, Field, Lag, Rolling, RollingPair, Unary, to_dict


WINDOWS = (5, 10, 20, 30, 60)
KBAR_NAMES = ("KMID", "KLEN", "KMID2", "KUP", "KUP2", "KLOW", "KLOW2", "KSFT", "KSFT2")
ROLLING_PREFIXES = (
    "ROC", "MA", "STD", "BETA", "RSQR", "RESI", "MAX", "MIN", "QTLU", "QTLD", "RANK", "RSV",
    "IMAX", "IMIN", "IMXD", "CORR", "CORD", "CNTP", "CNTN", "CNTD", "SUMP", "SUMN", "SUMD",
    "VMA", "VSTD", "WVMA", "VSUMP", "VSUMN", "VSUMD",
)


def _fallback_names() -> list[str]:
    return [*KBAR_NAMES, "OPEN0", "HIGH0", "LOW0", "VWAP0", *[f"{prefix}{window}" for prefix in ROLLING_PREFIXES for window in WINDOWS]]


def alpha158_feature_names() -> list[str]:
    """Return Alpha158 names from installed Qlib, or the pinned public fallback."""
    try:
        from qlib.contrib.data.loader import Alpha158DL  # type: ignore[import-not-found]

        _, names = Alpha158DL.get_feature_config({
            "kbar": {}, "price": {"windows": [0], "feature": ["OPEN", "HIGH", "LOW", "VWAP"]}, "rolling": {},
        })
        if len(names) == 158:
            return list(names)
    except ImportError:
        pass
    return _fallback_names()


def _div(left: Expr, right: Expr) -> Expr:
    return Binary("div", left, right)


def _change(field: str) -> Expr:
    return Binary("sub", Field(field), Lag(Field(field), 1))


def _positive(expr: Expr) -> Expr:
    return Binary("max", expr, Const(0))


def _mapping(name: str) -> Expr:
    close, high, low, volume = Field("close"), Field("high"), Field("low"), Field("volume")
    spread = Binary("sub", high, low)
    body = Binary("sub", close, Field("open"))
    kbar: dict[str, Expr] = {
        "KMID": _div(body, Field("open")), "KLEN": _div(spread, Field("open")), "KMID2": _div(body, Binary("add", spread, Const(1e-12))),
        "KUP": _div(Binary("sub", high, Binary("max", Field("open"), close)), Field("open")),
        "KUP2": _div(Binary("sub", high, Binary("max", Field("open"), close)), Binary("add", spread, Const(1e-12))),
        "KLOW": _div(Binary("sub", Binary("min", Field("open"), close), low), Field("open")),
        "KLOW2": _div(Binary("sub", Binary("min", Field("open"), close), low), Binary("add", spread, Const(1e-12))),
        "KSFT": _div(Binary("sub", Binary("sub", Binary("mul", Const(2), close), high), low), Field("open")),
        "KSFT2": _div(Binary("sub", Binary("sub", Binary("mul", Const(2), close), high), low), Binary("add", spread, Const(1e-12))),
    }
    if name in kbar:
        return kbar[name]
    if name in {"OPEN0", "HIGH0", "LOW0", "VWAP0"}:
        return _div(Field(name[:-1].lower()), close)
    match = re.fullmatch(r"([A-Z]+)(\d+)", name)
    if match is None:
        raise ValueError("unknown Alpha158 feature name")
    family, window_s = match.groups()
    window = int(window_s)
    ratio = lambda expr: _div(expr, close)
    if family == "ROC": return ratio(Lag(close, window))
    if family == "MA": return ratio(Rolling("mean", close, window))
    if family == "STD": return ratio(Rolling("std", close, window))
    if family == "BETA": return ratio(Rolling("slope", close, window))
    if family == "RSQR": return Rolling("rsquare", close, window)
    if family == "RESI": return ratio(Rolling("residual", close, window))
    if family == "MAX": return ratio(Rolling("max", high, window))
    if family == "MIN": return ratio(Rolling("min", low, window))
    if family == "QTLU": return ratio(Rolling("quantile", close, window, 0.8))
    if family == "QTLD": return ratio(Rolling("quantile", close, window, 0.2))
    if family == "RANK": return Rolling("rank", close, window)
    if family == "RSV": return _div(Binary("sub", close, Rolling("min", low, window)), Binary("add", Binary("sub", Rolling("max", high, window), Rolling("min", low, window)), Const(1e-12)))
    if family == "IMAX": return _div(Rolling("idxmax", high, window), Const(window))
    if family == "IMIN": return _div(Rolling("idxmin", low, window), Const(window))
    if family == "IMXD": return _div(Binary("sub", Rolling("idxmax", high, window), Rolling("idxmin", low, window)), Const(window))
    if family == "CORR": return RollingPair("corr", close, Unary("log", Binary("add", volume, Const(1))), window)
    if family == "CORD": return RollingPair("corr", _div(close, Lag(close, 1)), Unary("log", Binary("add", _div(volume, Lag(volume, 1)), Const(1))), window)
    if family in {"CNTP", "CNTN", "CNTD"}:
        up, down = Binary("gt", close, Lag(close, 1)), Binary("lt", close, Lag(close, 1))
        if family == "CNTP": return Rolling("mean", up, window)
        if family == "CNTN": return Rolling("mean", down, window)
        return Binary("sub", Rolling("mean", up, window), Rolling("mean", down, window))
    source = volume if family.startswith("V") else close
    delta = _change("volume" if family.startswith("V") else "close")
    denominator = Binary("add", Rolling("sum", Unary("abs", delta), window), Const(1e-12))
    if family in {"SUMP", "VSUMP"}: return _div(Rolling("sum", _positive(delta), window), denominator)
    if family in {"SUMN", "VSUMN"}: return _div(Rolling("sum", _positive(Unary("neg", delta)), window), denominator)
    if family in {"SUMD", "VSUMD"}: return _div(Binary("sub", Rolling("sum", _positive(delta), window), Rolling("sum", _positive(Unary("neg", delta)), window)), denominator)
    if family == "VMA": return _div(Rolling("mean", source, window), Binary("add", source, Const(1e-12)))
    if family == "VSTD": return _div(Rolling("std", source, window), Binary("add", source, Const(1e-12)))
    if family == "WVMA":
        weighted = Binary("mul", Unary("abs", Binary("sub", _div(close, Lag(close, 1)), Const(1))), volume)
        return _div(Rolling("std", weighted, window), Binary("add", Rolling("mean", weighted, window), Const(1e-12)))
    raise ValueError(f"unmapped Alpha158 family {family}")


# These prove that the requested major Tier-1 families have concrete mappings.
MAJOR_FAMILY_EXAMPLES: dict[str, Expr] = {
    "rolling_mean": Rolling("mean", Field("close"), 5), "rolling_std": Rolling("std", Field("close"), 5),
    "rolling_corr": RollingPair("corr", Field("close"), Field("volume"), 5), "rolling_cov": RollingPair("cov", Field("close"), Field("volume"), 5),
    "rolling_slope": Rolling("slope", Field("close"), 5), "rolling_residual": Rolling("residual", Field("close"), 5), "rolling_rsquare": Rolling("rsquare", Field("close"), 5),
    "rolling_max": Rolling("max", Field("high"), 5), "rolling_min": Rolling("min", Field("low"), 5), "rolling_idxmax": Rolling("idxmax", Field("high"), 5), "rolling_idxmin": Rolling("idxmin", Field("low"), 5), "rolling_quantile": Rolling("quantile", Field("close"), 5, 0.8),
    "rolling_ts_rank": Rolling("rank", Field("close"), 5), "cross_sectional_rank": CrossSection("rank", Field("close"), "CSI500"),
    "returns": Binary("sub", _div(Field("close"), Lag(Field("close"), 1)), Const(1)), "signed_power": Binary("signed_power", Field("close"), Const(2)),
    "abs": Unary("abs", Field("close")), "sign": Unary("sign", Field("close")),
}


def report() -> dict[str, Any]:
    entries: dict[str, dict[str, Any]] = {}
    for name in alpha158_feature_names():
        try:
            expr = _mapping(name)
            check(expr)
            entries[name] = {"expressible": True, "mapping": to_dict(expr)}
        except (ValueError, KeyError) as exc:
            entries[name] = {"expressible": False, "reason": str(exc)}
    unexpressible = [name for name, entry in entries.items() if not entry["expressible"]]
    total = len(entries)
    expressible = total - len(unexpressible)
    return {"total_count": total, "expressible_count": expressible, "percentage": round(100 * expressible / total, 2), "unexpressible": unexpressible, "features": entries}


def main() -> int:
    print(json.dumps(report(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
