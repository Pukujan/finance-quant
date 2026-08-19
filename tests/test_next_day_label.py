from finance_quant.pit.fixtures import generate
from finance_quant.pit.labels import next_day_returns
from finance_quant.pit.store import MemoryGoldStore


def test_next_day_label_uses_tomorrow_close():
    store = MemoryGoldStore()
    for rec in generate():
        store.put(rec)
    days = ["2024-01-02", "2024-01-03", "2024-01-04"]
    rets = next_day_returns(store, "AAA", days, "2024-01-05")
    assert "2024-01-02" in rets
    assert "2024-01-04" not in rets
