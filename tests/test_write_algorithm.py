from finance_quant.execution.lean import ExecutionContract, StrategyManifest
from finance_quant.execution.write import write_algorithm


def test_generated_algorithm_file_is_pinned_and_deterministic(tmp_path):
    manifest = StrategyManifest("B1", "data", "sig", ("AAA",), ExecutionContract())
    a = write_algorithm(manifest, tmp_path / "algo.py")
    b = write_algorithm(manifest, tmp_path / "algo2.py")
    assert a.read_text() == b.read_text()
    assert "DO NOT EDIT" in a.read_text()
    assert "dataset_manifest_hash=data" in a.read_text()
