from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Binary, Field


def test_div_of_equal_fields_is_one():
    hist = [{"close": 8.0, "open": 8.0}]
    assert evaluate(Binary("div", Field("close"), Field("open")), hist) == 1.0
