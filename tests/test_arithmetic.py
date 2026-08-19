from finance_quant.dsl.interpreter import evaluate
from finance_quant.dsl.ir import Binary, Field


def test_add_sub_mul():
    hist = [{"close": 4.0, "volume": 2.0}]
    assert evaluate(Binary("add", Field("close"), Field("volume")), hist) == 6.0
    assert evaluate(Binary("sub", Field("close"), Field("volume")), hist) == 2.0
    assert evaluate(Binary("mul", Field("close"), Field("volume")), hist) == 8.0
