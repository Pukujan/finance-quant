from finance_quant.execution.lean import ExecutionContract, StrategyManifest, generate_algorithm


def test_generated_lean_algorithm_forbids_cloud_data_and_hand_edits():
    code = generate_algorithm(StrategyManifest("B1", "data", "sig", ("AAA",), ExecutionContract()))
    assert "DO NOT EDIT" in code
    assert "never QC cloud data" in code or "never from QC cloud data" in code
    assert "dataset_manifest_hash=data" in code
