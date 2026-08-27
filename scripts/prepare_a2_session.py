from __future__ import annotations

import argparse
import json
from pathlib import Path

from finance_quant.trader.evidence import ReplayableAccountStore
from finance_quant.trader.stateful import plan_stateful_session


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--fixture-out", type=Path, required=True)
    parser.add_argument("--evidence-out", type=Path, required=True)
    args = parser.parse_args(argv)
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    if args.db.exists():
        store = ReplayableAccountStore(args.db)
    else:
        store = ReplayableAccountStore(args.db, initial_cash=spec["initial_cash"])
    with store:
        fixture, evidence = plan_stateful_session(store, spec)
    args.fixture_out.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_out.parent.mkdir(parents=True, exist_ok=True)
    args.fixture_out.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.evidence_out.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
