"""CLI: python -m finance_quant <command>"""
from __future__ import annotations

import sys

COMMANDS = {
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
}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print("finance-quant commands:")
        for name, path in COMMANDS.items():
            print(f"  {name:16} {path}")
        return 0
    cmd = argv[0]
    if cmd not in COMMANDS:
        print(f"unknown command {cmd!r}", file=sys.stderr)
        return 2
    print(COMMANDS[cmd])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
