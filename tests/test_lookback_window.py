from finance_quant.dsl.checker import check
from finance_quant.dsl.ir import Field, Rolling


def test_rolling_lookback_is_window_minus_one():
    assert check(Rolling("mean", Field("close"), 1)).min_lookback_bars == 0
    assert check(Rolling("mean", Field("close"), 10)).min_lookback_bars == 9
