from finance_quant.orchestration.fanin import status
from finance_quant.orchestration.lifecycle import AttemptStore


def test_empty_expected_set_is_complete():
    store = AttemptStore(":memory:")
    st = status(store, "m", ())
    assert st.complete
    assert st.total_expected == 0
    store.close()
