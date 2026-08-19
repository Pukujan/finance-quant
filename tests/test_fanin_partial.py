import pytest

from finance_quant.orchestration.fanin import PartialCampaign, deterministic_aggregate
from finance_quant.orchestration.lifecycle import AttemptStore


def test_deterministic_aggregate_raises_when_incomplete(tmp_path):
    store = AttemptStore(tmp_path / "fanin.db")
    with pytest.raises(PartialCampaign, match="0/3"):
        deterministic_aggregate(store, "m" * 64, ("a", "b", "c"))
    store.close()
