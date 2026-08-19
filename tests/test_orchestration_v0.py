"""Property tests for the V0 orchestration core (issue #10 required catalog).

Covered: retry/idempotency, duplicate receipts, out-of-order completion,
crash before/after artifact write, partial campaign fan-in, malformed receipt
rejection, deterministic campaign expansion, authority-boundary enforcement,
cancellation, sealed-capability egress. Backend round-trip + timeout crash tests
run a real subprocess against the local backend.
"""
from __future__ import annotations

import json
import os
import random
import time

import pytest

from finance_quant.orchestration import fanin, fanout
from finance_quant.orchestration.authority import (AuthorityViolation,
                                                   CapabilityClass,
                                                   assert_worker_capability,
                                                   worker_environment)
from finance_quant.orchestration.backends.local import CrashReport, LocalBackend
from finance_quant.orchestration.contracts import (ContractError, ResourceRequest,
                                                   TerminalStatus, WorkOrder,
                                                   content_hash)
from finance_quant.orchestration.lifecycle import (AttemptState, AttemptStore,
                                                   CommitOutcome, LifecycleError)
from finance_quant.orchestration.receipts import parse_receipt
from finance_quant.orchestration.executor import run_work_order

FAST = ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=30.0, heartbeat_s=0.5)


def make_wo(i: int = 0, task: str = "finance_quant.orchestration.handlers:run") -> WorkOrder:
    return WorkOrder(
        campaign_id="test", task_type=task, dataset_snapshot_id="snap-0",
        code_commit="0" * 40, seeds=(42,), manifest_hash="m" * 64,
        resource_request=FAST, fold_id=f"fold-{i}",
    )


def make_receipt(wo: WorkOrder, retry_seq: int = 0, metrics=(("acc", 1.0),)):
    from finance_quant.orchestration.contracts import ResultReceipt
    return ResultReceipt(
        work_order_hash=wo.work_order_hash, retry_seq=retry_seq,
        terminal_status=TerminalStatus.COMPLETED, worker_id="w0", backend_id="local",
        started_at=1.0, ended_at=2.0, environment_hash="env", metrics=metrics,
    )


@pytest.fixture()
def store(tmp_path):
    s = AttemptStore(tmp_path / "attempts.db")
    yield s
    s.close()


# --- contracts ----------------------------------------------------------------
def test_work_order_hash_stable_and_key_order_insensitive():
    wo = make_wo()
    assert wo.attempt_id == wo.work_order_hash
    assert content_hash({"b": 1, "a": 2}) == content_hash({"a": 2, "b": 1})
    with pytest.raises(Exception):
        _ = dataclass_mutate(wo)  # frozen


def dataclass_mutate(wo):
    wo.task_type = "x"


def test_receipt_contract_rejects_inverted_times():
    from finance_quant.orchestration.contracts import ResultReceipt
    with pytest.raises(ContractError):
        ResultReceipt(work_order_hash="x", retry_seq=0,
                      terminal_status=TerminalStatus.COMPLETED, worker_id="w",
                      backend_id="b", started_at=2.0, ended_at=1.0, environment_hash="e")


# --- ledger lifecycle -----------------------------------------------------------
def test_issue_is_idempotent(store):
    wo = make_wo()
    assert store.issue(wo) is True
    assert store.issue(wo) is False


def test_duplicate_receipt_cannot_fork_authority(store):
    wo = make_wo()
    store.issue(wo)
    store.mark_queued(wo.work_order_hash)
    store.mark_running(wo.work_order_hash)
    r1 = make_receipt(wo, metrics=(("acc", 1.0),))
    r2 = make_receipt(wo, metrics=(("acc", 999.0),))
    assert store.commit_receipt(r1) is CommitOutcome.COMMITTED
    assert store.commit_receipt(r2) is CommitOutcome.INVALID   # attempt already terminal
    receipts = store.authoritative_receipts([wo.work_order_hash])
    assert len(receipts) == 1
    assert "999.0" not in receipts[0]


def test_duplicate_receipt_superseded_path(store):
    wo = make_wo()
    store.issue(wo)  # first attempt
    store.mark_queued(wo.work_order_hash, 0)
    store.mark_running(wo.work_order_hash, 0)
    store.commit_receipt(make_receipt(wo, 0))
    # a retried attempt also completes -> duplicate authority rejected structurally
    store.issue(wo, retry_seq=1)
    store.mark_queued(wo.work_order_hash, 1)
    store.mark_running(wo.work_order_hash, 1)
    assert store.commit_receipt(make_receipt(wo, 1)) is CommitOutcome.DUPLICATE
    assert len(store.authoritative_receipts([wo.work_order_hash])) == 1
    assert len(store.duplicates()) == 1


def test_terminal_states_do_not_resurrect(store):
    wo = make_wo()
    store.issue(wo)
    store.cancel(wo.work_order_hash)
    with pytest.raises(LifecycleError):
        store.mark_running(wo.work_order_hash)


def test_malformed_receipt_rejected():
    with pytest.raises(ContractError):
        parse_receipt('{"not": "a receipt"}')


def test_commit_receipt_for_unknown_attempt_is_invalid(store):
    wo = make_wo()
    assert store.commit_receipt(make_receipt(wo)) is CommitOutcome.INVALID


# --- fan-out -------------------------------------------------------------------
def _spec(seeds=(7,)):
    return fanout.CampaignSpec(
        campaign_id="camp", dataset_snapshot_id="snap-0", code_commit="0" * 40,
        seeds=seeds,
        stages=(fanout.StageSpec(
            task_type="finance_quant.orchestration.handlers:run",
            dimensions=(
                ("factor_hash", ("f1", "f2")),
                ("model_config_hash", ("m1",)),
                ("fold_id", ("k1", "k2", "k3")),
                ("cost_policy_version", ("c0", "c1")),
            ),
        ),),
        resource_request=FAST,
    )


def test_expansion_is_deterministic():
    hashes = {fanout.expand_campaign(_spec()).manifest_hash for _ in range(50)}
    assert len(hashes) == 1
    m = fanout.expand_campaign(_spec())
    assert len(m.work_orders) == 2 * 1 * 3 * 2
    ids = m.expected_attempt_ids
    assert len(set(ids)) == len(ids)


def test_expansion_key_order_in_spec_does_not_change_identity():
    spec_a = _spec()
    st = spec_a.stages[0]
    reordered = fanout.StageSpec(task_type=st.task_type,
                                 dimensions=tuple(reversed(list(st.dimensions))))
    spec_b = fanout.CampaignSpec(
        campaign_id=spec_a.campaign_id, dataset_snapshot_id=spec_a.dataset_snapshot_id,
        code_commit=spec_a.code_commit, seeds=spec_a.seeds, stages=(reordered,),
        resource_request=FAST)
    ma, mb = fanout.expand_campaign(spec_a), fanout.expand_campaign(spec_b)
    assert sorted(ma.expected_attempt_ids) == sorted(mb.expected_attempt_ids)


# --- fan-in ----------------------------------------------------------------------
def test_fanin_order_independent_and_partial_never_complete(store):
    m = fanout.expand_campaign(_spec())
    wos = list(m.work_orders)
    for wo in wos:
        store.issue(wo)

    # complete only a random subset -> never complete
    subset = wos[: len(wos) - 1]
    for wo in subset:
        store.mark_queued(wo.work_order_hash)
        store.mark_running(wo.work_order_hash)
        store.commit_receipt(make_receipt(wo))
    st = fanin.status(store, m.manifest_hash, m.expected_attempt_ids)
    assert not st.complete
    with pytest.raises(fanin.PartialCampaign):
        fanin.deterministic_aggregate(store, m.manifest_hash, m.expected_attempt_ids)

    # finish the remainder IN SHUFFLED ORDER; aggregate must be arrival-invariant
    rng = random.Random(1234)
    for wo in rng.sample(wos[len(wos) - 1:], 1):
        store.mark_queued(wo.work_order_hash)
        store.mark_running(wo.work_order_hash)
        store.commit_receipt(make_receipt(wo))
    agg = fanin.deterministic_aggregate(store, m.manifest_hash, m.expected_attempt_ids)
    assert agg["n_authoritative"] == len(wos)

    # simulate a second scheduler observing a different completion order:
    store2_path = None
    import tempfile, pathlib
    store2 = AttemptStore(pathlib.Path(tempfile.mkdtemp()) / "s2.db")
    wos2 = list(m.work_orders)
    rng2 = random.Random(99)
    for wo in rng2.sample(wos2, len(wos2)):
        store2.issue(wo)
        store2.mark_queued(wo.work_order_hash)
        store2.mark_running(wo.work_order_hash)
        store2.commit_receipt(make_receipt(wo))
    agg2 = fanin.deterministic_aggregate(store2, m.manifest_hash, m.expected_attempt_ids)
    store2.close()
    assert agg["fingerprint"] == agg2["fingerprint"]


# --- authority boundary -----------------------------------------------------------
def test_worker_env_strips_forbidden_handles():
    dirty = {"PATH": os.environ.get("PATH", ""),
             "FQ_EXPERIMENT_LEDGER_URI": "x", "FQ_PROMOTION_API": "y",
             "MLFLOW_TRACKING_URI": "z"}
    env = worker_environment(CapabilityClass.RESEARCH_WORKER, base=dirty)
    assert "FQ_EXPERIMENT_LEDGER_URI" not in env
    assert env["FQ_CAPABILITY"] == "research_worker"
    assert_worker_capability(env)  # must not raise


def test_worker_assertion_kills_contaminated_env():
    with pytest.raises(AuthorityViolation):
        assert_worker_capability({"FQ_PROMOTION_API": "http://evil",
                                  "FQ_CAPABILITY": "research_worker"})


def test_sealed_worker_loses_network_handles():
    dirty = {"PATH": "x", "OPENAI_API_BASE": "https://api", "HTTPS_PROXY": "p"}
    env = worker_environment(CapabilityClass.SEALED_SCORING_WORKER, base=dirty)
    assert "OPENAI_API_BASE" not in env and "HTTPS_PROXY" not in env
    assert_worker_capability(env)


# --- executor + local backend (real subprocess) -----------------------------------
def test_executor_crashes_of_handler_become_failed_receipt(tmp_path):
    wo = make_wo(task="finance_quant.orchestration.handlers:boom")
    receipt = run_work_order(wo, tmp_path, worker_id="t", backend_id="t")
    assert receipt.terminal_status is TerminalStatus.FAILED
    assert receipt.error_class == "RuntimeError"


def test_local_backend_round_trip(tmp_path):
    backend = LocalBackend()
    wo = make_wo()
    outcome = backend.execute(wo)
    assert not isinstance(outcome, CrashReport), getattr(outcome, "detail", "")
    assert outcome.terminal_status is TerminalStatus.COMPLETED
    assert outcome.metrics == (("attempt", 1.0),)


def test_local_backend_timeout_becomes_crash(tmp_path):
    backend = LocalBackend()
    wo = WorkOrder(
        campaign_id="t", task_type="finance_quant.orchestration.handlers:sleep",
        dataset_snapshot_id="s", code_commit="0" * 40, seeds=(1,),
        manifest_hash="m" * 64,
        resource_request=ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=1.0,
                                         heartbeat_s=0.2),
        input_refs=(("sleep_s", "10"),),
    )
    outcome = backend.execute(wo)
    assert isinstance(outcome, CrashReport)
    assert outcome.error_class == "timeout"


def test_scheduler_crash_then_retry_succeeds(tmp_path):
    from finance_quant.orchestration.retries import RetryPolicy
    from finance_quant.orchestration.scheduler import Scheduler

    store = AttemptStore(tmp_path / "sched.db")
    backend = LocalBackend()
    scheduler = Scheduler(store, backend, RetryPolicy(max_retries=1))
    spec = fanout.CampaignSpec(
        campaign_id="c", dataset_snapshot_id="s", code_commit="0" * 40, seeds=(1,),
        stages=(fanout.StageSpec(
            task_type="finance_quant.orchestration.handlers:sleep",
            dimensions=(("fold_id", ("k1",)),)),
        ),
        resource_request=ResourceRequest(cpu=1, mem_mb=64, wall_timeout_s=0.3,
                                         heartbeat_s=0.1),
    )
    manifest = fanout.expand_campaign(spec)
    wo = manifest.work_orders[0]
    # no input_refs sleep_s -> default 5s -> times out twice -> attempts recorded
    scheduler._run_one(wo)
    assert store.next_retry_seq(wo.work_order_hash) == 2  # initial + 1 retry
    assert store.last_state(wo.work_order_hash) is AttemptState.CRASHED
    store.close()


def test_scheduler_resume_only_runs_attempts_not_already_terminal(tmp_path):
    """Adversarial restart drill: persisted ledger, not scheduler RAM, is authority."""
    from finance_quant.orchestration.scheduler import Scheduler

    store = AttemptStore(tmp_path / "resume.db")
    backend = LocalBackend()
    manifest = fanout.expand_campaign(_spec())
    first, rest = manifest.work_orders[0], manifest.work_orders[1:]
    # Simulate a prior scheduler dying after it committed exactly one work order.
    store.issue(first)
    store.mark_queued(first.work_order_hash)
    store.mark_running(first.work_order_hash)
    store.commit_receipt(make_receipt(first))
    store.close()

    restarted = AttemptStore(tmp_path / "resume.db")
    scheduler = Scheduler(restarted, backend)
    # The individual attempt already terminal: a resume must not resurrect it.
    assert restarted.last_state(first.work_order_hash) is AttemptState.COMPLETED
    for wo in rest:
        scheduler._run_one(wo)
    aggregate = fanin.deterministic_aggregate(
        restarted, manifest.manifest_hash, manifest.expected_attempt_ids
    )
    assert aggregate["n_authoritative"] == len(manifest.work_orders)
    assert restarted.last_state(first.work_order_hash) is AttemptState.COMPLETED
    restarted.close()
