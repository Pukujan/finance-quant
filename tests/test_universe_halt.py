import pytest

from finance_quant.execution.universe import InstrumentHalted, InstrumentState, assert_tradable


def test_halted_and_delisted_names_cannot_receive_orders():
    assert_tradable(InstrumentState("AAA", True, False, False))
    with pytest.raises(InstrumentHalted):
        assert_tradable(InstrumentState("ZZZ", False, False, True))
    with pytest.raises(InstrumentHalted):
        assert_tradable(InstrumentState("BBB", True, True, False))
