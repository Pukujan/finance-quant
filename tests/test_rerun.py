from finance_quant.experiments.ledger import RunSpec
from finance_quant.experiments.rerun import rerun_receipt


def test_fresh_environment_rerun_reproduces_run_id_and_metrics(tmp_path):
    spec = RunSpec("B1", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    receipt = rerun_receipt(spec, {"ic": 0.2}, {"model": "abc"},
                            tmp_path / "a.db", tmp_path / "b.db", tmp_path / "export")
    assert receipt["same_run_id"]
    assert receipt["same_metrics"]
    assert receipt["same_spec_hash"]
