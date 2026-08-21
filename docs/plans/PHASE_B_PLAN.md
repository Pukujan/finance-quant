# Phase B Execution Plan — Trustworthy Boring Baseline Vertical Slice

**Status:** DRAFT — owner decision required on vendor + universe before slice 1 starts.  
**Owner decision authority:** data-source vendor, universe scope, and monthly data budget are owner calls; this plan recommends and sequences the engineering slices.  
**References:** issue #1 (master DAG), #2 (PIT storage), #4 (Qlib/MLflow), #5 (LEAN), #7 (search bake-off), #9 (sealed holdout).

---

## 1. Goal

Produce the first **trustworthy, reproducible benchmark** for `finance-quant`:

- Real market data ingested into the bitemporal PIT store.
- B1–B5 boring baselines run through the native orchestration path.
- Qlib training/evaluation path with MLflow run lineage.
- LEAN backtest replay with explicit fill/slippage/fee models.
- Cost-aware returns compared against rank-IC-only returns.
- A sealed mini-holdout set created for the Phase C adversarial campaign.

**Non-goal:** automated alpha search, live trading, paper trading, model training, or graph-neural-symbolic experiments. Those are Phase C / new-spike scope.

---

## 2. Exit criteria (Phase B is done when)

1. A canonical real-data fixture exists with a pinned manifest hash.
2. `python -m finance_quant verify` runs B1–B5 end-to-end on that fixture in CI.
3. Qlib train/eval path emits MLflow-compatible run records referencing the fixture hash.
4. LEAN replay path emits backtest receipts with a named cost/fill model.
5. A cost-stress report exists: B1–B5 Sharpe / return under nominal vs 2x-slippage scenarios.
6. A tiny sealed holdout set is committed to `finance-quant-holdout` (issue #9).
7. A fresh-environment rerun from a clean runner reproduces the same aggregate receipt hashes.

---

## 3. Data vendor recommendation

### 3.1 Candidate matrix

| Vendor | Strengths for `finance-quant` | Weaknesses | Approx. research cost | Verdict |
|---|---|---|---|---|
| **Polygon.io** | Clean SIP timestamps; explicit `sip_timestamp`; good EOD + trades/quotes; corporate-actions endpoint; well-documented `kt` semantics | Paid tier for full market; needs API key management | ~$49–$199/mo for equities | **Recommended primary** |
| **Alpaca Markets** | Free tier for US equity daily; clean REST API; good for prototyping | Shorter history; weaker corporate-actions / fundamental coverage; timestamp semantics simpler | Free for basic tier | **Recommended fallback / prototype** |
| **Tiingo** | Excellent EOD + fundamentals; stable symbology | Equities focus; less granular timestamp story than Polygon | ~$10–$300/mo depending tier | **Recommended for fundamentals later** |
| Yahoo / scraped | Free | No reliable `kt`; survivorship-biased; restatement handling unknown; violates issue #2 authority boundary | Free | **REJECT as authority** |

### 3.2 Recommendation

**Start with Polygon.io as the canonical authority for Phase B.**

Reasoning:
- `sip_timestamp` gives us a defensible `kt` definition (issue #2: "kt is the #1 PIT failure mode").
- Corporate-actions endpoint lets us test split/dividend handling against real announcements.
- The API is simple enough that the adapter is a thin layer over the existing PIT record contract.

**If budget is a concern, run slice 1 against Alpaca free tier first**, then swap the adapter to Polygon once the ingest contract is stable. The PIT store should not care which vendor produced the row.

---

## 4. Slice-by-slice execution

Each slice is a PR-sized unit of work. Slices 1–3 are the critical path; slices 4–6 can run in parallel after slice 2.

### Slice 1 — Vendor adapter + small universe ingest
**Branch:** `feat/phase-b-polygon-adapter`  
**Issue refs:** #1 Phase B step 1, #2  
**Scope:**
- Add `finance_quant.ingest.polygon` adapter implementing the PIT record contract.
- Ingest 100 liquid US equities, 5 years of daily OHLCV, into the existing SQLite `PITStore`.
- Ingest corporate-actions stream (splits, dividends) for the same universe.
- Emit a manifest hash (`snapshot_pin`) for the fixture.
- Add environment config template: `.env.example` with `POLYGON_API_KEY`, `POLYGON_BASE_URL`.
- Add property test: `as_of` queries on real data match a small hand-checked reference sample.

**Acceptance:**
- `scripts/run_pit_bakeoff.py` passes on the new fixture.
- `pytest tests/ingest/test_polygon_adapter.py` passes.
- No code path reads "latest"; all reads use `as_of(vt, kt)`.

**Owner input needed:** Polygon API key, final universe list (default: S&P 100 or Nasdaq-100).

---

### Slice 2 — Canonical fixture freeze + rerun contract
**Branch:** `feat/phase-b-fixture-freeze`  
**Issue refs:** #1 Phase B step 1, #2, #10  
**Scope:**
- Promote the ingested dataset to a canonical fixture under `data/fixtures/phase-b/`.
- Store manifest hash in `data/fixtures/phase-b/manifest.json`.
- Add `scripts/freeze_fixture.py` that re-ingests and verifies the manifest hash.
- Add CI step that asserts the fixture manifest hash matches the committed value.
- Document the `kt` contract for this fixture in `docs/plans/PHASE_B_DATA_CONTRACT.md` (already created).

**Acceptance:**
- Fresh runner can reproduce the fixture hash from the same adapter version + API key.
- Hash mismatch fails CI.

---

### Slice 3 — B1–B5 baselines on real data
**Branch:** `feat/phase-b-b1-b5-real-data`  
**Issue refs:** #1 Phase B step 3, #3, #10  
**Scope:**
- Run B1–B5 on the canonical fixture through native WorkOrder orchestration.
- Record every attempt in the SQLite attempt ledger.
- Emit ExperimentLedger receipts with `agent_origin: human/baseline`.
- Add `scripts/run_b1_b5_phase_b.py`.
- Wire into the unified benchmark (`scripts/run_phase_b_benchmark.py`) and CLI (`python -m finance_quant benchmark`).
- Add the determinism drill script (`scripts/run_phase_b_determinism_drill.py`, CLI: `python -m finance_quant drill`).

**Acceptance:**
- All B1–B5 attempts end in terminal states.
- Fan-in aggregate is deterministic across 3 independent runs.
- Rank IC report is written to `reports/b1_b5_rank_ic.json`.

---

### Slice 4 — Qlib train/eval path with MLflow lineage
**Branch:** `feat/phase-b-qlib-mlflow`  
**Issue refs:** #1 Phase B step 4, #4  
**Scope:**
- Build a Qlib-format extract from the PIT fixture at a pinned `kt`.
- Train LightGBM Alpha158 baseline on the extract.
- Log run to MLflow with fields: `dataset_manifest_hash`, `feature_ir_hash`, `model_config_hash`, `split_policy_ref`, `cost_model_ref`.
- Add `scripts/run_qlib_phase_b.py`.

**Acceptance:**
- Model artifact is reproducible from the manifest hash + config.
- Failed-run drill: force an exception mid-training; ExperimentLedger records it.
- Fresh rerun from clean env produces identical predictions hash.

---

### Slice 5 — LEAN backtest with realistic costs
**Branch:** `feat/phase-b-lean-replay`  
**Issue refs:** #1 Phase B step 6, #5  
**Scope:**
- Convert B1–B5 signals + Qlib predictions into a LEAN custom data source.
- Run LEAN backtest with an explicit fill model, slippage model, and fee model.
- Cost-stress test: nominal model + 2x slippage model.
- Add `scripts/run_lean_phase_b.py`.

**Acceptance:**
- LEAN receipt includes named models and parameters.
- Cost-aware returns diverge from rank-IC-only returns in the expected direction.
- Determinism: same inputs produce same equity curve hash.

---

### Slice 6 — Sealed mini-holdout set
**Branch:** `feat/phase-b-sealed-holdout`  
**Issue refs:** #1 Phase B → Phase C handoff, #9  
**Scope:**
- Create a small sealed holdout set (synthetic or held-out real period) in `finance-quant-holdout`.
- Generate the holdout with `scripts/generate_phase_b_holdout.py` (output: `data/fixtures/phase-b-holdout/`).
- Write the public seal commitment with `scripts/write_phase_b_seal.py` (output: `docs/acceptance/PHASE_B_HOLDOUT_SEAL.json`).
- Add `SealRecord` to the public repo referencing the holdout Merkle root.
- Add one clean-runner acceptance test that validates the Merkle root without exposing labels.

**Acceptance:**
- `finance_quant.acceptance.seal` validates the Merkle root against the public `SealRecord`.
- Use counters documented: `SEAL-A` max two per epoch; `SEAL-B` exactly one.

---

## 5. Data contract for Phase B ingest

Every ingested record must carry:

```json
{
  "instrument_id": "internal-sym",
  "namespace": "bar",
  "vt": "2020-01-02T16:00:00-05:00",
  "kt": "2020-01-02T16:00:01.123000-05:00",
  "payload": { "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 1000 },
  "source": { "vendor": "polygon", "feed": "stocks/eod", "collection_method": "rest" },
  "ingest_receipt": { "ingest_run_id": "<uuid>", "landed_at": "<iso>", "raw_payload_hash": "<sha256>" },
  "revision": 1,
  "superseded_by": null
}
```

For corporate actions:
- `namespace`: `corporate_action`
- `payload`: `{ "type": "split", "ratio": 2.0, "announcement_date": "...", "ex_date": "...", "effective_date": "..." }`
- `kt` = announcement timestamp from Polygon, not ex-date or effective date.

---

## 6. Acceptance / verification

- **Property tests:** existing Hypothesis suite (`FQ-PROP-002`) runs against the new fixture.
- **Full benchmark:** `python -m finance_quant benchmark` (or `scripts/run_phase_b_benchmark.py`) orchestrates fixture freeze/load, B1–B5, Qlib train/eval, and LEAN replay in one run, writing `reports/phase_b_benchmark.json`.
- **Determinism drill:** `python -m finance_quant drill` (or `scripts/run_phase_b_determinism_drill.py`) runs the benchmark N times and asserts identical receipt hashes.
- **Cost-stress drill:** run LEAN replay with 2x slippage; verify returns degrade monotonically.
- **Fresh-runner drill:** a new venv + clean data directory reproduces the canonical fixture hash and B1–B5 receipt hashes.
- **Sealed holdout:** `scripts/generate_phase_b_holdout.py` creates the synthetic holdout under `data/fixtures/phase-b-holdout/`; `scripts/write_phase_b_seal.py` writes the public seal to `docs/acceptance/PHASE_B_HOLDOUT_SEAL.json`. The sealed Merkle root is `cc7d65a7e660456872d029e6851c9f88cdfd450e51db80b5af139dd27f59c2c4`.

---

## 7. Cost estimate

| Item | One-time | Monthly | Notes |
|---|---|---|---|
| Polygon research tier | — | ~$49–$199 | Required for full market; can prototype on Alpaca free |
| CI minutes (GitHub Actions) | — | ~$0–$20 | Existing free tier likely sufficient |
| Compute (local) | existing | — | Phase B stays local-subprocess only (#10 decision) |
| MLflow tracking server | — | $0 if local | Can use local SQLite/ filesystem store |
| LEAN cloud / data | — | $0 | Local LEAN runs only |
| **Total Phase B cash outlay** | **~$0** | **~$50–$220** | Controllable by vendor choice |

---

## 8. Risks and rollback

| Risk | Mitigation | Rollback |
|---|---|---|
| Polygon API changes or downtime | Adapter is thin; vendor-swappable | Revert to Alpaca adapter or synthetic fixture |
| `kt` semantics ambiguous for a vendor field | Document exact field mapping; add property test | Re-ingest with corrected `kt` mapping and new manifest hash |
| Qlib dependency breaks on Python 3.13 | Pin Python 3.11/3.12 in CI and pyproject.toml | Use existing venv / Docker pin |
| LEAN local setup fragile on Windows | Provide Docker path for LEAN runs | Skip LEAN slice and use Qlib backtest as temporary execution truth (explicitly labeled) |
| Fixture too large for CI | Shrink universe to 20 symbols for CI; full 100 for nightly | CI uses reduced fixture; full fixture pinned separately |

---

## 9. Decision gates

Before slice 1 starts, the owner must decide:

1. **Vendor:** Polygon (recommended), Alpaca fallback, or other?
2. **Universe:** S&P 100, Nasdaq-100, or custom list?
3. **Budget ceiling:** confirm monthly data spend is acceptable.
4. **Python pin:** confirm 3.11 or 3.12 for Qlib compatibility.

After slice 3 completes, decide whether to:
- Proceed to Qlib + LEAN (slices 4–5), or
- Expand the search-bakeoff lanes (#7) on the same fixture, or
- Add a new spike for training a mini local model.

After Phase B exits, the next milestone is **Phase C adversarial acceptance** using the sealed holdout from slice 6. Paper trading is gated behind that.

---

## 10. Summary

Phase B turns the existing V0 plumbing into an honest benchmark. The highest-value first step is **real data ingest** (slice 1), because every downstream slice — baselines, Qlib, LEAN, search lanes, and eventually paper trading — depends on a trustworthy `vt/kt` authority. Polygon is the recommended vendor. Automated model search and neurosymbolic KG experiments are intentionally out of Phase B scope; they should be evaluated against the Phase B benchmark once it exists.
