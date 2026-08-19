from finance_quant.pit.model import BitemporalRecord, PitContractError
import pytest


@pytest.mark.parametrize("ns", ["unknown", "alpha", ""])
def test_unknown_namespace_is_rejected(ns):
    with pytest.raises(PitContractError):
        BitemporalRecord(ns, "AAA", "2024-01-02", "2024-01-02", {}, "x", 0)
