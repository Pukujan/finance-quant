import pytest

from finance_quant.acceptance.seal import SealRecord
from finance_quant.acceptance.uses import SealExhausted, assert_use_allowed


def test_seal_a_allows_two_uses_seal_b_one():
    a = SealRecord("SEAL-A", "c" * 64, "l" * 64, "t", "h" * 40, "s", 2)
    b = SealRecord("SEAL-B", "c" * 64, "l" * 64, "t", "h" * 40, "s", 1)
    assert_use_allowed(a, 1)
    assert_use_allowed(a, 2)
    with pytest.raises(SealExhausted):
        assert_use_allowed(a, 3)
    with pytest.raises(SealExhausted):
        assert_use_allowed(b, 2)
