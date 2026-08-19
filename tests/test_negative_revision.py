from finance_quant.pit.model import BitemporalRecord, PitContractError
import pytest


def test_negative_revision_is_rejected():
    with pytest.raises(PitContractError):
        BitemporalRecord("bar", "AAA", "2024-01-02", "2024-01-02", {}, "x", -1)
