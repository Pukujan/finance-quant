from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

from finance_quant.execution.differential import DifferentialConformanceError
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


def _recovered_committed(fault_class: str, detail: str) -> dict[str, Any]:
    return {
        "fault_class": fault_class,
        "disposition": "RECOVERED_COMMITTED",
        "detail": detail,
        "authority": "NONE",
    }


def run_candidate_process(
    command: Sequence[str], *, timeout_seconds: float, nonzero_fault_class: str = "nonzero_exit"
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
            **_fail_closed(nonzero_fault_class, f"candidate exited {completed.returncode}"),
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


def _expect_probe_failure(
    fault_class: str,
    probe: dict[str, Any],
    fixture: dict[str, Any],
    pin: dict[str, Any],
) -> dict[str, Any]:
    try:
        verify_probe(probe, fixture, pin)
    except (DifferentialConformanceError, KeyError, ValueError) as exc:
        return _fail_closed(fault_class, str(exc))
    raise AssertionError(f"{fault_class} probe fault was accepted")


def run_fault_campaign() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    nonzero = run_candidate_process(
        [sys.executable, "-c", "import sys; sys.exit(23)"], timeout_seconds=5.0
    )
    assert nonzero["disposition"] == "FAIL_CLOSED" and nonzero["fault_class"] == "nonzero_exit"
    cases.append(nonzero)

    runtime_exception = run_candidate_process(
        [sys.executable, "-c", "raise RuntimeError('injected A1 runtime exception')"],
        timeout_seconds=5.0,
        nonzero_fault_class="runtime_exception",
    )
    assert runtime_exception["disposition"] == "FAIL_CLOSED"
    assert runtime_exception["fault_class"] == "runtime_exception"
    cases.append(runtime_exception)

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

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    expected = verify_probe(_public_probe(), fixture, pin)

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

        duplicate_path = tmp_path / "duplicate-delivery.out"
        duplicate_line = json.dumps(_public_probe(), sort_keys=True)
        duplicate_path.write_text(f"{duplicate_line}\n{duplicate_line}\n", encoding="utf-8")
        try:
            load_probe_result(duplicate_path)
        except ValueError as exc:
            cases.append(_fail_closed("duplicate_delivery", str(exc)))
        else:
            raise AssertionError("duplicate production result delivery was accepted")

        malformed_probe = _public_probe()
        malformed_probe.pop("fill_price")
        cases.append(_expect_probe_failure("malformed_payload", malformed_probe, fixture, pin))

        reordered_probe = {
            **_public_probe(),
            "fill_price": "10",
            "fill_time": "2026-06-01T20:00:00Z",
            "source_event_id": "bar-1",
        }
        cases.append(_expect_probe_failure("invalid_reorder", reordered_probe, fixture, pin))

        dropped_event_probe = {
            **_public_probe(),
            "fill_time": "2026-06-01T20:00:00Z",
            "source_event_id": "bar-1",
        }
        cases.append(_expect_probe_failure("dropped_event", dropped_event_probe, fixture, pin))

        crash_before_path = tmp_path / "crash-before-commit.json"
        crash_before = run_candidate_process(
            [sys.executable, "-c", "import sys; sys.exit(71)"],
            timeout_seconds=5.0,
            nonzero_fault_class="crash_before_commit",
        )
        assert not crash_before_path.exists()
        assert crash_before["fault_class"] == "crash_before_commit"
        cases.append(crash_before)

        crash_after_path = tmp_path / "crash-after-commit.json"
        crash_after_path.write_text(json.dumps(expected, sort_keys=True) + "\n", encoding="utf-8")
        crash_after = run_candidate_process(
            [sys.executable, "-c", "import sys; sys.exit(72)"],
            timeout_seconds=5.0,
            nonzero_fault_class="crash_after_commit",
        )
        assert crash_after["fault_class"] == "crash_after_commit"
        validate_persisted_evidence(crash_after_path, expected)
        cases.append(
            _recovered_committed(
                "crash_after_commit",
                "candidate crashed after exact authoritative evidence commit; committed evidence revalidated",
            )
        )

        validate_persisted_evidence(crash_after_path, expected)
        cases.append(
            _recovered_committed(
                "restart_replay",
                "restart accepted only the exact committed authoritative evidence",
            )
        )

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
            cases.append(_fail_closed("persisted_state_corruption", str(exc)))
        else:
            raise AssertionError("corrupted persisted candidate evidence was accepted")

    expected_faults = {
        "nonzero_exit",
        "runtime_exception",
        "timeout",
        "dependency_missing",
        "candidate_output_corruption",
        "duplicate_delivery",
        "malformed_payload",
        "invalid_reorder",
        "dropped_event",
        "crash_before_commit",
        "crash_after_commit",
        "restart_replay",
        "persisted_evidence_corruption",
        "persisted_state_corruption",
    }
    observed_faults = {str(case["fault_class"]) for case in cases}
    assert observed_faults == expected_faults
    assert all(case["authority"] == "NONE" for case in cases)
    assert all(
        case["disposition"] == "FAIL_CLOSED"
        for case in cases
        if case["fault_class"] not in {"crash_after_commit", "restart_replay"}
    )
    assert all(
        case["disposition"] == "RECOVERED_COMMITTED"
        for case in cases
        if case["fault_class"] in {"crash_after_commit", "restart_replay"}
    )

    return {
        "schema_version": "1.0.0",
        "issue": 15,
        "phase": "A1",
        "gate": "LEAN_PROCESS_CHAOS_FAULT",
        "candidate": "LEAN",
        "properties": ["FQ-PROP-015", "FQ-PROP-018", "FQ-PROP-021", "FQ-PROP-022"],
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
