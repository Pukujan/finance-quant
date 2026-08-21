"""Verify that finance_quant.baselines re-exports the full public API."""
from __future__ import annotations

from finance_quant.baselines import (
    __all__,
    FoldResult,
    momentum_expression,
    rank_expression,
    returns_at_cutoff,
    run_buy_and_hold,
    run_cross_section_rank,
    run_momentum,
    run_walk_forward,
    score_rank_ic,
    sma3_expression,
)


def test_all_exports_defined():
    assert isinstance(__all__, list)
    assert len(__all__) == 10


def test_all_exports_importable():
    import finance_quant.baselines as pkg
    for name in __all__:
        assert hasattr(pkg, name), f"{name} is in __all__ but not importable"


def test_fold_result_is_dataclass():
    from dataclasses import is_dataclass
    assert is_dataclass(FoldResult)


def test_functions_are_callable():
    assert callable(momentum_expression)
    assert callable(run_momentum)
    assert callable(rank_expression)
    assert callable(run_cross_section_rank)
    assert callable(run_buy_and_hold)
    assert callable(sma3_expression)
    assert callable(run_walk_forward)
    assert callable(score_rank_ic)
    assert callable(returns_at_cutoff)


def test_momentum_expression_returns_binary():
    from finance_quant.dsl.ir import Binary
    expr = momentum_expression()
    assert isinstance(expr, Binary)


def test_sma3_expression_returns_rolling():
    from finance_quant.dsl.ir import Rolling
    expr = sma3_expression()
    assert isinstance(expr, Rolling)


def test_rank_expression_returns_cross_section():
    from finance_quant.dsl.ir import CrossSection
    expr = rank_expression()
    assert isinstance(expr, CrossSection)
