from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

from scripts.run_lean_a1_fill_probe import load_probe_result, verify_probe

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "fixtures/execution/a1-lean-fill-probe-v1.json"
PIN_PATH = ROOT / "contracts/execution/lean-a1-candidate-pin-v1.json"


def _fail_closed(fault_class: str, detail: str) -> dict[str, Any]:
    return {
        "fault_class": fault_class,
        "disposition": "FAIL_CLOSED",
        "detail": detail,
        "authority": "NONE",
    }


def run_candidate_process(
    command: Sequence[str], *, timeout_seconds: float
) -> dict[str, Any]:
    """Run an A1 candidate subprocess and classify process-boundary failures fail-closed."""
    try:
        completed = subprocess.run(
            list(command),
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as exc:
        return _fail_closed("dependency_missing", str(exc))
    except subprocess.TimeoutExpired:
        return _fail_closed("timeout", f"exceeded {timeout_seconds} seconds")

    if completed.returncode != 0:
        return {
            **_fail_closed("nonzero_exit", f"candidate exited {completed.returncode}"),
            "exit_code": completed.returncode,
        }
    return {
        "fault_class": None,
        "disposition": "PROCESS_OK",
        "exit_code": 0,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "authority": "NONE",
    }


def validate_persisted_evidence(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    """Reject malformed or semantically changed persisted candidate evidence."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("persisted LEAN evidence is unreadable or malformed") from exc
    if not isinstance(value, dict) or value != expected:
        raise ValueError("persisted LEAN evidence does not match recomputed authoritative evidence")
    return value


def _public_probe() -> dict[str, Any]:
    return {
        "engine": "LEAN",
        "probe_scope": "EquityFillModel.MarketOnOpenFill",
        "status": "FILLED",
        "instrument_id": "AAA",
        "fill_quantity": "5",
        "fill_price": "11",
        "fill_time": "2026-06-02T13:30:00Z",
        "source_event_id": "bar-2",
    }


def run_fault_campaign() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    nonzero = run_candidate_process(
        [sys.executable, "-c", "import sys; sys.exit(23)"], timeout_seconds=5.0
    )
    assert nonzero["disposition"] == "FAIL_CLOSED" and nonzero["fault_class"] == "nonzero_exit"
    cases.append(nonzero)

    timeout = run_candidate_process(
        [sys.executable, "-c", "import time; time.sleep(2)"], timeout_seconds=0.05
    )
    assert timeout["disposition"] == "FAIL_CLOSED" and timeout["fault_class"] == "timeout"
    cases.append(timeout)

    missing = run_candidate_process(
        ["finance-quant-intentionally-missing-a1-dependency"], timeout_seconds=1.0
    )
    assert missing["disposition"] == "FAIL_CLOSED" and missing["fault_class"] == "dependency_missing"
    cases.append(missing)

    with tempfile.TemporaryDirectory(prefix="fq-a1-lean-fault-") as tmp:
        tmp_path = Path(tmp)

        corrupt_process = run_candidate_process(
            [sys.executable, "-c", "print('corrupted candidate stdout')"], timeout_seconds=5.0
        )
        assert corrupt_process["disposition"] == "PROCESS_OK"
        raw_path = tmp_path / "corrupt-probe.out"
        raw_path.write_text(str(corrupt_process["stdout"]), encoding="utf-8")
        try:
            load_probe_result(raw_path)
        except ValueError as exc:
            cases.append(_fail_closed("candidate_output_corruption", str(exc)))
        else:
            raise AssertionError("corrupted candidate stdout was accepted")

        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
        expected = verify_probe(_public_probe(), fixture, pin)
        corrupt_evidence = dict(expected)
        corrupt_evidence["semantic_conformance"] = "PASS_BUT_CORRUPTED"
        evidence_path = tmp_path / "corrupt-evidence.json"
        evidence_path.write_text(
            json.dumps(corrupt_evidence, sort_keys=True) + "\n", encoding="utf-8"
        )
        try:
            validate_persisted_evidence(evidence_path, expected)
        except ValueError as exc:
            cases.append(_fail_closed("persisted_evidence_corruption", str(exc)))
        else:
            raise AssertionError("corrupted persisted candidate evidence was accepted")

    expected_faults = {
        "nonzero_exit",
        "timeout",
        "dependency_missing",
        "candidate_output_corruption",
        "persisted_evidence_corruption",
    }
    observed_faults = {str(case["fault_class"]) for case in cases}
    assert observed_faults == expected_faults
    assert all(case["disposition"] == "FAIL_CLOSED" for case in cases)

    return {
        "schema_version": "1.0.0",
        "issue": 15,
        "phase": "A1",
        "gate": "LEAN_PROCESS_CHAOS_FAULT",
        "candidate": "LEAN",
        "properties": ["FQ-PROP-021", "FQ-PROP-022"],
        "fault_classes": sorted(expected_faults),
        "cases": cases,
        "status": "PASS",
        "runtime_disposition": "PENDING",
        "authority": "NONE",
        "sealed_holdout_access": "DENIED_TO_ORDINARY_AGENTS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="A1 LEAN process-boundary chaos/fault campaign")
    parser.add_argument("--output", type=Path, default=Path("a1-lean-process-fault-receipt.json"))
    args = parser.parse_args()
    receipt = run_fault_campaign()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "fault_classes": receipt["fault_classes"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())