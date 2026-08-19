import hashlib

from finance_quant.execution.lean import ExecutionContract, StrategyManifest, generate_algorithm


def test_generated_algorithm_hash_is_deterministic():
    contract = ExecutionContract()
    manifest = StrategyManifest(
        strategy_id="s1",
        dataset_manifest_hash="a" * 64,
        signal_artifact_hash="b" * 64,
        symbols=("SPY",),
        execution_contract=contract,
    )
    text = generate_algorithm(manifest)
    h = hashlib.blake2b(text.encode(), digest_size=32).hexdigest()
    assert h == hashlib.blake2b(generate_algorithm(manifest).encode(), digest_size=32).hexdigest()
