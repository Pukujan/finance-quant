from finance_quant.dsl.checker import TemporalError, check
from finance_quant.dsl.ir import Field, Lag
from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
import pytest


def test_leaky_expression_never_becomes_a_successful_run(tmp_path):
    leaky = Lag(Field("close"), -1)
    with pytest.raises(TemporalError):
        check(leaky)
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("leak", "c" * 40, "env", "data", "ir-leak", "none", (1,), "split", "cost",
                   agent_origin="random-v0")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.INVALID, error_class="TemporalError")
    assert done.status is RunStatus.INVALID
    ledger.close()
