from __future__ import annotations

import pytest

from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.interpreter import evaluate, evaluate_cross_section
from finance_quant.dsl.ir import Binary, Const, CrossSection, Field, Fundamental, Lag, Rolling, from_dict, to_dict


def test_sma_expression_checks_and_interprets_without_future_access():
    expr = Rolling("mean", Field("close"), 3)
    cert = check(expr)
    assert cert.max_lookahead_days == 0 and cert.min_lookback_bars == 2
    assert evaluate(expr, [{"close": 1}, {"close": 2}, {"close": 6}]) == 3.0


def test_negative_lag_is_a_static_leakage_error():
    with pytest.raises(TemporalError, match="forward-looking"):
        check(Lag(Field("close"), -1))


def test_underdeclared_fundamental_lag_is_rejected():
    with pytest.raises(TemporalError, match="requires >= 45"):
        check(Fundamental("revenue", declared_lag_days=10))


def test_cross_section_requires_bitemporal_universe_and_is_deterministic():
    expr = CrossSection("rank", Field("close"), "FIXIDX")
    assert check(expr).requires_universe == "FIXIDX"
    ranks = evaluate_cross_section(expr, {"AAA": [{"close": 10}], "BBB": [{"close": 20}]})
    assert ranks == {"AAA": 0.5, "BBB": 1.0}


def test_ir_round_trip_and_binary_expression():
    expr = Binary("sub", Field("close"), Lag(Field("close"), 1))
    restored = from_dict(to_dict(expr))
    assert restored == expr
    assert evaluate(restored, [{"close": 2}, {"close": 5}]) == 3.0
