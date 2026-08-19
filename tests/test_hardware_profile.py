from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus


def test_hardware_profile_defaults_and_is_recorded(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("e", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost",
                   hardware_profile="cpu-only")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"x": 1.0})
    assert done.spec.hardware_profile == "cpu-only"
    ledger.close()
