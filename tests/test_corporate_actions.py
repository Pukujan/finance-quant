from finance_quant.pit.corporate_actions import apply_split_if_total_return, split_ratio_as_of
from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore


def test_split_is_invisible_before_announcement_and_raw_mode_keeps_price():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    actions = store.as_of("corporate_action", ["CCC"], "2024-01-01", "2024-03-01", "2024-01-15")
    assert split_ratio_as_of(actions, "CCC", "2024-02-15", "2024-01-15") == 1.0
    later = store.as_of("corporate_action", ["CCC"], "2024-01-01", "2024-03-01", "2024-02-05")
    assert split_ratio_as_of(later, "CCC", "2024-02-15", "2024-02-05") == 2.0
    assert apply_split_if_total_return(100.0, 2.0, "Raw") == 100.0
    assert apply_split_if_total_return(100.0, 2.0, "SplitAdjusted") == 50.0
