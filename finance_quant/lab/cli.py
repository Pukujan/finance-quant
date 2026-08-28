"""CLI for the fixed research laboratory.

Usage:
    python -m finance_quant lab run benchmark.json candidates.json \
        --state-dir .lab-state --parallel 8

The benchmark owns historical snapshots/outcomes. Candidate files own arms only.
Each arm selects exact versioned component artifacts; its knowledge manifest is
derived by the control plane rather than supplied by candidate code.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from finance_quant.experiments.ledger import ExperimentLedger

from .core import (
    ArmSpec,
    CanonicalOutcome,
    ExperimentBatchSpec,
    LabError,
    TemporalLaneDatum,
    canonical_json,
    freeze_snapshot,
)
from .runner import run_batch


def _components(raw: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    if "lanes" in raw or "knowledge_manifest_hash" in raw:
        raise LabError(
            "candidate arms must declare exact components; legacy lanes/knowledge_manifest_hash are not accepted"
        )
    rows = raw.get("components")
    if not isinstance(rows, list) or not rows:
        raise LabError("candidate arm must declare a non-empty components list")
    components: list[tuple[str, str]] = []
    for item in rows:
        if not isinstance(item, Mapping):
            raise LabError("each candidate component must be an object with lane and artifact_hash")
        lane = str(item.get("lane", ""))
        artifact_hash = str(item.get("artifact_hash", ""))
        if not lane or not artifact_hash:
            raise LabError("candidate component lane and artifact_hash are required")
        components.append((lane, artifact_hash))
    return tuple(components)


def _arm(raw: Mapping[str, Any]) -> ArmSpec:
    return ArmSpec(
        arm_id=str(raw["arm_id"]),
        components=_components(raw),
        executor_ref=str(raw["executor_ref"]),
        model_config_json=canonical_json(raw.get("model_config", {})),
        retrieval_policy_json=canonical_json(raw.get("retrieval_policy", {})),
        feature_projection_json=canonical_json(raw.get("feature_projection", {})),
        portfolio_policy_json=canonical_json(raw.get("portfolio_policy", {})),
    )


def load_candidates(path: str | Path) -> tuple[ArmSpec, ...]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    forbidden = {"snapshots", "outcomes", "labels", "benchmark", "experiment"} & set(payload)
    if forbidden:
        raise LabError(f"candidate file cannot own benchmark data: {sorted(forbidden)}")
    arms = tuple(_arm(item) for item in payload.get("arms", ()))
    if not arms:
        raise LabError("candidate file must declare at least one arm")
    return arms


def load_benchmark(path: str | Path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if "arms" in payload:
        raise LabError("benchmark file cannot declare candidate arms")
    raw = payload["experiment"]

    snapshots = []
    for row in payload["snapshots"]:
        data = tuple(
            TemporalLaneDatum.from_payload(
                str(item["lane"]),
                str(item["artifact_hash"]),
                str(item["known_at"]),
                item["payload"],
                valid_from=str(item["valid_from"]) if item.get("valid_from") is not None else None,
                valid_to=str(item["valid_to"]) if item.get("valid_to") is not None else None,
            )
            for item in row["data"]
        )
        snapshots.append(
            freeze_snapshot(
                str(row["entity"]),
                str(row["decision_time"]),
                str(row["horizon"]),
                data,
            )
        )

    outcomes = tuple(
        CanonicalOutcome(
            str(row["entity"]),
            str(row["decision_time"]),
            str(row["outcome_time"]),
            str(row["horizon"]),
            float(row["realized_return"]),
            float(row.get("cost_bps", 0.0)),
        )
        for row in payload["outcomes"]
    )
    return raw, tuple(snapshots), outcomes


def load_execution(benchmark_path: str | Path, candidate_path: str | Path):
    raw, snapshots, outcomes = load_benchmark(benchmark_path)
    arms = load_candidates(candidate_path)
    batch = ExperimentBatchSpec(
        experiment_id=str(raw["experiment_id"]),
        code_sha=str(raw["code_sha"]),
        env_lock_hash=str(raw["env_lock_hash"]),
        dataset_manifest_hash=str(raw["dataset_manifest_hash"]),
        split_policy_ref=str(raw["split_policy_ref"]),
        cost_model_ref=str(raw["cost_model_ref"]),
        seeds=tuple(int(x) for x in raw["seeds"]),
        outcome_horizon=str(raw["outcome_horizon"]),
        arms=arms,
    )
    return batch, snapshots, outcomes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="finance-quant lab")
    sub = parser.add_subparsers(dest="lab_command", required=True)
    run = sub.add_parser("run", help="Run candidate arms against a separate fixed benchmark")
    run.add_argument("benchmark")
    run.add_argument("candidate_set")
    run.add_argument("--state-dir", default=".lab-state")
    run.add_argument("--parallel", type=int, default=1)
    run.add_argument("--output", default="")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.lab_command != "run":
        return 2
    state = Path(args.state_dir)
    state.mkdir(parents=True, exist_ok=True)
    batch, snapshots, outcomes = load_execution(args.benchmark, args.candidate_set)
    ledger = ExperimentLedger(state / "experiments.sqlite")
    try:
        result = run_batch(batch, snapshots, outcomes, max_workers=args.parallel, ledger=ledger)
    finally:
        ledger.close()
    text = json.dumps(result.to_dict(), sort_keys=True, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0
