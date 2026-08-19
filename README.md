# finance-quant

Reproducible quantitative research and trading laboratory.

Project planning and architecture are tracked in GitHub Issues. FOSSIL and Cortex are
external integrations, not this repository's ownership boundary.

## Current V0 (main)

Executable plumbing, not live trading:

- Bitemporal PIT store (SQLite + JSONL+manifest) with restatement/delist/split fixture
- Tier-1 IR, temporal checker, reference interpreter, Qlib compiler
- Native orchestration (WorkOrders, attempts, local backend, deterministic fan-in)
- Append-only ExperimentLedger + MLflow-compatible export + fresh-env rerun receipt
- B1–B5 boring baselines (SMA, walk-forward, momentum, cross-sectional rank, buy-and-hold)
- Proposal-only RANDOM/GP search lanes (no promotion authority)
- Sealed-holdout commitment interface (cases stay off-repo)
- Mechanical risk veto, same-bar fill contract, promotion-ladder conformance
- GitHub Actions pytest on every push (`requirements-dev.txt`)
- Optional TimescaleDB/XTDB PIT adapters (skipped in CI unless DSN env vars are set)
- Optional ArcticDB PIT adapter (skipped unless `arcticdb` is installed; Apache-converted versions only)
- Generated LEAN algorithm skeleton with execution-contract constants and same-bar fill contract
- 491+ tests covering PIT leakage, restatements, survivorship, graph as-of, search floors, risk veto, fill rules, worker authority, evidence lineage, promotion ladder
- Smoke runner (`scripts/smoke.py`) and `python -m finance_quant verify` exercised in CI after pytest

## Verify

```text
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest tests
```

Useful scripts:

- `scripts/run_pit_bakeoff.py` — Q1–Q8 PIT harness
- `scripts/run_b1_b5_campaign.py` — boring baseline campaign
- `scripts/run_search_batch.py` — RANDOM+GP trials into the ledger
- `scripts/run_b2_via_scheduler.py` — B2 folds as native WorkOrders
- `scripts/run_search_scorecard.py` — RANDOM vs GP rank-IC scorecard (propose-only)
- `scripts/run_rank_ic_report.py` — B1–B5 walk-forward rank IC
- `scripts/run_two_stage.py` — feature_eval then lean_replay
- `scripts/smoke.py` — pytest + bake-off + campaign + scorecard
- `python -m finance_quant help` — list packaged command entrypoints
