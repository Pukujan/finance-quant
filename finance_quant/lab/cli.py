"""CLI for the fixed research laboratory.

Usage:
    python -m finance_quant lab run candidate-set.json --state-dir .lab-state --parallel 8
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
    TemporalLaneDatum,
    canonical_json,
    freeze_snapshot,
)
from .runner import run_batch


def _arm(raw: Mapping[str, Any]) -> ArmSpec:
    return ArmSpec(
        arm_id=str(raw["arm_id"]),
        lanes=tuple(str(x) for x in raw["lanes"]),
        knowledge_manifest_hash=str(raw["knowledge_manifest_hash"]),
        executor_ref=str(raw["executor_ref"]),
        model_config_json=canonical_json(raw.get("model_config", {})),
        retrieval_policy_json=canonical_json(raw.get("retrieval_policy", {})),
        feature_projection_json=canonical_json(raw.get("feature_projection", {})),
        portfolio_policy_json=canonical_json(raw.get("portfolio_policy", {})),
    )


def load_candidate_set(path: str | Path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_batch = payload["batch"]
    arms = tuple(_arm(item) for item in raw_batch["arms"])
    batch = ExperimentBatchSpec(
        experiment_id=str(raw_batch["experiment_id"]),
        code_sha=str(raw_batch["code_sha"]),
        env_lock_hash=str(raw_batch["env_lock_hash"]),
        dataset_manifest_hash=str(raw_batch["dataset_manifest_hash"]),
        split_policy_ref=str(raw_batch["split_policy_ref"]),
        cost_model_ref=str(raw_batch["cost_model_ref"]),
        seeds=tuple(int(x) for x in raw_batch["seeds"]),
        outcome_horizon=str(raw_batch["outcome_horizon"]),
        arms=arms,
    )

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
    return batch, tuple(snapshots), outcomes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="finance-quant lab")
    sub = parser.add_subparsers(dest="lab_command", required=True)
    run = sub.add_parser("run", help="Run a declarative candidate-set JSON through the fixed lab")
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
    batch, snapshots, outcomes = load_candidate_set(args.candidate_set)
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
