from finance_quant.orchestration.fanin import campaign_fingerprint


def test_fingerprint_changes_when_metrics_change():
    a = '{"work_order_hash": "a", "terminal_status": "completed", "metrics": [["x", 1]], "artifact_manifest": []}'
    b = '{"work_order_hash": "a", "terminal_status": "completed", "metrics": [["x", 2]], "artifact_manifest": []}'
    assert campaign_fingerprint("m", [a]) != campaign_fingerprint("m", [b])
