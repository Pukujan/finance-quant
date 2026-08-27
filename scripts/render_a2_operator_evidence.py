from __future__ import annotations

import argparse
import json
from pathlib import Path

from finance_quant.trader.evidence import ReplayableAccountStore
from finance_quant.trader.operator import build_operator_snapshot, render_operator_html

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--html-out", type=Path, required=True)
    args = parser.parse_args(argv)
    project = json.loads((ROOT / "contracts/project/project-state.json").read_text(encoding="utf-8"))
    with ReplayableAccountStore(args.db) as store:
        snapshot = build_operator_snapshot(store, project["authority"])
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.html_out.write_text(render_operator_html(snapshot), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
