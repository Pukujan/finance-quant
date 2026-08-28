# 2026-08-28 — parallel lab control-plane handoff

Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #27
Safety scope: local simulated paper only; no broker/live capital

This session converted the versioned-knowledge/parallel-arm design in #27 into executable code under `finance_quant/lab/`.

## Landed capabilities

- immutable content-addressed component registry and manifest identities;
- PIT lane data and frozen decision snapshots;
- deterministic arm and experiment-batch identities;
- exact arm-manifest-to-frozen-artifact verification;
- parallel candidate execution using frozen `ArmContext` only;
- canonical outcome join after candidate prediction;
- full-information per-arm scoring against one outcome ID per decision;
- ExperimentLedger knowledge/retrieval/arm/router identity fields;
- no-hindsight exponentially weighted expert router;
- strict benchmark/candidate CLI separation;
- persistent isolated shadow paper accounts per arm using `VirtualAccountStore`;
- focused property/integration/restart/idempotency tests;
- dedicated `lab-control-plane` GitHub Actions workflow and public smoke fixtures.

## Public execution interface

`python -m finance_quant lab run BENCHMARK.json CANDIDATES.json --state-dir .lab-state --parallel N --output result.json`

Candidate definitions cannot contain snapshots, outcomes, labels or benchmark data. The benchmark file owns those inputs.

Smoke files:

- `fixtures/lab/benchmark-smoke.json`
- `fixtures/lab/candidates-smoke.json`

## Important semantic boundaries

Candidate agents may own:

- component/extractor/model implementation;
- declared knowledge lanes;
- retrieval/model/feature/portfolio configuration;
- executor code that consumes `ArmContext`.

Candidate agents do not own:

- PIT snapshot freeze;
- realized outcomes;
- score calculation;
- ExperimentLedger run identity;
- historical router cutoff;
- authoritative paper-account state.

## Tests added

- `tests/test_lab_control_plane.py`
- `tests/test_lab_manifest_guard.py`
- `tests/test_lab_shadow.py`

The dedicated workflow also reruns `tests/test_workstation_product.py` to protect the existing working product.

## CI evidence during build

Earlier successful runs in this session:

- `33149223541` — initial fixed laboratory tests and workstation regression;
- `33149292495` — manifest guard;
- `33149419972` — benchmark/candidate separation.

A later run is triggered by the shadow-paper and final lab changes; verify latest branch-head `lab-control-plane` conclusion before integrating new candidate lanes.

## Known intentional limitations

- scheduler baseline is dependency-light `ThreadPoolExecutor`; Ray/Optuna/Qlib are future adapters, not prerequisites;
- smoke benchmark is synthetic and exists to validate the control plane, not predictive usefulness;
- real historical news/macro/supply-chain/RAG lanes remain #29/#19 work;
- first router is inspectable exponential weighting, not the final contextual model;
- workstation leaderboards/decision-inspector integration remains #32/#17 work.

## Next exact action

Give Luna issues #29, #19 and #21 plus this fixed lab interface. Let it spawn independent subagents for historical PIT data, KG/RAG and model candidates, publish them through the immutable component/arm contracts, and use the lab as executioner across multiple symbols/regimes.
