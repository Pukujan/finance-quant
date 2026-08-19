from finance_quant.pit.model import BitemporalRecord, PitContractError
import pytest


def test_short_date_is_rejected():
    with pytest.raises(PitContractError):
        BitemporalRecord("bar", "AAA", "2024-1-2", "2024-01-02", {}, "x", 0)
