# finance-quant

Local point-in-time quantitative research, walk-forward evaluation, and zero-money simulated paper trading.

The working product and its fixed experiment laboratory are now on `main`. The repo is no longer organized around the former assurance/promotion ladder; current work is judged by executable product correctness and subsequent realized market outcomes.

> **Safety scope:** local simulated paper trading only. No broker credentials, live order authority, or live capital.

## What works now

### Local predictive workstation

`finance_quant.workstation` provides a runnable local research/paper-trading surface with:

- real daily market history from Yahoo;
- historical SEC CompanyFacts with filing-date point-in-time visibility;
- price/trend features;
- current small PIT fundamental feature set;
- strict walk-forward ridge evaluation;
- a separate current/live prediction with no unresolved label leakage;
- persistent SQLite simulated cash, positions, orders and fills;
- next-open simulated execution with configurable starting capital and slippage;
- browser inspection of prices, predictions, realized outcomes, SEC evidence and paper-account state.

Run it:

```bash
python -m pip install -e ".[test]"
python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000
```

JSON mode:

```bash
python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000 --json
```

The current structured SEC lane should be understood as **PIT fundamentals**, not a full knowledge graph. Internal legacy field names may still use `kg`; a real historical temporal KG/RAG is the next product wave.

### Fixed parallel research laboratory

`finance_quant.lab` is the execution/measuring layer for candidate data, KG/RAG, feature and model versions.

It owns:

- historical PIT snapshot construction;
- canonical subsequent market outcomes;
- benchmark/candidate separation;
- exact component/evaluation/run identity;
- parallel arm execution and scoring;
- no-hindsight router timing;
- persistent isolated shadow-paper accounts.

Candidate workers do **not** own historical labels or relax the knowledge cutoff.

Standard component payload schema:

```text
finance-quant.lab.temporal-observations.v1
```

The lab can keep several versions of the same semantic lane visible at one historical decision cut, while each arm selects an exact `(lane, artifact_hash)` version. This supports direct A/B/C/... comparison against the same realized future price.

## Lab CLI

Publish one immutable component version:

```bash
python -m finance_quant lab publish-component \
  SPEC.json PAYLOAD.json \
  --registry .lab-state/registry \
  --output artifact.json
```

Assemble registered component versions into the fixed PIT benchmark:

```bash
python -m finance_quant lab assemble-benchmark \
  EVALUATION.json COMPONENTS.json \
  --registry .lab-state/registry \
  --output benchmark.json
```

Run explicit candidate arms or a bounded candidate matrix in parallel:

```bash
python -m finance_quant lab run \
  benchmark.json candidates.json \
  --state-dir .lab-state \
  --parallel 16 \
  --output result.json
```

Synthetic smoke fixtures are in `fixtures/lab/`. They prove the control plane and component-version comparison machinery, not market alpha.

## Current empirical baseline

The existing real AAPL workstation run from 2018 through 2026-08-27 produced 1,988 historical walk-forward predictions.

- price-only directional accuracy: **53.3702%**;
- price + current small PIT SEC-fundamental set: **51.8612%**;
- delta: **-1.5091 percentage points**.

So the current tiny fundamental set made this simple AAPL ridge baseline worse. That negative result is retained; it is not evidence that a richer temporal KG/RAG is useless.

The simulated paper path has also been exercised with real data: a signal persisted on 2026-08-26, then the next available session executed a simulated AAPL buy and marked the persistent account. This proves the signal -> persisted decision -> simulated fill -> account-state loop, not profitability.

Historical simple long/cash metrics in the workstation are not yet a cost-complete strategy return and should not be treated as credible profitability evidence.

## Architecture

```text
real historical information
        |
        v
PIT normalization / known_at clocks
        |
        v
immutable versioned components
(price / fundamentals / news / events / macro / KG / RAG / models)
        |
        v
fixed historical benchmark
        |
        v
parallel exact-version arms
        |
        v
predictions BEFORE outcome join
        |
        v
same canonical subsequent market outcome
        |
        v
OOS scoring + experiment lineage
        |
        v
prior-resolved-only router
        |
        v
isolated zero-money shadow paper
        |
        v
browser workstation / empirical iteration
```

Historical prices up to a decision cutoff may be model input. Prices after that cutoff are labels/evaluation only and must not leak into features, retrieval, routing or predictions.

## Luna handoff: start here

Yes—there is a durable handoff for Luna/subagents on `main`.

Read in this order:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md)
3. [`docs/handoffs/LATEST.md`](docs/handoffs/LATEST.md)
4. [`docs/plans/LUNA_CANDIDATE_PROTOCOL.md`](docs/plans/LUNA_CANDIDATE_PROTOCOL.md)
5. GitHub issues **#27, #29, #19 and #21**
6. `finance_quant/lab/` and `tests/test_lab_*.py`

### Ownership split

**Core/integration owner**

- preserve the fixed benchmark/PIT/outcome/account semantics;
- review and integrate cross-lane changes;
- run merge gates;
- keep `main` coherent;
- compare empirical results fairly.

**Luna / candidate workers**

- build competing versioned data/features/KG/RAG/models;
- publish immutable temporal component artifacts or arm executors;
- run them through the fixed lab;
- report exact artifact hashes, arm IDs, evaluation hashes and OOS results;
- keep negative experiments in lineage.

Luna should not redesign the answer key inside a candidate lane.

## Next implementation wave for Luna

Run these workstreams in parallel where practical:

1. **Raw market history** — raw OHLCV plus separately timestamped splits, dividends and corporate actions.
2. **SEC documents** — historical filing text, filing timestamps, amendments and provenance.
3. **Macro vintages** — ALFRED-style historical releases/revisions where available.
4. **Historical financial news/events** — publication/first-known clocks, entity resolution, syndication dedup, attention/hype features.
5. **Industrial temporal graph** — supplier/customer/competitor/product/industry/event relationships with evidence, time, confidence and materiality. Apple/Samsung-style component-specific supplier relationships belong here.
6. **PIT-safe RAG** — historical corpus filtering before ranking/retrieval, with evidence IDs and provenance.
7. **Stronger local models** — interpretable linear/logistic, tree/boosting/ranking families, then selected temporal/neural models where useful.

First substantive experiment family:

```text
price
| +fundamentals
| +news/hype
| +events
| +supply/competitors
| +macro
| +RAG
| +bounded-KG
| combined
| contextual router
```

Run across multiple symbols and regimes using the same subsequent realized market outcomes.

## Direct correctness checks

The product/lab CI includes direct tests for the bugs that would invalidate the experiment:

- future-known data cannot enter an earlier PIT snapshot;
- later market shocks cannot change earlier walk-forward predictions;
- historical labeled predictions are separate from the current live signal;
- exact component versions are preserved and selected explicitly;
- candidates cannot smuggle benchmark labels/outcomes;
- evaluation identity changes when actual frozen inputs/outcomes change;
- router weights cannot use unresolved future outcomes;
- persistent paper accounts are restart-safe and idempotent;
- targeted source mutation probes must be caught.

The clean product integration also passes the repository-wide pytest/smoke workflow and the retained Phase-B benchmark/determinism verifier.

## Useful commands

```bash
python -m finance_quant help
python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000
python -m finance_quant lab --help
python -m pytest tests/test_workstation_product.py -q
python -m pytest tests/test_lab_*.py -q
python scripts/run_lab_mutation_probes.py
python -m pytest tests -q
python scripts/smoke.py
```

Older Phase-B and assurance-era implementation remains in the repository where still useful as historical substrate or compatibility code, but it is not the active product roadmap.
