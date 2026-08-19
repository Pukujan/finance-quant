import pytest

from finance_quant.acceptance.seal import SafeAcceptanceReceipt, SealRecord
from finance_quant.acceptance.uses import SealExhausted, assert_use_allowed


def test_seal_use_within_budget_allowed():
    record = SealRecord("A", "0" * 64, "1" * 64, "2024-01-01", "h", "s", max_uses=2)
    assert_use_allowed(record, 1)
    assert_use_allowed(record, 2)


def test_seal_use_exceeds_budget_raises():
    record = SealRecord("A", "0" * 64, "1" * 64, "2024-01-01", "h", "s", max_uses=1)
    with pytest.raises(SealExhausted):
        assert_use_allowed(record, 2)


def test_safe_receipt_invalid_status_rejected():
    with pytest.raises(ValueError, match="invalid acceptance status"):
        SafeAcceptanceReceipt("A", "0" * 64, "1" * 64, "unknown", (), (), 1)
