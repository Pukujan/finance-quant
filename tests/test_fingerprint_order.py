from finance_quant.orchestration.fanin import campaign_fingerprint


def test_campaign_fingerprint_is_order_independent():
    receipts = [
        '{"work_order_hash": "b", "terminal_status": "completed", "metrics": [["x", 1]], "artifact_manifest": []}',
        '{"work_order_hash": "a", "terminal_status": "completed", "metrics": [["x", 2]], "artifact_manifest": []}',
    ]
    assert campaign_fingerprint("m", receipts) == campaign_fingerprint("m", list(reversed(receipts)))
