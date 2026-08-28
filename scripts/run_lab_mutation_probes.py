"""Targeted source mutation probes for the fixed research laboratory.

This is intentionally small and semantic rather than repo-wide mutation testing.
Each probe injects one realistic corruption into the checked-out source, runs the
single public test that must detect it in a fresh Python process, then restores
the exact original bytes. A surviving mutant is a CI failure.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Probe:
    name: str
    path: str
    old: str
    new: str
    test: str


PROBES = (
    Probe(
        "future-known PIT filter removed",
        "finance_quant/lab/core.py",
        "        if _parse_time(self.known_at) > decision:\n            return False",
        "        if False and _parse_time(self.known_at) > decision:\n            return False",
        "tests/test_lab_control_plane.py::test_future_known_data_cannot_change_prior_frozen_snapshot",
    ),
    Probe(
        "same-lane component versions collapsed",
        "finance_quant/lab/core.py",
        "        key = item.component_key\n",
        "        key = (item.lane, \"__collapsed__\")\n",
        "tests/test_lab_control_plane.py::test_multiple_versions_of_same_lane_run_side_by_side_against_same_outcome",
    ),
    Probe(
        "direct snapshot future-known guard removed",
        "finance_quant/lab/core.py",
        "            if _parse_time(item.known_at) > decision:\n                raise LabError(f\"future-known component {item.component_key!r} leaked into snapshot\")",
        "            if False and _parse_time(item.known_at) > decision:\n                raise LabError(f\"future-known component {item.component_key!r} leaked into snapshot\")",
        "tests/test_lab_control_plane.py::test_snapshot_rejects_future_known_component_if_bypassing_freeze",
    ),
    Probe(
        "exact component membership guard removed",
        "finance_quant/lab/core.py",
        "    if missing:\n        raise LabError(f\"snapshot missing arm components: {missing}\")",
        "    if False and missing:\n        raise LabError(f\"snapshot missing arm components: {missing}\")",
        "tests/test_lab_manifest_guard.py::test_arm_cannot_select_an_artifact_not_present_in_frozen_snapshot",
    ),
    Probe(
        "canonical outcome coverage guard removed",
        "finance_quant/lab/runner.py",
        "    if expected_keys != set(outcome_by_key):\n",
        "    if False and expected_keys != set(outcome_by_key):\n",
        "tests/test_lab_control_plane.py::test_canonical_outcome_coverage_must_be_exact",
    ),
    Probe(
        "evaluation identity stopped depending on realized outcomes",
        "finance_quant/lab/runner.py",
        "            \"outcome_ids\": sorted(outcome.outcome_id for outcome in outcomes),",
        "            \"outcome_ids\": [],",
        "tests/test_lab_evaluation_identity.py::test_actual_outcome_and_snapshot_content_are_part_of_run_identity",
    ),
    Probe(
        "router allowed unresolved future outcomes",
        "finance_quant/lab/runner.py",
        "        if _parse_time(score.outcome_time) <= _parse_time(decision_time):\n            rewards[score.arm_id] += score.strategy_net_return",
        "        if True:\n            rewards[score.arm_id] += score.strategy_net_return",
        "tests/test_lab_control_plane.py::test_router_cannot_learn_from_outcome_that_has_not_resolved_yet",
    ),
    Probe(
        "candidate benchmark-data rejection removed",
        "finance_quant/lab/cli.py",
        "    forbidden = {\"snapshots\", \"outcomes\", \"labels\", \"benchmark\", \"experiment\"} & set(payload)",
        "    forbidden = set()",
        "tests/test_lab_control_plane.py::test_candidate_file_cannot_smuggle_outcomes",
    ),
    Probe(
        "shadow account restart re-applies initial cash",
        "finance_quant/lab/shadow.py",
        "        if path.exists():\n            return VirtualAccountStore(path)\n        return VirtualAccountStore(path, initial_cash=self.initial_cash)",
        "        return VirtualAccountStore(path, initial_cash=self.initial_cash)",
        "tests/test_lab_shadow.py::test_shadow_accounts_are_isolated_restartable_and_idempotent",
    ),
)


def run_probe(probe: Probe) -> tuple[bool, str]:
    path = ROOT / probe.path
    original = path.read_text(encoding="utf-8")
    count = original.count(probe.old)
    if count != 1:
        return False, f"mutation anchor count={count}; expected exactly one"

    mutated = original.replace(probe.old, probe.new, 1)
    path.write_text(mutated, encoding="utf-8")
    # Ensure source timestamp moves before the fresh interpreter starts.
    time.sleep(0.02)
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, "-B", "-m", "pytest", probe.test, "-q", "--cache-clear"],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    finally:
        path.write_text(original, encoding="utf-8")

    if result.returncode == 0:
        return False, "mutant survived; targeted test still passed\n" + result.stdout[-4000:]
    return True, result.stdout[-1000:]


def main() -> int:
    survivors: list[tuple[str, str]] = []
    for probe in PROBES:
        killed, detail = run_probe(probe)
        status = "KILLED" if killed else "SURVIVED"
        print(f"[{status}] {probe.name} -> {probe.test}")
        if not killed:
            survivors.append((probe.name, detail))

    print(f"mutation_probes={len(PROBES)} killed={len(PROBES) - len(survivors)} survived={len(survivors)}")
    if survivors:
        for name, detail in survivors:
            print(f"\nSURVIVOR: {name}\n{detail}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
