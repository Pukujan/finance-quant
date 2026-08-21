# Phase B FOSSIL Integration Plan

**Status:** PROPOSED — planning document; no FOSSIL writes are authorized until the owner approves the pack mount and credentials.  
**Scope:** Define the smallest set of FOSSIL evidence commits required to satisfy Phase B exit criteria and the Phase C adversarial handoff.  
**Authority:** FOSSIL owns durable reviewed evidence, provenance, decisions, and assumptions; `finance-quant` owns the quantitative research/trading laboratory and all numeric artifacts.

---

## 1. Goal

Phase B must produce not only reproducible numeric results, but also a reviewable evidence trail that lets a human reconstruct:

- Which fixture was used for every run.
- Which code, environment, model, and cost assumptions produced every receipt.
- Who (or which agent lane) generated each result.
- What promotion decision was made, on what evidence, and when.

This plan maps each Phase B runner to a minimal FOSSIL evidence commit type from spike #6, lists the required references, and defines the approval path.

---

## 2. FOSSIL commit types for Phase B

Use only the ontology from `docs/spikes/06-fossil-ontology-graph-features.md`:

| Type | Role in Phase B | Writers | Reviewers |
|---|---|---|---|
| `fq:DataSnapshot` | Canonical fixture, holdout fixture, any reduced-CI fixture | Pipeline / owner | Owner |
| `fq:RunRecord` | B1–B5, Qlib/LightGBM, LEAN replay, determinism drill, cost-stress report | Pipeline (agent or human) | Owner or delegated reviewer |
| `fq:ModelArtifact` | Qlib model config + predictions hash; any learned graph-feature artifact | Pipeline | Owner |
| `fq:FeatureIR` | Tier-1 IR expressions used by baselines | Pipeline | Owner |
| `fq:BacktestReceipt` | LEAN replay receipt (nominal + 2x slippage) | Pipeline | Owner |
| `fq:EvaluationReport` | Rank-IC report, cost-stress report, determinism drill report | Pipeline | Owner |
| `fq:PromotionReview` | Owner decision to promote a result or proceed to Phase C | Owner | Second human reviewer (if available) |

---

## 3. Required references on each commit

### `fq:DataSnapshot`

```text
manifest_hash: <fixture snapshot_pin>
namespace: ["bar", "corporate_action", ...]
vt_range: [start, end]
kt_bound: <ISO timestamp>
source_vendor: polygon | alpaca | synthetic
case_set_id: <for holdout fixture>
```

### `fq:RunRecord`

```text
run_id: <ExperimentLedger run_id or script receipt id>
dataset_manifest_hash: <snapshot_pin of fixture>
feature_ir_hash: <content hash of IR or config>
model_config_hash: <content hash of model config>
split_policy_ref: chronological-80-20-v0 | fixture-single-cutoff-v0 | ...
cost_model_ref: nominal-5bps-slippage-v0 | ...
agent_origin: human | baseline | qlib | lean | random | gp
status: SUCCESS | INVALID | FAILED
receipt_hash: <SHA-256 of receipt JSON>
```

### `fq:BacktestReceipt`

```text
run_record_ref: <fq:RunRecord id>
engine: lean-cli | lean-subprocess-stub
fill_model: ImmediateSameBarFillModel | ...
slippage_model: ConstantSlippageModel | ...
fee_model: ZeroFeeModel | ...
slippage_bps: 5.0 | 10.0
variant: nominal | 2x_slippage
equity_curve_hash: <optional>
```

### `fq:PromotionReview`

```text
decision: ADOPT | CONSTRAIN | REJECT | DEFER
scope: phase-b-exit | phase-c-promotion
run_records: [<run_id>, ...]
backtest_receipts: [<receipt_id>, ...]
evaluation_reports: [<report_id>, ...]
owner_identity: <owner handle>
reviewed_at: <ISO kt>
```

---

## 4. Runner-to-commit mapping

| Phase B runner | FOSSIL commits emitted | When |
|---|---|---|
| `scripts/run_phase_b_benchmark.py` | One `fq:DataSnapshot` for the fixture; one `fq:RunRecord` each for B1–B5, Qlib, LEAN; one `fq:EvaluationReport` for the consolidated benchmark | On successful completion |
| `scripts/run_b1_b5_phase_b.py` | One `fq:RunRecord` per B1–B5 experiment; one `fq:FeatureIR` per unique IR | On successful completion |
| `scripts/run_qlib_phase_b.py` | One `fq:RunRecord`; one `fq:ModelArtifact`; one `fq:FeatureIR` | On successful completion |
| `scripts/run_lean_phase_b.py` | One `fq:RunRecord`; one `fq:BacktestReceipt` per variant | On successful completion |
| `scripts/run_phase_b_determinism_drill.py` | One `fq:EvaluationReport` comparing receipt hashes across runs | On successful completion |
| `scripts/run_cost_stress_report.py` | One `fq:EvaluationReport` for nominal vs 2x slippage | On successful completion |
| `scripts/generate_phase_b_holdout.py` | One `fq:DataSnapshot` for the holdout feature records; label hash committed separately in holdout repo | On sealing |
| `scripts/write_phase_b_seal.py` | One `fq:PromotionReview` or `fq:RunRecord` referencing the sealed holdout Merkle root | On seal creation |

---

## 5. Writer / reviewer / owner path

1. **Pipeline writer:** every runner that produces a receipt or report writes a draft evidence commit to the FOSSIL pack. The writer is identified by `agent_origin`.
2. **Automated hygiene checks:** before any commit is accepted, verify that all referenced hashes exist in the local artifacts and that `kt` is not in the future.
3. **Reviewer queue:** draft commits sit in a `proposed/` namespace until a human reviewer or owner inspects them.
4. **Owner approval:** the owner merges the evidence commit into the authoritative namespace. Only the owner role can create `fq:PromotionReview` commits.
5. **Promotion gate:** a Phase B result may not be promoted to Phase C paper-trading without a signed `fq:PromotionReview` and a valid sealed-holdout seal.

---

## 6. Code seams to wire

To implement this plan, the following changes are needed (not yet implemented):

1. `finance_quant/lineage/fossil_writer.py` — new module with `commit_run_record`, `commit_data_snapshot`, `commit_backtest_receipt`, `commit_evaluation_report`, `commit_promotion_review`.
2. `finance_quant/lineage/pack.py` — ensure `LocalEvidencePack` can stage FOSSIL-compatible JSON or call a FOSSIL pack API.
3. Runner hooks in:
   - `scripts/run_b1_b5_phase_b.py`
   - `scripts/run_qlib_phase_b.py`
   - `scripts/run_lean_phase_b.py`
   - `scripts/run_phase_b_benchmark.py`
   - `scripts/run_phase_b_determinism_drill.py`
   - `scripts/run_cost_stress_report.py`
4. `scripts/write_phase_b_seal.py` — emit a `fq:PromotionReview` or reference the seal in a run record.
5. Tests in `tests/test_fossil_evidence.py` verifying each commit shape and hash references.

---

## 7. Prerequisites and blockers

| Prerequisite | Status | Blocker if missing |
|---|---|---|
| Dedicated FOSSIL pack with narrow read/write mounts | NOT SET UP | Pipeline cannot write evidence commits without widening authority |
| Owner FOSSIL credentials / API token | NOT SET UP | Owner cannot approve commits |
| Canonical fixture hash frozen | SATISFIED | `data/fixtures/phase-b/manifest.json` committed |
| Sealed holdout created | SATISFIED | `docs/acceptance/PHASE_B_HOLDOUT_SEAL.json` committed |
| Qlib/LEAN environment pinned | PARTIAL | Stubs exist; real pinning is an owner decision |
| Agent origin tagging in ExperimentLedger | SATISFIED | `agent_origin` field exists on `RunSpec` |

---

## 8. Decision gate

**PROPOSED:** before any FOSSIL integration code is merged, the owner must:

1. Confirm the FOSSIL pack location and mount rules.
2. Approve the evidence-commit schema above.
3. Name the owner/reviewer identities for Phase B.
4. Decide whether FOSSIL commits are written automatically by runners or manually via a separate `scripts/commit_evidence.py` step.

**Next step:** implement `finance_quant/lineage/fossil_writer.py` and a single runner hook (B1–B5) as a proof of concept, then rehearse the promotion flow on a synthetic fixture.

---

## 9. Non-goals

- FOSSIL does not store numeric time-series values; those remain in the PIT store, MLflow, and LEAN receipts.
- FOSSIL does not become the execution authority; it only records reviewed evidence about execution.
- No live trading or paper-trading authorization is granted by this plan.
