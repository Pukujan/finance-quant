"""CLI for the fixed research laboratory.

Typical autonomous flow:

    finance-quant lab publish-component spec.json payload.json --registry .lab-state/registry
    finance-quant lab assemble-benchmark evaluation.json components.json \
        --registry .lab-state/registry --output benchmark.json
    finance-quant lab run benchmark.json candidates.json \
        --state-dir .lab-state --parallel 8

Canonical outcomes stay in the evaluation/benchmark side. Candidate files own
arms only and select exact immutable component artifacts.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from finance_quant.experiments.ledger import ExperimentLedger

from .benchmark import assemble_benchmark
from .core import (
    ArmSpec,
    CanonicalOutcome,
    ComponentSpec,
    ExperimentBatchSpec,
    LabError,
    TemporalLaneDatum,
    canonical_json,
    freeze_snapshot,
)
from .matrix import expand_arm_matrix
from .registry import ComponentRegistry
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


def _component_spec(raw: Mapping[str, Any]) -> ComponentSpec:
    return ComponentSpec(
        lane=str(raw["lane"]),
        name=str(raw["name"]),
        version=str(raw["version"]),
        code_sha=str(raw["code_sha"]),
        input_dataset_manifest_hash=str(raw["input_dataset_manifest_hash"]),
        schema_version=str(raw.get("schema_version", "1")),
        ontology_version=str(raw.get("ontology_version", "1")),
        model_or_extractor_hash=str(raw.get("model_or_extractor_hash", "")),
        parameters_json=canonical_json(raw.get("parameters", {})),
        knowledge_cut_or_build_range=str(raw.get("knowledge_cut_or_build_range", "")),
        parent_artifact_hashes=tuple(str(x) for x in raw.get("parent_artifact_hashes", ())),
    )


def _json_file(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _emit(payload: Any, output: str = "") -> None:
    text = json.dumps(payload, sort_keys=True, indent=2)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
    print(text)


def load_candidates(path: str | Path) -> tuple[ArmSpec, ...]:
    payload = _json_file(path)
    if not isinstance(payload, Mapping):
        raise LabError("candidate file must contain a JSON object")
    forbidden = {"snapshots", "outcomes", "labels", "benchmark", "experiment"} & set(payload)
    if forbidden:
        raise LabError(f"candidate file cannot own benchmark data: {sorted(forbidden)}")
    explicit = tuple(_arm(item) for item in payload.get("arms", ()))
    matrix_arms: tuple[ArmSpec, ...] = ()
    if "matrix" in payload:
        matrix = payload["matrix"]
        if not isinstance(matrix, Mapping):
            raise LabError("candidate matrix must be an object")
        matrix_arms = expand_arm_matrix(matrix)
    arms = explicit + matrix_arms
    if not arms:
        raise LabError("candidate file must declare explicit arms or a matrix")
    ids = [arm.arm_id for arm in arms]
    if len(ids) != len(set(ids)):
        raise LabError("candidate file generated duplicate arm ids")
    return arms


def load_benchmark(path: str | Path):
    payload = _json_file(path)
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

    publish = sub.add_parser("publish-component", help="Publish one immutable component artifact")
    publish.add_argument("spec")
    publish.add_argument("payload")
    publish.add_argument("--registry", default=".lab-state/registry")
    publish.add_argument("--output", default="")

    assemble = sub.add_parser(
        "assemble-benchmark",
        help="Freeze registered component versions at fixed canonical outcome cuts",
    )
    assemble.add_argument("evaluation")
    assemble.add_argument("components")
    assemble.add_argument("--registry", default=".lab-state/registry")
    assemble.add_argument("--output", required=True)

    run = sub.add_parser("run", help="Run candidate arms against a separate fixed benchmark")
    run.add_argument("benchmark")
    run.add_argument("candidate_set")
    run.add_argument("--state-dir", default=".lab-state")
    run.add_argument("--parallel", type=int, default=1)
    run.add_argument("--output", default="")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.lab_command == "publish-component":
        raw_spec = _json_file(args.spec)
        payload = _json_file(args.payload)
        registry = ComponentRegistry(args.registry)
        try:
            artifact = registry.build(_component_spec(raw_spec), payload)
        finally:
            registry.close()
        _emit(asdict(artifact), args.output)
        return 0

    if args.lab_command == "assemble-benchmark":
        evaluation = _json_file(args.evaluation)
        component_set = _json_file(args.components)
        hashes = component_set.get("artifacts") if isinstance(component_set, Mapping) else None
        if not isinstance(hashes, list) or not hashes:
            raise LabError("components file must contain a non-empty artifacts list")
        registry = ComponentRegistry(args.registry)
        try:
            benchmark = assemble_benchmark(evaluation, registry, (str(x) for x in hashes))
        finally:
            registry.close()
        _emit(benchmark, args.output)
        return 0

    if args.lab_command == "run":
        state = Path(args.state_dir)
        state.mkdir(parents=True, exist_ok=True)
        batch, snapshots, outcomes = load_execution(args.benchmark, args.candidate_set)
        ledger = ExperimentLedger(state / "experiments.sqlite")
        try:
            result = run_batch(batch, snapshots, outcomes, max_workers=args.parallel, ledger=ledger)
        finally:
            ledger.close()
        _emit(result.to_dict(), args.output)
        return 0

    return 2
