from unittest import mock

from finance_quant.__main__ import COMMANDS, main


def test_help_shows_subcommands(capsys):
    rc = main(["--help"])
    assert rc == 0
    captured = capsys.readouterr()
    for cmd in COMMANDS:
        assert cmd in captured.out


def test_unknown_command_returns_nonzero():
    rc = main(["bogus-command"])
    assert rc != 0


def test_unknown_command_prints_error(capsys):
    main(["bogus-command"])
    captured = capsys.readouterr()
    assert "error" in captured.err.lower() or "unrecognized" in captured.err.lower()


def test_dispatch_verify_monkeypatch(capsys):
    with mock.patch("finance_quant.__main__._run_script", return_value=0) as fake:
        rc = main(["verify"])
        assert rc == 0
        fake.assert_called_once()
        args, _ = fake.call_args
        assert args[0] == COMMANDS["verify"]


def test_dispatch_freeze_monkeypatch(capsys):
    with mock.patch("finance_quant.__main__._run_script", return_value=0) as fake:
        rc = main(["freeze"])
        assert rc == 0
        fake.assert_called_once()
        args, _ = fake.call_args
        assert args[0] == COMMANDS["freeze"]


def test_dispatch_benchmark_monkeypatch(capsys):
    with mock.patch("finance_quant.__main__._run_script", return_value=0) as fake:
        rc = main(["benchmark"])
        assert rc == 0
        fake.assert_called_once()
        args, _ = fake.call_args
        assert args[0] == COMMANDS["benchmark"]


def test_dispatch_drill_monkeypatch(capsys):
    with mock.patch("finance_quant.__main__._run_script", return_value=0) as fake:
        rc = main(["drill"])
        assert rc == 0
        fake.assert_called_once()
        args, _ = fake.call_args
        assert args[0] == COMMANDS["drill"]
