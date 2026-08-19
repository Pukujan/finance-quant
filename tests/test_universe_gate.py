import pytest

from finance_quant.execution.universe import InstrumentHalted, InstrumentState, assert_tradable


def test_active_instrument_passes():
    assert_tradable(InstrumentState("AAA", in_universe=True, halted=False, delisted=False))


def test_halted_instrument_rejected():
    with pytest.raises(InstrumentHalted, match="AAA"):
        assert_tradable(InstrumentState("AAA", in_universe=True, halted=True, delisted=False))


def test_delisted_instrument_rejected():
    with pytest.raises(InstrumentHalted, match="ZZZ"):
        assert_tradable(InstrumentState("ZZZ", in_universe=True, halted=False, delisted=True))


def test_not_in_universe_rejected():
    with pytest.raises(InstrumentHalted, match="BBB"):
        assert_tradable(InstrumentState("BBB", in_universe=False, halted=False, delisted=False))
