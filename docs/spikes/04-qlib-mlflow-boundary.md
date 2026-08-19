# Spike #4 — Qlib + MLflow experiment/training boundary and reproducibility contract

Issue: Pukujan/finance-quant#4
Status: **DECIDED 2026-08-19** — ADOPT option A (Qlib substrate + MLflow store behind append-only ExperimentLedger facade; reproducibility contract sec. 3 binding); REJECT own-tracking-store. Decision recorded on issue #4 under owner auto-delegation (owner-reversible).
Serves invariants: I2 (reproducibility), I7 (failed trials visible), I5 (search != authority)

---

## 1. Verified state of the world (2026-08-19)

- **Qlib** (microsoft/qlib, ~47.7k stars, MIT, py3.8-3.12): full ML research pipeline —
  data provider, expression engine, dataset handlers (Alpha158/Alpha360 zoo verified),
  model zoo (~25 benchmarks), workflow/recorder layer, backtest, RL module, `qrun`
  YAML-driven runs. Ships a Point-in-Time DB feature (PR #343, Mar 2022) — depth of its
  bitemporal semantics needs hands-on verification before we lean on it.
- Qlib's recorder layer (`qlib.workflow.R`) is MLflow-based by default: experiments, runs,
  params, metrics, artifacts land in an MLflow tracking store (verified from docs/source).
- Qlib's official data bundle is **temporarily disabled** (verified); community mirror
  `chenditc/investment_data` exists; upstream itself warns the Yahoo-sourced data is
  imperfect. Consequence: Qlib's data layer is a *consumer* of our PIT authority (memo #2),
  never a source we inherit beliefs from.
- **RD-Agent** drives Qlib as its quant backend (`rdagent fin_quant|fin_factor|fin_model`,
  verified), Linux-only, Docker-orchestrated, LiteLLM-native. If spike #7 grants RD-Agent
  a lane, the boundary defined here is precisely the seam it plugs into.
- **AlphaGen** (ICT-FinD-Lab/alphagen, formerly RL-MLDM) ships `alphagen_qlib` adapters
  (verified) — same seam for the RL search lane.

## 2. The boundary question, precisely posed

Qlib overlaps our ownership in three places: (a) data provision, (b) expression/feature
semantics, (c) run/experiment recording. The spike must decide, per overlap zone:
*adopt Qlib's implementation, adapt behind our interface, or bypass.*

| Zone | Qlib native | Our invariant pressure | Proposal |
|---|---|---|---|
| (a) Data provision | snapshot-style provider, no knowledge-time axis | I1 | **Bypass reads.** Our `PITStore.as_of()` builds the training frame; Qlib receives a frozen, manifest-hashed extract. Qlib `provider_uri` points at *derived* artifacts only. |
| (b) Expression semantics | Qlib expression engine | I1, I3-DSL | **Adapt.** Tier-1 IR (memo #3) compiles *to* Qlib expressions where we adopt the engine; equivalence vs reference interpreter is a test, not a hope. |
| (c) Experiment recording | MLflow via `qlib.workflow.R` | I2, I7 | **Adopt MLflow as the store, wrap the contract.** We do not call `qlib.workflow.R` raw from research code; a thin `ExperimentLedger` facade enforces the required fields below. |

## 3. Reproducibility contract (the actual deliverable)

Every run — training, evaluation, backtest, search trial, FAILED trial — registers one
record with **all** fields present (missing field = run rejected):

```
run_record := {
  run_id, experiment_id, parent_run_id | null,      -- lineage (I7)
  code_sha, env_lock_hash (uv.lock / conda env.yml), -- environment
  dataset_manifest_hash,                             -- from memo #2 snapshot_pin()
  feature_ir_hash | model_class + hyperparams,
  seed(s), hardware_profile,
  cost_model_ref, split_policy_ref,
  metrics, artifacts (model, predictions, logs),
  status: {success | failed | invalid},              -- failed/invalid CANNOT be deleted
  agent_origin: {human | lane_id from #7} | null     -- provenance of the candidate
}
```

Mechanical enforcement points:
1. `ExperimentLedger` is the *only* writer to MLflow (Qlib's recorder writes through it).
2. `dataset_manifest_hash` must resolve against the PIT store or the artifact lake —
   a run pointing at unresolvable data is marked `invalid`, not merely warned (I2).
3. Deletion API is not exposed to research agents; retention is append-only (I7).
   MLflow allows run deletion — our facade removes that capability and the server-side
   deployment should too (policy note for whoever runs the tracking server).
4. Retry/resume: same `idempotency_key` -> same `run_id`; resume writes continuation
   events, never a second authority record (Phase C adversarial case #16).

## 4. Options scored

| Option | I2 reproducibility | I7 failure visibility | Integration cost | Verdict lean |
|---|---|---|---|---|
| A. Qlib pipeline + MLflow store + our boundary facade | ++ | ++ (facade-enforced) | medium | **recommended** |
| B. Qlib end-to-end as-is (qrun + R direct) | + (params yes, data pin no) | 0 (deletable) | low | acceptable only pre-Phase-B |
| C. No Qlib; own trainer + MLflow | + | + | high | DEFER — reinventing the model zoo is waste now |
| D. Own everything incl. own tracking store | ++ | ++ | highest | REJECT at this stage |

## 5. Bake-off / verification tasks for the spike

1. Hands-on: what does Qlib's PIT DB (PR #343) actually guarantee? If it models
   knowledge-time correctly it becomes a candidate *cache* inside our authority, not
   the authority itself. (one afternoon)
2. Fresh-runner rerun drill: container `A` trains LightGBM/Alpha158 on fixture extract;
   container `B` (clean env from lock) reproduces metrics to tolerance using only the
   run record. This is the I2 acceptance test for the whole contract.
3. Failed-run drill: force exceptions mid-training and mid-backtest; verify record
   survives with status `failed` and is undeletable via the facade.

## 6. Vertical-slice impact

- Phase B steps 3-4 literally are this contract: "Qlib training/evaluation path with
  MLflow-compatible run lineage" + "exact signal/feature/model artifact registration."
- The `agent_origin` field is the hook that lets #7's search lanes and #9's adversarial
  campaign coexist with boring research in one ledger.

## 6a. V0 implementation evidence (2026-08-19)

Committed in `51b26c1`: `finance_quant.experiments.ExperimentLedger` implements the
contract shell before a Qlib/MLflow adapter exists. `RunSpec` refuses missing code,
environment, dataset-manifest, IR/model hashes, seeds, split, and cost policy;
`begin` is idempotent by full-spec hash; terminal records are append-only and
immutable; failed records remain queryable. `scripts/run_b1_baseline.py` demonstrates
an actual PIT-to-ledger record. The Qlib+MLflow adapter and clean-container rerun drill
remain required integration verification tasks.

## 7. Evidence gaps before decision

- Result of verification task 1 (Qlib PIT depth).
- Confirm MLflow deployment posture (local file store vs server) and how deletion is
  disabled server-side — must be a deploy-time answer, not a convention.
- Windows-host reality check: Qlib claims Windows support (verified badge); LEAN wants
  dotnet; RD-Agent is Linux-only. Likely: WSL2 or Linux runner for anything RD-Agent.

## 8. Recommendation

**ADOPT option A**: Qlib as training/eval substrate, MLflow as run store, our
`ExperimentLedger` facade as the only write path; Qlib reads only manifest-pinned
extracts from the PIT authority. **REJECT D**, defer C. Write the reproducibility
contract (sec. 3) into the issue as the decision text — it is interface, not
implementation, and Phase B cannot start without it.
