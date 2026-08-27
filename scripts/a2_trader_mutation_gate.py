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
    Mutant("A2-ACCOUNT-OVERFILL-BYPASS", "critical", "finance_quant/trader/account.py", "if new_filled > order_qty:", "if False and new_filled > order_qty:", "tests/test_a2_account.py::test_fq_prop_024_fill_requires_order_and_cannot_overfill"),
    Mutant("A2-ACCOUNT-DUP-FILL-BYPASS", "critical", "finance_quant/trader/account.py", "if dict(prior) != fill:", "if False and dict(prior) != fill:", "tests/test_a2_account.py::test_fq_prop_028_duplicate_fill_is_idempotent_and_reopen_is_stable"),
    Mutant("A2-ACCOUNT-RESET-BYPASS", "critical", "finance_quant/trader/account.py", "if requested != str(row[\"cash\"]):", "if False and requested != str(row[\"cash\"]):", "tests/test_a2_account.py::test_existing_account_cannot_be_silently_reset"),
    Mutant("A2-SESSION-PARENT-BYPASS", "critical", "finance_quant/trader/session.py", "if current.parent_receipt_hash != previous.receipt_hash:", "if False and current.parent_receipt_hash != previous.receipt_hash:", "tests/test_a2_session.py::test_fq_prop_025_session_chain_requires_exact_continuity"),
    Mutant("A2-SESSION-STATE-BYPASS", "critical", "finance_quant/trader/session.py", "if current.initial_state_hash != previous.terminal_state_hash:", "if False and current.initial_state_hash != previous.terminal_state_hash:", "tests/test_a2_session.py::test_fq_prop_025_session_chain_requires_exact_continuity"),
    Mutant("A2-SESSION-HASH-BYPASS", "critical", "finance_quant/trader/session.py", "if self.receipt_hash != _canonical_hash(self.payload()):", "if False and self.receipt_hash != _canonical_hash(self.payload()):", "tests/test_a2_session.py::test_tampered_journal_fails_closed"),
    Mutant("A2-STRATEGY-KNOWNAT-BYPASS", "critical", "finance_quant/trader/strategy.py", "if event_time <= decision_dt and known_at <= decision_dt:", "if event_time <= decision_dt:", "tests/test_a2_strategy.py::test_fq_prop_030_future_or_late_known_events_cannot_change_prior_decision"),
    Mutant("A2-STRATEGY-EVENTTIME-BYPASS", "critical", "finance_quant/trader/strategy.py", "if event_time <= decision_dt and known_at <= decision_dt:", "if known_at <= decision_dt:", "tests/test_a2_strategy.py::test_future_event_is_excluded_even_if_its_knowledge_timestamp_is_early"),
    Mutant("A2-RISK-REJECTED-INTENT-BYPASS", "critical", "finance_quant/trader/risk.py", "approved = intent if decision.status == \"APPROVED\" else None", "approved = intent", "tests/test_a2_strategy.py::test_risk_gate_binds_strategy_intent_and_never_changes_it"),
    Mutant("A2-AUTH-LIVE-BYPASS", "critical", "finance_quant/trader/authority.py", "if project_authority.get(\"live_capital_enabled\") is not False:", "if False and project_authority.get(\"live_capital_enabled\") is not False:", "tests/test_a2_authority.py::test_live_capital_is_rejected_even_with_otherwise_valid_a2_promotion"),
    Mutant("A2-AUTH-HITL-BYPASS", "critical", "finance_quant/trader/authority.py", "if promotion is None:", "if False and promotion is None:", "tests/test_a2_authority.py::test_durable_paper_authority_still_requires_explicit_a2_hitl_receipt"),
    Mutant("A2-AUTH-SCOPE-BYPASS", "critical", "finance_quant/trader/authority.py", "if promotion.issue != 16 or promotion.phase != \"A2\" or promotion.decision != \"APPROVE\":", "if False and (promotion.issue != 16 or promotion.phase != \"A2\" or promotion.decision != \"APPROVE\"):", "tests/test_a2_authority.py::test_wrong_phase_or_issue_promotion_is_rejected_when_project_is_paper_ready"),
    Mutant("A2-EXEC-RUNTIME-PIN-BYPASS", "critical", "finance_quant/trader/execution.py", "if runtime_commit != A2_LEAN_COMMIT:", "if False and runtime_commit != A2_LEAN_COMMIT:", "tests/test_a2_execution_session.py::test_fixture_binding_and_runtime_pin_fail_closed_before_account_mutation"),
    Mutant("A2-EXEC-FIXTURE-BINDING-BYPASS", "critical", "finance_quant/trader/execution.py", "if receipt.get(\"input_hash\") != _fixture_hash(fixture):", "if False and receipt.get(\"input_hash\") != _fixture_hash(fixture):", "tests/test_a2_execution_session.py::test_fixture_binding_and_runtime_pin_fail_closed_before_account_mutation"),
    Mutant("A2-EXEC-TERMINAL-RECON-BYPASS", "critical", "finance_quant/trader/execution.py", "store.assert_terminal_matches(cash=receipt[\"cash\"], positions=list(receipt.get(\"positions\", [])))", "_ = (receipt[\"cash\"], receipt.get(\"positions\", []))", "tests/test_a2_execution_session.py::test_reconciliation_failure_rolls_back_entire_execution_receipt"),
]

THRESHOLDS = {"critical": 0.98, "high": 0.95}


def _purge_module_bytecode(path: Path) -> None:
    cache = path.parent / "__pycache__"
    if cache.is_dir():
        for pyc in cache.glob(f"{path.stem}.*.pyc"):
            pyc.unlink()


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
    parser = argparse.ArgumentParser(description="A2 source mutation gate for trader authority/account/session surfaces")
    parser.add_argument("--output", type=Path, default=Path("a2-mutation-receipt.json"))
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
        raise SystemExit("baseline A2 mutation oracles are not green")

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
            _purge_module_bytecode(path)
            try:
                completed = _run_pytest(mutant.oracle)
                killed = completed.returncode != 0
                results.append({
                    **asdict(mutant),
                    "status": "KILLED" if killed else "SURVIVED",
                    "oracle_returncode": completed.returncode,
                    "oracle_output_tail": completed.stdout[-2000:],
                })
            finally:
                path.write_text(original, encoding="utf-8")
                _purge_module_bytecode(path)
    finally:
        for path, original in originals.items():
            path.write_text(original, encoding="utf-8")
            _purge_module_bytecode(path)

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
        if rate < threshold or (severity == "critical" and survivors):
            failed = True

    receipt = {
        "schema_version": "1.0.0",
        "phase": "A2",
        "issue": 16,
        "gate": "MUTATION",
        "policy": {
            "critical_minimum_valid_mutant_kill_rate": 0.98,
            "high_minimum_valid_mutant_kill_rate": 0.95,
            "critical_invariant_bypass_survivor_allowed": False,
        },
        "summary": summary,
        "mutants": results,
        "status": "PASS" if not failed else "FAIL",
        "authority": "NONE",
    }
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt["summary"], indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
