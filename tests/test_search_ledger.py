from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.search.evaluator import evaluate_proposal
from finance_quant.search.gp_lane import evolve
from finance_quant.search.random_lane import propose


def test_search_lanes_register_every_trial_including_invalid(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    histories = [[{"close": 1.0, "volume": 100.0, "open": 1.0, "high": 1.1, "low": 0.9}] * 12]
    proposals = propose(3, 4) + evolve(5, generations=1, population=3)
    recorded = []
    for p in proposals:
        ev = evaluate_proposal(p, histories)
        spec = RunSpec(
            experiment_id=f"{p.lane_id}-{ev.proposal_hash[:8]}",
            code_sha="0" * 40, env_lock_hash="dev", dataset_manifest_hash="d" * 64,
            feature_ir_hash=ev.proposal_hash, model_config_hash="none",
            seeds=(p.seed,), split_policy_ref="fixture", cost_model_ref="none",
            agent_origin=p.lane_id,
        )
        run = ledger.begin(spec)
        status = RunStatus.SUCCESS if ev.valid else RunStatus.INVALID
        done = ledger.finalize(run.run_id, status, {"score": ev.score or 0.0},
                               error_class=ev.violation_class)
        recorded.append(done)
    assert len(recorded) == len(proposals)
    assert all(r.status in {RunStatus.SUCCESS, RunStatus.INVALID} for r in recorded)
    ledger.close()
