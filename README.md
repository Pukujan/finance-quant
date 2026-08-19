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

## Verify

```text
python -m venv .venv
.venv\Scripts\pip install pytest hypothesis
.venv\Scripts\python -m pytest tests
```

Useful scripts:

- `scripts/run_pit_bakeoff.py` — Q1–Q8 PIT harness
- `scripts/run_b1_b5_campaign.py` — boring baseline campaign
- `scripts/run_search_batch.py` — RANDOM+GP trials into the ledger
- `scripts/demo_exit_campaign.py` — crash-surviving fan-in proof
