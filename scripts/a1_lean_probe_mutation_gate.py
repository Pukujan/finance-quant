from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts/run_lean_a1_fill_probe.py"
ORACLE = "tests/test_a1_lean_probe_assurance.py"


@dataclass(frozen=True)
class Mutant:
    mutant_id: str
    severity: str
    old: str
    new: str


MUTANTS = [
    Mutant(
        "A1-LEAN-UNKNOWN-STDOUT-BYPASS",
        "critical",
        '_TRACE_PREFIX = "TRACE::"',
        '_TRACE_PREFIX = ""',
    ),
    Mutant(
        "A1-LEAN-TRACE-LEADER-BYPASS",
        "critical",
        "return bool(match and line[match.end() :].startswith(_TRACE_PREFIX))",
        "return _TRACE_PREFIX in line",
    ),
    Mutant(
        "A1-LEAN-EXTRA-JSON-BYPASS",
        "critical",
        "if len(matches) != 1 or len(candidates) != 1:",
        "if len(matches) != 1:",
    ),
    Mutant(
        "A1-LEAN-ENGINE-GUARD-BYPASS",
        "critical",
        'if probe.get("engine") != _EXPECTED_ENGINE:',
        'if False and probe.get("engine") != _EXPECTED_ENGINE:',
    ),
    Mutant(
        "A1-LEAN-CREDENTIAL-GUARD-BYPASS",
        "critical",
        'if pin.get("credentials_required") is not False or pin.get("cli_used") is not False:',
        'if False and (pin.get("credentials_required") is not False or pin.get("cli_used") is not False):',
    ),
]


def _purge_bytecode() -> None:
    cache = TARGET.parent / "__pycache__"
    if cache.is_dir():
        for pyc in cache.glob(f"{TARGET.stem}.*.pyc"):
            pyc.unlink()


def _pytest() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", ORACLE],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="A1 mutation gate for the LEAN production probe normalizer")
    parser.add_argument("--output", type=Path, default=Path("a1-lean-mutation-receipt.json"))
    args = parser.parse_args()

    baseline = _pytest()
    if baseline.returncode != 0:
        print(baseline.stdout)
        raise SystemExit("LEAN probe mutation baseline is not green")

    original = TARGET.read_text(encoding="utf-8")
    results: list[dict[str, object]] = []
    try:
        for mutant in MUTANTS:
            if original.count(mutant.old) != 1:
                raise SystemExit(f"{mutant.mutant_id}: mutation anchor must occur exactly once")
            mutated = original.replace(mutant.old, mutant.new, 1)
            compile(mutated, str(TARGET), "exec")
            TARGET.write_text(mutated, encoding="utf-8")
            _purge_bytecode()
            try:
                completed = _pytest()
                killed = completed.returncode != 0
                results.append(
                    {
                        **asdict(mutant),
                        "status": "KILLED" if killed else "SURVIVED",
                        "oracle_returncode": completed.returncode,
                        "oracle_output_tail": completed.stdout[-2000:],
                    }
                )
            finally:
                TARGET.write_text(original, encoding="utf-8")
                _purge_bytecode()
    finally:
        TARGET.write_text(original, encoding="utf-8")
        _purge_bytecode()

    killed = sum(item["status"] == "KILLED" for item in results)
    rate = killed / len(results)
    survivors = [item["mutant_id"] for item in results if item["status"] == "SURVIVED"]
    failed = rate < 0.98 or bool(survivors)
    receipt = {
        "schema_version": "1.0.0",
        "phase": "A1",
        "issue": 15,
        "gate": "LEAN_PROBE_MUTATION",
        "properties": ["FQ-PROP-015", "FQ-PROP-019", "FQ-PROP-021"],
        "authority": "NONE",
        "sealed_holdout_access": "DENIED_TO_ORDINARY_AGENTS",
        "valid_mutants": len(results),
        "killed": killed,
        "kill_rate": rate,
        "required_kill_rate": 0.98,
        "critical_invariant_bypass_survivor_allowed": False,
        "survivors": survivors,
        "mutants": results,
        "status": "FAIL" if failed else "PASS",
    }
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("status", "kill_rate", "survivors")}, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())