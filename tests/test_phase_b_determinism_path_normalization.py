from scripts.run_phase_b_determinism_drill import content_hash, semantic_lean_receipt


def test_lean_semantic_receipt_ignores_ephemeral_parent_directory():
    a = {
        "strategy_id": "phase-b-baselines",
        "status": "success",
        "custom_data_source": r"C:\\temp\\phase-b-drill\\lean_0\\lean_receipt_custom_data.py",
        "signal_hash": "same",
    }
    b = {
        "strategy_id": "phase-b-baselines",
        "status": "success",
        "custom_data_source": r"C:\\temp\\phase-b-drill\\lean_1\\lean_receipt_custom_data.py",
        "signal_hash": "same",
    }
    assert content_hash(semantic_lean_receipt(a)) == content_hash(semantic_lean_receipt(b))
