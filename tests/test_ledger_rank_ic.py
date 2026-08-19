from finance_quant.baselines.momentum import run_momentum
from finance_quant.experiments.ledger import ExperimentLedger, RunSpec, RunStatus
from finance_quant.pit.fixtures import N_DAYS, START, SYMBOLS, business_days, generate
from finance_quant.pit.store import MemoryGoldStore


def test_b3_rank_ic_is_stored_on_the_run_record(tmp_path):
    store = MemoryGoldStore()
    for row in generate():
        store.put(row)
    days = business_days(START, N_DAYS)
    fold = run_momentum(store, SYMBOLS, days, days[-2])
    ledger = ExperimentLedger(tmp_path / "runs.db")
    spec = RunSpec("B3", "c" * 40, "env", "data", "ir", "model", (1,), "split", "cost")
    run = ledger.begin(spec)
    done = ledger.finalize(run.run_id, RunStatus.SUCCESS, {"rank_ic": fold.rank_ic})
    assert dict(done.metrics)["rank_ic"] == fold.rank_ic
    ledger.close()
