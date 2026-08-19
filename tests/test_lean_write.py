from pathlib import Path

from finance_quant.execution.lean import ExecutionContract, StrategyManifest, generate_algorithm
from finance_quant.execution.write import write_algorithm


def test_write_algorithm_roundtrip(tmp_path):
    contract = ExecutionContract()
    manifest = StrategyManifest(
        strategy_id="s1",
        dataset_manifest_hash="a" * 64,
        signal_artifact_hash="b" * 64,
        symbols=("SPY", "QQQ"),
        execution_contract=contract,
    )
    path = write_algorithm(manifest, tmp_path / "main.py")
    text = Path(path).read_text(encoding="utf-8")
    assert "GENERATED FILE - DO NOT EDIT." in text
    assert "strategy_id=s1" in text
    assert f"dataset_manifest_hash={'a' * 64}" in text
    assert f"signal_artifact_hash={'b' * 64}" in text
    assert "signal at bar t cannot fill earlier than next-bar open" in text
    assert "GeneratedFinanceQuantAlgorithm(QCAlgorithm)" in text
    assert "SPY" in text
    assert "QQQ" in text
