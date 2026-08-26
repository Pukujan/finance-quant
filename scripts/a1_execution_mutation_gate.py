from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Mutant:
    mutant_id: str
    severity: str
    path: str
    old: str
    new: str
    oracle: str


MUTANTS = [
    Mutant(
        "A1-CONF-AUTHORITY-BYPASS",
        "critical",
        "finance_quant/execution/conformance.py",
        "if authority.get(key) != value:",
        "if False and authority.get(key) != value:",
        "tests/test_execution_conformance.py::test_runtime_contract_is_bound_to_a1_and_fails_closed",
    ),
    Mutant(
        "A1-CONF-MISSING-FIELD-BYPASS",
        "critical",
        "finance_quant/execution/conformance.py",
        "if missing:\n        errors.append(f\"missing required receipt fields: {missing}\")",
        "if False and missing:\n        errors.append(f\"missing required receipt fields: {missing}\")",
        "tests/test_execution_conformance.py::test_receipt_missing_required_field_fails_closed",
    ),
    Mutant(
        "A1-CONF-FORBIDDEN-IDENTITY-BYPASS",
        "critical",
        "finance_quant/execution/conformance.py",
        "if found:\n        errors.append(f\"forbidden identity inputs present: {found}\")",
        "if False and found:\n        errors.append(f\"forbidden identity inputs present: {found}\")",
        "tests/test_execution_conformance.py::test_receipt_forbidden_identity_input_is_rejected_at_any_depth",
    ),
    Mutant(
        "A1-CONF-RUNTIME-STATE-BYPASS",
        "critical",
        "finance_quant/execution/conformance.py",
        "if state not in allowed_states:",
        "if False and state not in allowed_states:",
        "tests/test_execution_conformance.py::test_receipt_rejects_runtime_specific_order_state",
    ),
    Mutant(
        "A1-CONF-SELF-HASH-INCLUDED",
        "high",
        "finance_quant/execution/conformance.py",
        "normalized.pop(\"receipt_hash\", None)",
        "_ = normalized.get(\"receipt_hash\")",
        "tests/test_execution_conformance.py::test_canonical_receipt_hash_is_independent_of_mapping_key_order_and_self_hash",
    ),
    Mutant(
        "A1-REF-SAME-BAR-ELIGIBLE",
        "critical",
        "finance_quant/execution/reference.py",
        "and event[\"event_time\"] > intent[\"created_at\"]",
        "and event[\"event_time\"] >= intent[\"created_at\"]",
        "tests/test_execution_reference.py::test_fq_prop_015_daily_decision_never_fills_same_bar",
    ),
    Mutant(
        "A1-REF-FUTURE-KNOWN-ELIGIBLE",
        "critical",
        "finance_quant/execution/reference.py",
        "and event[\"known_at\"] <= event[\"event_time\"]",
        "and event[\"known_at\"] >= event[\"event_time\"]",
        "tests/test_execution_reference.py::test_fq_prop_019_future_known_event_does_not_influence_earlier_execution",
    ),
    Mutant(
        "A1-REF-ZERO-LIQUIDITY-ELIGIBLE",
        "critical",
        "finance_quant/execution/reference.py",
        "and D(str(event.get(\"payload\", {}).get(\"liquidity\", \"0\"))) > 0",
        "and D(str(event.get(\"payload\", {}).get(\"liquidity\", \"0\"))) >= 0",
        "tests/test_execution_reference.py::test_zero_liquidity_cannot_synthesize_fill",
    ),
    Mutant(
        "A1-REF-PARTIAL-FILL-BYPASS",
        "critical",
        "finance_quant/execution/reference.py",
        "fill_qty = min(qty, available)",
        "fill_qty = qty",
        "tests/test_execution_reference.py::test_fq_prop_016_partial_fill_never_exceeds_order_quantity",
    ),
    Mutant(
        "A1-REF-CLOSE-INSTEAD-OF-OPEN",
        "critical",
        "finance_quant/execution/reference.py",
        "price = D(str(event[\"payload\"][\"open\"]))",
        "price = D(str(event[\"payload\"][\"close\"]))",
        "tests/test_execution_reference.py::test_fq_prop_017_reference_accounting_reconciles_cash_equity_and_nav",
    ),
    Mutant(
        "A1-REF-FEE-OMITTED",
        "critical",
        "finance_quant/execution/reference.py",
        "cash_delta = -(fill_qty * price) - fee if side == \"BUY\" else (fill_qty * price) - fee",
        "cash_delta = -(fill_qty * price) if side == \"BUY\" else (fill_qty * price)",
        "tests/test_execution_reference.py::test_fq_prop_017_reference_accounting_reconciles_cash_equity_and_nav",
    ),
    Mutant(
        "A1-REF-CONFLICTING-DUPLICATE-ACCEPTED",
        "critical",
        "finance_quant/execution/reference.py",
        "if prior is not None and prior != event:",
        "if False and prior is not None and prior != event:",
        "tests/test_execution_reference.py::test_ambiguous_duplicate_event_identity_fails_closed",
    ),
    Mutant(
        "A1-REF-EVENT-ORDER-NONCANONICAL",
        "high",
        "finance_quant/execution/reference.py",
        "return sorted(seen.values(), key=lambda e: (e[\"event_time\"], int(e[\"sequence\"]), e[\"event_id\"]))",
        "return list(seen.values())",
        "tests/test_execution_metamorphic.py::test_metamorphic_event_input_permutation_preserves_receipt",
    ),
]

THRESHOLDS = {"critical": 0.98, "high": 0.95}


def _run_pytest(oracle: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", oracle],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="A1 source mutation gate for execution conformance surfaces")
    parser.add_argument("--output", type=Path, default=Path("a1-mutation-receipt.json"))
    args = parser.parse_args()

    baseline_oracles = sorted({mutant.oracle for mutant in MUTANTS})
    baseline = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *baseline_oracles],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if baseline.returncode != 0:
        print(baseline.stdout)
        raise SystemExit("baseline mutation oracles are not green")

    results: list[dict[str, object]] = []
    originals: dict[Path, str] = {}
    try:
        for mutant in MUTANTS:
            path = ROOT / mutant.path
            original = originals.setdefault(path, path.read_text(encoding="utf-8"))
            if original.count(mutant.old) != 1:
                raise SystemExit(f"{mutant.mutant_id}: mutation anchor must occur exactly once")
            mutated = original.replace(mutant.old, mutant.new, 1)
            compile(mutated, str(path), "exec")
            path.write_text(mutated, encoding="utf-8")
            try:
                completed = _run_pytest(mutant.oracle)
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
                path.write_text(original, encoding="utf-8")
    finally:
        for path, original in originals.items():
            path.write_text(original, encoding="utf-8")

    summary: dict[str, dict[str, object]] = {}
    failed = False
    for severity, threshold in THRESHOLDS.items():
        scoped = [item for item in results if item["severity"] == severity]
        killed = sum(item["status"] == "KILLED" for item in scoped)
        rate = killed / len(scoped) if scoped else 1.0
        survivors = [item["mutant_id"] for item in scoped if item["status"] == "SURVIVED"]
        summary[severity] = {
            "valid_mutants": len(scoped),
            "killed": killed,
            "kill_rate": rate,
            "required_kill_rate": threshold,
            "survivors": survivors,
        }
        if rate < threshold:
            failed = True
        if severity == "critical" and survivors:
            failed = True

    receipt = {
        "phase": "A1",
        "issue": 15,
        "gate": "MUTATION",
        "policy": {
            "critical_minimum_valid_mutant_kill_rate": 0.98,
            "high_minimum_valid_mutant_kill_rate": 0.95,
            "critical_invariant_bypass_survivor_allowed": False,
        },
        "summary": summary,
        "mutants": results,
        "status": "PASS" if not failed else "FAIL",
    }
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt["summary"], indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
