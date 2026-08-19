import sys
from pathlib import Path

from finance_quant.__main__ import COMMANDS, main


def test_cli_lists_generate_lean():
    assert "generate-lean" in COMMANDS


def test_generate_lean_cli_writes_file(tmp_path):
    out = tmp_path / "main.py"
    ret = main(["generate-lean", "--out", str(out), "--symbols", "SPY,QQQ", "--strategy-id", "test"])
    assert ret == 0
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "GeneratedFinanceQuantAlgorithm(QCAlgorithm)" in text
    assert "SPY" in text
    assert "QQQ" in text


def test_generate_lean_check_passes(tmp_path):
    ret = main([
        "generate-lean", "--check",
        "--dataset-hash", "d" * 64,
        "--signal-hash", "a" * 64,
        "--strategy-id", "test2",
    ])
    assert ret == 0


def test_generate_lean_check_fails_on_bad_hash(tmp_path):
    ret = main([
        "generate-lean", "--check",
        "--dataset-hash", "not-a-hash",
        "--signal-hash", "a" * 64,
        "--strategy-id", "test2",
    ])
    assert ret == 2
