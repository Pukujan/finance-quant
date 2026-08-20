"""CLI entrypoint for Trial Gate V0: validate a trial artifact JSON file."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from finance_quant.gate import check_trial_artifact_file


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help", "help"}:
        print("usage: trial-gate <artifact.json>")
        return 0
    result = check_trial_artifact_file(argv[0])
    for v in result.violations:
        print(f"VIOLATION: {v}", file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
