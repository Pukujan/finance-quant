"""Tests that Trial Gate V0 integrates with real B1-B5 campaign artifacts."""
from __future__ import annotations

from finance_quant.baselines.cross_section import run_buy_and_hold
from finance_quant.baselines.momentum import run_momentum
from finance_quant.baselines.walk_forward import run_walk_forward, sma3_expression
from finance_quant.dsl.ir import to_dict
from finance_quant.experiments.artifact import run_record_to_trial_artifact
from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.gate import check_trial_artifact
from finance_quant.orchestration.contracts import content_hash
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import SQLiteBitemporalStore


def _run(tmp_path, suffix=""):
    db_path = tmp_path / f"pit{suffix}.db"
    days = business_days(START, N_DAYS)
    cutoff = days[-2]
    pit = SQLiteBitemporalStore(db_path)
    for rec in generate():
        pit.put(rec)
    ledger = ExperimentLedger(tmp_path / f"runs{suffix}.db")
    manifest = pit.snapshot_pin()
    ir_hash, folds = run_walk_forward(pit, SYMBOLS, days, (days[19], days[39], cutoff))
    fold = folds[-1]
    spec = RunSpec("B1-sma3", "a" * 64, "b" * 64, manifest, ir_hash, ir_hash,
                   (0,), "fixture-cutoff-v0", "not-executed-v0")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS,
                           {"n_signals": float(fold.n_signals),
                            "mean_signal": fold.mean_signal,
                            "rank_ic": fold.rank_ic},
                           {"fold": content_hash(fold.fold_id), "signal": fold.signal_hash})
    ledger.close()
    pit.close()
    return done


def test_b1_run_record_passes_trial_gate(tmp_path):
    done = _run(tmp_path)
    artifact = run_record_to_trial_artifact(done)
    gate = check_trial_artifact(artifact)
    assert gate.ok, gate.violations


def test_b1_run_record_is_deterministic(tmp_path):
    a = _run(tmp_path, "a")
    b = _run(tmp_path, "b")
    assert run_record_to_trial_artifact(a) == run_record_to_trial_artifact(b)
    assert a.run_id == b.run_id


def test_b1_artifact_has_no_label_in_feature_hash(tmp_path):
    done = _run(tmp_path)
    artifact = run_record_to_trial_artifact(done)
    assert "label" not in artifact["feature_ir_hash"].lower()
    assert "target" not in artifact["feature_ir_hash"].lower()


def test_run_record_to_trial_artifact_preserves_all_required_fields(tmp_path):
    done = _run(tmp_path)
    artifact = run_record_to_trial_artifact(done)
    required = {"run_id", "experiment_id", "dataset_manifest_hash", "feature_ir_hash",
                "model_config_hash", "code_sha", "env_lock_hash", "seeds", "split_policy_ref",
                "cost_model_ref", "agent_origin", "status", "artifacts", "metrics"}
    assert required <= set(artifact.keys())
