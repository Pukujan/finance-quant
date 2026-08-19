from pathlib import Path

from finance_quant.__main__ import COMMANDS


def test_cli_lists_verify():
    assert "verify" in COMMANDS


def test_verify_script_exists():
    assert Path(COMMANDS["verify"]).exists()
