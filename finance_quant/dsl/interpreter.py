"""Slow, dependency-light reference interpreter for Tier-1 IR (spike #3 oracle)."""
from __future__ import annotations

import math
from typing import Mapping, Sequence

from .ir import Binary, Const, CrossSection, Expr, Field, Fundamental, Lag, Rolling, RollingPair, Unary


class EvaluationError(ValueError):
    pass


def evaluate(expr: Expr, history: Sequence[Mapping[str, float]], index: int | None = None) -> float:
    """Evaluate one symbol's history up to index. No future row is ever read."""
    i = len(history) - 1 if index is None else index
    if i < 0 or i >= len(history):
        raise EvaluationError("evaluation index outside supplied history")
    if isinstance(expr, Const): return expr.value
    if isinstance(expr, Field): return float(history[i][expr.name])
    if isinstance(expr, Fundamental): return float(history[i][expr.name])
    if isinstance(expr, Unary):
        x = evaluate(expr.arg, history, i)
        return {"neg": lambda: -x, "abs": lambda: abs(x), "log": lambda: math.log(x),
                "sign": lambda: 1.0 if x > 0 else -1.0 if x < 0 else 0.0}[expr.op]()
    if isinstance(expr, Binary):
        a, b = evaluate(expr.left, history, i), evaluate(expr.right, history, i)
        if expr.op == "add": return a + b
        if expr.op == "sub": return a - b
        if expr.op == "mul": return a * b
        if expr.op == "div": return a / b
        if expr.op == "min": return min(a, b)
        if expr.op == "max": return max(a, b)
    if isinstance(expr, Lag): return evaluate(expr.arg, history, i - expr.bars)
    if isinstance(expr, Rolling):
        lo = i - expr.window + 1
        if lo < 0: raise EvaluationError("insufficient history for rolling window")
        xs = [evaluate(expr.arg, history, j) for j in range(lo, i + 1)]
        if expr.op == "mean": return sum(xs) / len(xs)
        if expr.op == "sum": return sum(xs)
        if expr.op == "std":
            m = sum(xs) / len(xs)
            return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))
        if expr.op == "rank": return sum(x <= xs[-1] for x in xs) / len(xs)
    if isinstance(expr, RollingPair):
        lo = i - expr.window + 1
        if lo < 0: raise EvaluationError("insufficient history for rolling pair")
        xs = [evaluate(expr.left, history, j) for j in range(lo, i + 1)]
        ys = [evaluate(expr.right, history, j) for j in range(lo, i + 1)]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / len(xs)
        varx = sum((x - mx) ** 2 for x in xs) / len(xs)
        vary = sum((y - my) ** 2 for y in ys) / len(ys)
        if expr.op == "cov": return cov
        if expr.op == "slope": return 0.0 if varx == 0 else cov / varx
        if expr.op == "residual":
            slope = 0.0 if varx == 0 else cov / varx
            intercept = my - slope * mx
            return ys[-1] - (slope * xs[-1] + intercept)
        if expr.op == "rsquare":
            if varx == 0 or vary == 0: return 0.0
            r = cov / (math.sqrt(varx) * math.sqrt(vary))
            return r * r
        sx = math.sqrt(varx)
        sy = math.sqrt(vary)
        if sx == 0 or sy == 0: return 0.0
        return cov / (sx * sy)
    if isinstance(expr, CrossSection):
        raise EvaluationError("cross-sectional evaluation needs evaluate_cross_section")
    raise EvaluationError(f"unsupported expression {expr!r}")


def evaluate_cross_section(expr: CrossSection, histories: Mapping[str, Sequence[Mapping[str, float]]]) -> dict[str, float]:
    vals = {symbol: evaluate(expr.arg, history) for symbol, history in histories.items()}
    ordered = sorted(vals.items(), key=lambda p: (p[1], p[0]))
    if expr.op == "rank":
        return {s: (i + 1) / len(ordered) for i, (s, _) in enumerate(ordered)}
    if expr.op == "zscore":
        mean = sum(vals.values()) / len(vals)
        var = sum((x - mean) ** 2 for x in vals.values()) / len(vals)
        sd = math.sqrt(var)
        return {s: 0.0 if sd == 0 else (v - mean) / sd for s, v in vals.items()}
    raise EvaluationError(f"unsupported cross-sectional op {expr.op}")
