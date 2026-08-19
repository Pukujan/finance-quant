from finance_quant.orchestration.receipts import parse_receipt
from finance_quant.orchestration.contracts import ContractError
import pytest


@pytest.mark.parametrize("payload", [
    "{}",
    '{"work_order_hash": "x"}',
    "not-json",
    '{"work_order_hash": "x", "retry_seq": -1, "terminal_status": "completed", "worker_id": "w", "backend_id": "b", "started_at": 2, "ended_at": 1, "environment_hash": "e"}',
])
def test_malformed_receipts_are_rejected(payload):
    with pytest.raises(ContractError):
        parse_receipt(payload)
