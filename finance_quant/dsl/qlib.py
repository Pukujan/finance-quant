"""Pure compiler from approved Tier-1 IR to Qlib expression syntax.

Qlib is intentionally optional: this compiler is testable without importing Qlib.
The checker is always called first, so unsupported or temporally invalid IR never
reaches a downstream Qlib runtime.
"""
from __future__ import annotations

from .checker import check
from .ir import Binary, Const, CrossSection, Expr, Field, Fundamental, Lag, Rolling, RollingPair, Unary


class QlibCompileError(ValueError):
    pass


_UNARY = {"neg": "Neg", "abs": "Abs", "log": "Log", "sign": "Sign"}
_BINARY = {"add": "Add", "sub": "Sub", "mul": "Mul", "div": "Div", "min": "Min", "max": "Max"}
_ROLLING = {"mean": "Mean", "std": "Std", "sum": "Sum", "rank": "Rank",
            "max": "Max", "min": "Min", "idxmax": "IdxMax", "idxmin": "IdxMin",
            "quantile": "Quantile"}


def compile_expr(expr: Expr) -> str:
    """Compile an accepted expression. Cross-section ops are intentionally not
    emitted: their universe semantics belong to the surrounding Qlib dataset handler.
    """
    check(expr)
    return _emit(expr)


def _emit(expr: Expr) -> str:
    if isinstance(expr, Const): return repr(expr.value)
    if isinstance(expr, Field): return "$" + expr.name
    if isinstance(expr, Fundamental): return "$" + expr.name
    if isinstance(expr, Unary): return f"{_UNARY[expr.op]}({_emit(expr.arg)})"
    if isinstance(expr, Binary): return f"{_BINARY[expr.op]}({_emit(expr.left)},{_emit(expr.right)})"
    if isinstance(expr, Lag): return f"Ref({_emit(expr.arg)},{expr.bars})"
    if isinstance(expr, Rolling): return f"{_ROLLING[expr.op]}({_emit(expr.arg)},{expr.window})"
    if isinstance(expr, RollingPair):
        name = {"corr": "Corr", "cov": "Cov", "slope": "Slope", "residual": "Resi", "rsquare": "Rsquare"}[expr.op]
        return f"{name}({_emit(expr.left)},{_emit(expr.right)},{expr.window})"
    if isinstance(expr, CrossSection):
        raise QlibCompileError(
            "cross-sectional ops require the bitemporal universe-aware handler; "
            "they are not scalar Qlib expressions"
        )
    raise QlibCompileError(f"unhandled IR node {type(expr)!r}")
