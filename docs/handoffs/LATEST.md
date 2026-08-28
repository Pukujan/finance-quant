# Handoff — fixed parallel research laboratory ready for candidate agents

Date: 2026-08-28
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #27
Product mode: local research + simulated paper only; no broker/live capital

## What changed

The repository now has an executable **fixed laboratory/control plane** so Luna or another multi-agent implementation system can generate many candidate KG/RAG/data/model arms without owning the benchmark, future labels, scoring semantics or paper-account truth.

Product loop:

`fixed historical benchmark -> PIT snapshot freeze -> candidate arms -> parallel predictions -> one canonical realized outcome per decision -> full-information scoring -> prior-OOS-only router -> isolated shadow paper -> workstation/leaderboards`

The former assurance-phase ladder remains historical implementation material, not the roadmap.

## Run interface for Luna

Use:

`python -m finance_quant lab run BENCHMARK.json CANDIDATES.json --state-dir .lab-state --parallel 16 --output result.json`

Two separate files are intentional:

- `BENCHMARK.json` owns experiment metadata, historical candidate data/PIT clocks, decision cuts and realized outcomes;
- `CANDIDATES.json` owns only arm definitions, lane declarations, executor references and candidate configuration.

The candidate loader rejects snapshots/outcomes/labels/benchmark data. A candidate therefore cannot change the future answer it is judged against through the normal execution interface.

Templates:

- `fixtures/lab/benchmark-smoke.json`
- `fixtures/lab/candidates-smoke.json`

## Control-plane implementation

New `finance_quant/lab/` package:

- `core.py` — immutable component/manifest/arm/batch identities; PIT lane data and snapshot freeze; candidate-only `ArmContext`; canonical outcomes and scores;
- `registry.py` — content-addressed immutable component artifacts, SQLite metadata, parent DAG and descendant queries;
- `runner.py` — deterministic sequential/parallel arm execution, exact manifest guard, canonical full-information scoring, ExperimentLedger persistence and first no-hindsight expert router;
- `cli.py` — separate benchmark/candidate execution interface;
- `shadow.py` — one persistent zero-money `VirtualAccountStore` per arm, restart-safe/idempotent and isolated;
- `demo.py` — deterministic smoke executor only.

Top-level CLI now exposes `finance-quant lab`.

`ExperimentLedger.RunSpec` was extended compatibly with:

- `knowledge_manifest_hash`
- `retrieval_policy_hash`
- `arm_spec_hash`
- `router_config_hash`

## Correctness tests

`tests/test_lab_control_plane.py`, `tests/test_lab_manifest_guard.py`, and `tests/test_lab_shadow.py` cover the fixed semantics that candidate agents must not be able to change accidentally:

- deterministic content/artifact identities;
- immutable old component versions;
- DAG descendant isolation;
- deterministic manifests and one artifact per lane;
- property-based future-known data insertion cannot alter an earlier snapshot;
- direct future-known snapshot construction rejected;
- arm sees only declared lanes;
- claimed knowledge manifest must equal exact frozen lane artifacts;
- sequential == parallel for deterministic arms;
- exact canonical outcome coverage and same outcome ID for all arms at a decision;
- router ignores outcomes unresolved at its decision time;
- ExperimentLedger run identities are idempotent and arm-sensitive;
- candidate file cannot smuggle benchmark outcomes/labels;
- shadow accounts are isolated by arm, survive restart and do not duplicate the same simulated transition;
- multi-instrument shadow valuation requires explicit marks rather than inventing prices.

## Green CI evidence

Dedicated workflow: `.github/workflows/lab-control-plane.yml`.

Run **33149664715** completed successfully on control-plane code SHA `e67335d4e55490acbfef152cee0cb0036d0fd0a9`:

- fixed laboratory correctness suite: **14 passed in 4.86s**;
- autonomous separated benchmark/candidate CLI smoke: **passed**;
- existing workstation regression: **4 passed in 0.87s**;
- smoke output artifact: `lab-smoke-result`, artifact ID **9677180076**;
- artifact SHA256: `47d8c009235254a2ed787404d6fe6a8fd72465d013ae735853bb4aaf547ea0e4`.

The smoke run produced price and price+news predictions from the same frozen snapshot and then scored both against the exact same canonical outcome ID. A deliberately future-known news record was present in the benchmark input and was excluded by the historical snapshot freeze.

## Existing workstation result retained

The working real-data workstation remains intact. Real AAPL/SEC workflow `33146074713` produced 1,988 walk-forward predictions:

- price-only directional accuracy: 53.3702%;
- price + current small SEC-fundamental set: 51.8612%;
- current knowledge delta: -1.5091 pp.

The current small SEC fundamentals do **not** prove KG value. The point of the new laboratory is to test richer historical information lanes objectively and in parallel.

The existing real-data paper proof remains:

- signal 2026-08-26;
- BUY 305 AAPL next open 2026-08-27 @ 310.61209779052734;
- marked NAV $101,210.2061 from $100,000.

This is simulated paper evidence only, not profitability evidence.

## Durable issue map

- #27 parent flywheel/control plane
- #28 component registry/DAG
- #29 historical PIT data lanes
- #30 parallel arm scheduler/shared outcomes
- #31 scoring/router/shadow paper
- #32 workstation experiment UI
- #19 temporal KG + PIT-safe RAG
- #21 model research/training

The shared interfaces above are now code, not just issue prose. Candidate subagents should adapt to these interfaces rather than redesigning benchmark/outcome semantics locally.

## Next exact action for Luna

Spawn parallel candidate workers against #29, #19 and #21:

1. raw OHLCV + timestamped corporate actions;
2. SEC filing text/amendments;
3. ALFRED macro vintages;
4. historical news/event ingestion + syndication dedup;
5. industrial/supplier/customer/competitor relation extraction;
6. bounded temporal graph retrieval / PIT-safe RAG;
7. stronger local model families.

Have each worker publish immutable component artifacts/arm executors and candidate definitions. Run all affordable arms through the fixed benchmark runner. Do not let candidate code construct realized labels or read live/unfrozen data directly.

First substantive experiment set:

`price | +fundamentals | +news/hype | +events | +supply/competitors | +macro | +RAG | +bounded-KG | combined | router`

across multiple symbols/regimes. Subsequent realized prices remain the objective judge.
