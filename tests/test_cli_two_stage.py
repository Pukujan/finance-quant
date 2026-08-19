from pathlib import Path

from finance_quant import __main__ as cli


def test_cli_includes_two_stage_and_path_exists():
    assert "two-stage" in cli.COMMANDS
    assert (Path(__file__).resolve().parents[1] / cli.COMMANDS["two-stage"]).exists()
