# Handoff — Luna-ready versioned parallel experiment executioner

Date: 2026-08-28
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #27
Product mode: local research + simulated paper only; no broker/live capital

## State

The fixed research laboratory is now implemented and green. Luna/subagents can publish many competing data/KG/RAG/model versions and use the repository itself as the executioner/measuring machine.

The control plane, not candidate code, owns:

- historical PIT snapshot construction;
- canonical realized outcomes;
- evaluation/run identity;
- scoring;
- no-hindsight router timing;
- experiment ledger truth;
- per-arm simulated paper-account truth.

Candidate workers own component/model implementations and version proposals.

## Autonomous flow

### 1. Publish immutable versioned component artifacts

`python -m finance_quant lab publish-component SPEC.json PAYLOAD.json --registry .lab-state/registry --output artifact.json`

Temporal component payload schema:

`finance-quant.lab.temporal-observations.v1`

Each observation has:

- `entity` (`*` allowed for global/macro observations);
- `known_at`;
- optional `valid_from` / `valid_to`;
- component-specific payload.

### 2. Assemble the fixed PIT benchmark

`python -m finance_quant lab assemble-benchmark EVALUATION.json COMPONENTS.json --registry .lab-state/registry --output benchmark.json`

`EVALUATION.json` owns fixed canonical outcomes and experiment settings. `COMPONENTS.json` is just the artifact hashes to make available at historical decision cuts.

Benchmark assembly reads the registered artifacts, filters by PIT visibility and freezes all visible versions. A future-known observation cannot enter an earlier snapshot.

### 3. Declare candidates

Candidate files may contain explicit arms and/or a bounded `matrix`.

Every arm selects **exact** `(lane, artifact_hash)` components. Candidate code does not supply its own manifest hash; the lab derives it.

A frozen snapshot can simultaneously contain e.g.:

`price@v2 | news@v3 | news@v4 | KG@v5 | KG@v6`

so different arms can compare versions directly against the same future outcome.

The matrix expander supports:

- fixed base components;
- named versions for variant lanes;
- explicitly requested lane combinations;
- multiple model executors/configs;
- `max_arms` ceiling.

It does not silently generate an unbounded Cartesian product.

### 4. Execute all affordable arms

`python -m finance_quant lab run benchmark.json candidates.json --state-dir .lab-state --parallel 16 --output result.json`

Every arm predicts before the canonical outcome is joined. Every arm at a decision receives the exact same outcome ID and cost assumptions.

The result records:

- batch hash;
- evaluation hash;
- every prediction;
- every score;
- per-arm summary metrics.

`evaluation_hash` depends on the actual frozen snapshot IDs and actual outcome IDs, so changing either changes the ExperimentLedger run identity even if a human dataset label was accidentally left unchanged.

### 5. Route/paper

The first expert router uses prior resolved OOS results only. Outcomes that have not resolved by the historical decision time cannot affect its weights.

`ShadowPaperLab` provides one persistent zero-money `VirtualAccountStore` per arm, with restart/idempotency and account isolation.

## Stable implementation surfaces

`finance_quant/lab/`:

- `core.py` — immutable component/arm/snapshot/outcome identities and PIT semantics;
- `registry.py` — content-addressed artifact store + dependency DAG;
- `benchmark.py` — standard temporal-observation schema + component-to-PIT-benchmark assembly;
- `matrix.py` — bounded declarative arm expansion;
- `runner.py` — parallel prediction, canonical full-information scoring, evaluation identity, ledger writes, no-hindsight router;
- `shadow.py` — isolated persistent simulated accounts;
- `cli.py` — publish / assemble / run public interface;
- `demo.py` — synthetic deterministic smoke executor only.

`ExperimentLedger.RunSpec` includes knowledge/retrieval/arm/router identity plus `evaluation_hash`.

## Latest correctness evidence

Dedicated workflow: `.github/workflows/lab-control-plane.yml`.

Latest green code run: **33173989475** on SHA `4ce8be50ecdc453d0ece0db440bf2b93f693063b`.

- lab tests: **23 passed in 1.90s**;
- targeted source mutation probes: **9 killed / 0 survived**;
- public CLI smoke: **passed**;
- existing workstation regression: **4 passed**;
- smoke artifact ID: **9686784711**;
- artifact ZIP SHA256: `a0bdbcc9c2708c82dee482408387aff3a5248c7c2843022cb53f7a9bd5826354`.

The mutation probes prove current tests detect direct corruptions to:

- future-known PIT filtering;
- simultaneous same-lane component versions;
- direct future snapshot construction;
- exact component selection;
- canonical outcome coverage;
- actual evaluation-content identity;
- router hindsight;
- candidate label/benchmark separation;
- shadow-account restart semantics.

The smoke concurrently ran:

- `price` -> +0.0100 prediction;
- `price + news@v3` -> +0.0300;
- `price + news@v4` -> -0.0050;

from the same frozen snapshot and scored all three against one canonical outcome ID. This is synthetic infrastructure evidence, not market-alpha evidence.

## Existing real product result remains

The workstation real-data result is unchanged:

- AAPL window through 2026-08-27;
- 1,988 walk-forward predictions;
- price-only directional accuracy **53.3702%**;
- current tiny SEC-fundamental lane **51.8612%**;
- delta **-1.5091 pp**.

Current SEC fundamentals do not prove KG value.

Existing zero-money paper proof:

- 2026-08-26 signal persisted;
- simulated 2026-08-27 next-open fill BUY 305 AAPL @ 310.61209779052734;
- marked NAV $101,210.2061 from $100,000.

This proves the execution path, not profitability.

## Luna execution assignment

Use #29, #19 and #21 as parallel candidate workstreams. Spawn independent workers for:

1. raw OHLCV + timestamped splits/dividends/corporate actions;
2. SEC filing text/amendments;
3. ALFRED macro vintages;
4. historical financial news/events + syndication dedup + attention/hype features;
5. industrial supplier/customer/competitor relationships;
6. bounded temporal graph retrieval / PIT-safe RAG;
7. stronger local predictive model families.

Each worker should publish versioned temporal component artifacts or arm executors through the stable lab interfaces. Do not redesign benchmark/outcome semantics inside those lanes.

First real candidate family:

`price | +fundamentals | +news/hype | +events | +supply/competitors | +macro | +RAG | +bounded-KG | combined | contextual router`

across multiple symbols/regimes.

## Durable issue map

- #27 parent laboratory/flywheel
- #28 registry/DAG
- #29 historical PIT data
- #30 arm scheduler/shared outcomes
- #31 scoring/router/shadow paper
- #32 experiment UI
- #19 temporal KG + PIT-safe RAG
- #21 local model research

## Important boundary

The private/sealed holdout repository was not inspected or rerun. Do not inspect its cases/labels unless a later explicit authorization permits that. Normal product iteration should use public/fixed historical evaluation sets and future realized outcomes.
