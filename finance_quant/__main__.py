"""CLI: python -m finance_quant <command>"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

# Backward-compatible mapping used by existing tests.
COMMANDS = {
    "cost-stress": "scripts/run_cost_stress_report.py",
    "mvfi": "scripts/run_phase_b_mvfi.py",
    "fresh-env-drill": "scripts/run_fresh_environment_drill.py",
    "verify": "scripts/verify.py",
    "benchmark": "scripts/run_phase_b_benchmark.py",
    "freeze": "scripts/freeze_fixture.py",
    "drill": "scripts/run_phase_b_determinism_drill.py",
    "pit-bakeoff": "scripts/run_pit_bakeoff.py",
    "b1-b5": "scripts/run_b1_b5_campaign.py",
    "search-batch": "scripts/run_search_batch.py",
    "smoke": "scripts/smoke.py",
    "alpha158": "scripts/alpha158_coverage.py",
    "scorecard": "scripts/run_search_scorecard.py",
    "rank-ic": "scripts/run_rank_ic_report.py",
    "b2-scheduler": "scripts/run_b2_via_scheduler.py",
    "seal-mini": "scripts/write_seal_mini_a.py",
    "two-stage": "scripts/run_two_stage.py",
    "generate-lean": "scripts/generate_lean.py",
    "trial-gate": "scripts/trial_gate.py",
}


def _run_script(script_rel: str, remainder: list[str]) -> int:
    import runpy
    script_path = Path(script_rel)
    if not script_path.exists():
        print(f"script not found: {script_path}", file=sys.stderr)
        return 2
    sys.argv = [str(script_path)] + remainder
    try:
        runpy.run_path(str(script_path), run_name="__main__")
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 0
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    return _run_script(COMMANDS["verify"], args.remainder)


def _cmd_benchmark(args: argparse.Namespace) -> int:
    return _run_script(COMMANDS["benchmark"], args.remainder)


def _cmd_freeze(args: argparse.Namespace) -> int:
    return _run_script(COMMANDS["freeze"], args.remainder)


def _cmd_drill(args: argparse.Namespace) -> int:
    return _run_script(COMMANDS["drill"], args.remainder)


_SUBCOMMAND_HANDLERS = {
    "verify": _cmd_verify,
    "benchmark": _cmd_benchmark,
    "freeze": _cmd_freeze,
    "drill": _cmd_drill,
}


def _cmd_generic(args: argparse.Namespace) -> int:
    """Fall through to the legacy COMMANDS table for any other script."""
    name = args._legacy_name
    script_rel = COMMANDS.get(name)
    if script_rel is None:
        print(f"unknown command {name!r}", file=sys.stderr)
        return 2
    return _run_script(script_rel, args.remainder)


def _cmd_help(args: argparse.Namespace) -> int:
    parser = build_parser()
    parser.print_help()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="finance-quant",
        description="Reproducible quantitative research and trading laboratory",
    )
    sub = parser.add_subparsers(dest="command")

    p_help = sub.add_parser("help", help="Show this help message")
    p_help.set_defaults(func=_cmd_help)

    p_verify = sub.add_parser("verify", help="Run the existing verification suite (pytest + smoke)")
    p_verify.set_defaults(func=_cmd_verify)

    p_bench = sub.add_parser("benchmark", help="Run scripts.run_phase_b_benchmark")
    p_bench.set_defaults(func=_cmd_benchmark)

    p_freeze = sub.add_parser("freeze", help="Run scripts.freeze_fixture")
    p_freeze.set_defaults(func=_cmd_freeze)

    p_drill = sub.add_parser("drill", help="Run scripts.run_phase_b_determinism_drill")
    p_drill.set_defaults(func=_cmd_drill)

    for name in COMMANDS:
        if name not in _SUBCOMMAND_HANDLERS:
            p = sub.add_parser(name, help=f"Run {COMMANDS[name]}")
            p.set_defaults(func=_cmd_generic, _legacy_name=name)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args, remainder = parser.parse_known_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 0
    if args.command is None:
        parser.print_help()
        return 0
    func = args.func
    ns = argparse.Namespace(remainder=remainder)
    if hasattr(args, "_legacy_name"):
        ns._legacy_name = args._legacy_name
    try:
        return func(ns)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
