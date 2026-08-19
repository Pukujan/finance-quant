from finance_quant.pit.corporate_actions import split_ratio_as_of
from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore


def test_split_ratio_is_1_before_announcement_even_after_effective_vt():
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    actions = store.as_of("corporate_action", ["CCC"], "2024-01-01", "2024-03-01", "2024-01-20")
    # Effective date is 2024-02-15, announcement 2024-02-01; knowledge 2024-01-20 cannot see it.
    assert split_ratio_as_of(actions, "CCC", "2024-02-20", "2024-01-20") == 1.0
