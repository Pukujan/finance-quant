from finance_quant.orchestration.fanin import campaign_fingerprint


def test_fingerprint_changes_with_manifest():
    r = '{"work_order_hash": "a", "terminal_status": "completed", "metrics": [], "artifact_manifest": []}'
    assert campaign_fingerprint("m1", [r]) != campaign_fingerprint("m2", [r])
