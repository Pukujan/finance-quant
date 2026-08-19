from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Binary, Field


def test_div_by_field_volume():
    hist = [{"close": 10.0, "volume": 4.0}]
    assert evaluate(Binary("div", Field("close"), Field("volume")), hist) == 2.5
