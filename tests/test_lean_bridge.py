from finance_quant.execution.lean import ExecutionContract, StrategyManifest, generate_algorithm


def test_generated_lean_algorithm_pins_data_and_contract():
    contract = ExecutionContract()
    manifest = StrategyManifest("B1", "data-hash", "signal-hash", ("AAA", "BBB"), contract)
    code = generate_algorithm(manifest)
    assert "dataset_manifest_hash=data-hash" in code
    assert contract.hash in code
    assert "signal at bar t cannot fill earlier than next-bar open" in code
    assert generate_algorithm(manifest) == code
