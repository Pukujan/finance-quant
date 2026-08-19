from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Field, Lag


def test_lag_one_reads_previous_bar_only():
    hist = [{"close": 1.0}, {"close": 9.0}]
    assert evaluate(Lag(Field("close"), 1), hist) == 1.0
