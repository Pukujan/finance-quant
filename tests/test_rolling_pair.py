from finance_quant.dsl.checker import check
from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, RollingPair, from_dict, to_dict
from finance_quant.dsl.qlib import compile_expr


def test_rolling_corr_is_historical_only_and_compiles():
    expr = RollingPair("corr", Field("close"), Field("volume"), 3)
    assert check(expr).max_lookahead_days == 0
    assert check(expr).min_lookback_bars == 2
    hist = [{"close": 1.0, "volume": 10.0}, {"close": 2.0, "volume": 20.0}, {"close": 3.0, "volume": 30.0}]
    assert abs(evaluate(expr, hist) - 1.0) < 1e-9
    assert compile_expr(expr) == "Corr($close,$volume,3)"
    assert from_dict(to_dict(expr)) == expr
