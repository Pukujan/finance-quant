# Current project state

<!-- MACHINE-STATE: architecture=WORKING_LOCAL_QUANT_WORKSTATION_PLUS_LAB status=LUNA_CANDIDATE_EXECUTION_READY active_issue=27 -->

## Active direction

Build and empirically improve the working local quant workstation through a fixed parallel research laboratory:

`real historical data -> PIT normalization -> immutable versioned knowledge/model components -> assembled historical benchmark -> parallel walk-forward arms -> canonical realized market outcomes -> full-information scoring/router -> isolated persistent local paper accounts -> browser workstation`

The former assurance-phase ladder and OSS architecture bakeoff are not product gates. Historical evidence remains as implementation history. New research is judged by direct product correctness and unseen realized market outcomes.

Live capital is out of scope. Local simulated paper trading is enabled.

### Luna execution update (2026-08-28)

- Market candidate lane implemented in `finance_quant/lanes/market.py`.
- Raw AAPL OHLCV and separately timestamped corporate actions published into
  `.lab-state/registry` from Yahoo chart data for 2023-01-01 through 2025-12-31.
- Development lab run completed with 751 canonical next-session outcomes and
  evaluation hash `b3d531720440ea71dfbfcc4db9b378c9dca266f29e9c92c8b9cb71f29875504c`.
- The run uses an explicit session-close knowledge-clock upper-bound assumption;
  it is not a substitute for historical first-known source timestamps.
- SEC filing/text and CompanyFacts lanes are now published and acceptance-clock
  tested; a RAG artifact is derived from the SEC filing artifact.
- Macro, news/event, temporal industrial-KG, and local model lane implementations
  are now present with focused correctness tests. A bounded GDELT replay is
  pinned for public development, but its pull has no distinct publication
  timestamps and required an explicit HTTP transport fallback; no GDELT
  predictive result is claimed.
- A real SEC regulatory-event artifact is now available for AAPL (25 8-K/6-K
  events, acceptance clocks preserved), and pinned JSONL replay validation is
  available for later news/KG source drops.
- A first 5-arm market/SEC/RAG/model-family matrix completed on 730 shared
  outcomes with evaluation hash
  `809e9e91053211f1d4a809128a65513bf434c6f8fdf0c55cb420c0a106d7a650`; its
  single-symbol tree result is exploratory only.
- Model/router/shadow integration is covered by a focused test proving prior-
  OOS-only routing and isolated idempotent zero-money account advancement.
- The contextual-router experiment completed over the same 730 shared outcomes
  (evaluation hash `809e9e91053211f1d4a809128a65513bf434c6f8fdf0c55cb420c0a106d7a650`)
  at 52.0548% directional accuracy; it underperformed the standalone tree and
  is retained as a negative development result.
- A pinned news/event replay artifact, a three-vintage ALFRED CPI replay, and a
  322-relation Wikidata industrial snapshot are now published. The Wikidata
  snapshot is correctly held out of the 2023-2025 score because its truthful
  retrieval cut is 2026-08-28.
- The multi-symbol matrix now covers AAPL/MSFT/AMZN with 2,197 shared outcomes
  (evaluation hash `a01ad41ac0e83c34fd59b0a289be28ba935684a2067c748416acf8fa96e34a9`),
  and the ALFRED macro-integrated matrix covers 1,503 outcomes (evaluation hash
  `f46f8be889b3f6e66fa22d8c2b12c03f84b2f96d3fe66eb9d55fd632bdf7a3d0`).
- The pinned GDELT replay covers 2,270 English-language article metadata
  records across AAPL/AMZN/MSFT from 2023–2025; its artifact is
  `727188f0b7e6455206890ab484cf41eaeddb32730da48b6ce4ae497c30bfdd8f` and its
  replay SHA-256 is `542560f6134cf4a869e125674dad15c65afaee76a38216ef7eb7f53c422ee685`.
- The GDELT compact-index integration matrix covers 1,503 shared outcomes
  (evaluation hash `5feebfaa3f9a469d90080fbd5174efb2b455a4475313437f6a44f8b21788faf7`);
  metadata presence does not change the fundamentals result.
- A separate 2020–2025 public extension covers 4,149 shared outcomes across
  AAPL/MSFT/AMZN (evaluation hash
  `0912e4e64c02dfd13da68a56cdf2c9a20fdea3ac60caacd4fbb2596978d388ba`). Its
  independent 80/20 OOS summary covers 831 decisions: the exploratory tree
  scored 53.4296% directional accuracy versus 48.9771% for raw price. The
  extension remains non-canonical because market knowledge time is still the
  documented session-close upper bound.
- A public training-only threshold fit was also evaluated on that extension.
  It selected per-symbol thresholds AAPL 75.81, AMZN 102.27, and MSFT 199.39
  from the first 80% of each symbol’s outcomes, then scored 53.4296% on the
  same 831 OOS decisions. The result is retained under
  `experiments/luna/trained-entity-tree-2020-2025/` and does not resolve
  `Q-MODEL-001`; the OOS slice is still late-period and the market clock is
  still an upper-bound assumption.
- A per-symbol chronological 80/20 OOS/regime summary and a contextual
  prior-OOS-only router run are retained under `experiments/luna/`; the router
  run covers 2,197 decisions and selects only among already-resolved candidate
  scores.
- Full current regression is `968 passed, 24 skipped`.
- Next concrete work: replace the development-only GDELT fallback with a
  pinned historical news source with authenticated/native clocks, obtain dated
  industrial relation evidence, and extend OOS/regime/model-family experiments
  without backdating current snapshots.
- The historical horizon, universe, and asset-class choice is explicitly open
  in `docs/plans/OPEN_SCOPE_QUESTIONS.md` (`Q-SCOPE-001`); the current
  2023–2025 US-equity slice is only an engineering-first public fixture.

## Fixed laboratory/control plane is Luna-ready

`finance_quant.lab` is now the fixed measuring/execution layer for Luna or other candidate-generating agents. Candidate workers can publish many data/KG/RAG/model versions and run them in parallel without owning historical labels, PIT cuts, scoring, evaluation identity, or paper-account truth.

The autonomous flow is:

1. publish immutable component artifacts;
2. assemble PIT historical benchmark snapshots from registered component versions and fixed canonical outcomes;
3. declare explicit arms or a bounded arm matrix;
4. run all affordable arms concurrently;
5. score every arm against the same realized outcome at each decision point;
6. preserve exact component/evaluation/run lineage;
7. route using prior resolved OOS results only;
8. advance surviving arms in isolated zero-money shadow paper accounts.

### Public CLI

Publish a component:

`python -m finance_quant lab publish-component SPEC.json PAYLOAD.json --registry .lab-state/registry --output artifact.json`

Assemble a benchmark:

`python -m finance_quant lab assemble-benchmark EVALUATION.json COMPONENTS.json --registry .lab-state/registry --output benchmark.json`

Run candidate arms:

`python -m finance_quant lab run benchmark.json candidates.json --state-dir .lab-state --parallel 16 --output result.json`

`EVALUATION.json`/the assembled benchmark owns canonical outcomes. `CANDIDATES.json` owns only candidate arm/component/model/retrieval configuration. Candidate files are rejected if they contain snapshots, outcomes, labels, benchmark data, or experiment metadata.

## Stable lab contracts

### Versioned components

`ComponentSpec` + `ComponentRegistry` provide content-addressed immutable artifacts with:

- lane/name/version;
- code/input-dataset identity;
- schema/ontology/extractor/parameter identity;
- parent artifacts and dependency DAG;
- immutable payload bytes;
- descendant queries for selective downstream invalidation.

A standard temporal-observation artifact uses schema:

`finance-quant.lab.temporal-observations.v1`

with observations carrying `entity`, `known_at`, optional valid-time interval, and payload. Global observations may use entity `*`.

### Multiple versions at one historical cut

A frozen snapshot may contain several versions of the same semantic lane simultaneously, e.g.:

`price@v2 | news@v3 | news@v4 | KG-retriever@v5 | KG-retriever@v6`

Each `ArmSpec` selects exact `(lane, artifact_hash)` components. One arm still uses at most one artifact per semantic lane, but different arms can select different versions from the same frozen snapshot. This directly supports A/B/C/... version flywheels.

### Benchmark assembly

`assemble_benchmark` reads registered temporal artifacts and freezes each version at each fixed decision time **after PIT filtering**. Future-known rows are absent from the frozen snapshot. Canonical realized outcomes remain a separate evaluation input.

### Arm matrices

Candidate files may declare a bounded matrix with:

- fixed base components;
- named versions for variant lanes;
- explicit lane combinations/interactions;
- multiple model executors/configs;
- `max_arms` hard ceiling.

The lab expands this into exact immutable `ArmSpec`s. It never silently invents a full Cartesian product beyond the combinations requested.

### Full-information execution

Every affordable arm can predict every eligible historical decision. One canonical outcome is materialized per entity/decision/horizon and every arm is scored against that exact same outcome ID/cost assumptions.

The standard-library thread runner is the dependency-light baseline. Ray/Optuna/Qlib may be adapters later, not prerequisites for correctness.

### Experiment identity

`ExperimentLedger.RunSpec` now includes:

- knowledge manifest hash;
- retrieval policy hash;
- arm spec hash;
- router config hash;
- **evaluation hash**.

The evaluation hash is derived from actual frozen snapshot IDs and actual canonical outcome IDs, so changing historical input content or the realized answer necessarily creates a different experiment identity even if a human dataset label was left unchanged.

### Router and shadow paper

The first inspectable router is an exponentially weighted expert ensemble that only consumes outcomes resolved by the current historical decision time. Future unresolved arm performance cannot affect earlier weights.

`ShadowPaperLab` maintains one persistent authoritative `VirtualAccountStore` per arm. Accounts are isolated, restart-safe/idempotent, and zero-money simulation only.

## Correctness evidence

Dedicated workflow: `.github/workflows/lab-control-plane.yml`.

Latest green code run: **33173989475** at SHA `4ce8be50ecdc453d0ece0db440bf2b93f693063b`.

Results:

- lab correctness suite: **23 passed**;
- targeted semantic source mutations: **9/9 killed, 0 survived**;
- public benchmark/candidate CLI smoke: **passed**;
- existing workstation regression: **4/4 passed**;
- smoke artifact ID: **9686784711**;
- smoke artifact ZIP SHA256: `a0bdbcc9c2708c82dee482408387aff3a5248c7c2843022cb53f7a9bd5826354`.

The nine mutation probes deliberately corrupt:

1. future-known PIT filtering;
2. simultaneous same-lane version preservation;
3. direct snapshot future-time guard;
4. exact component selection;
5. canonical outcome coverage;
6. evaluation identity dependence on realized outcomes;
7. router no-hindsight timing;
8. candidate benchmark/label separation;
9. shadow-account restart behavior.

All nine are detected by the executable tests.

The smoke proves `price`, `price+news@v3`, and `price+news@v4` can run concurrently from the same frozen snapshot and receive the same canonical outcome ID. This is a synthetic control-plane proof, not predictive-performance evidence.

## Working workstation MVP retained

`finance_quant.workstation` remains runnable with:

`python -m finance_quant workstation --ticker AAPL --start 2018-01-01 --capital 100000`

It still provides real Yahoo daily market history, SEC CompanyFacts PIT fundamentals, strict walk-forward ridge evaluation, persistent simulated paper execution, and browser inspection.

The public Luna lab now also has a real SEC-fundamentals development arm. On
the frozen 2023–2025 multi-symbol slice it scored **54.2249%** directional
accuracy over 1,503 shared outcomes, versus **50.0998%** for raw price. The
matrix identity is evaluation hash
`43dfa010b5b5506699ace88614996f1181d4160dff9720973644daaa3f793ef5` and batch
hash `1bea1647e531d704d7d8863fc0844cad17b1bbf76655dd11cbded78f70453dd9`.
This is a public exploratory result, separate from the workstation MVP’s
existing walk-forward baseline and not evidence of holdout or live performance.
The fundamentals arm’s independent per-symbol 80/20 OOS summary was
**53.7954%** over 303 decisions versus **51.4851%** for raw price. The
development CPI-momentum arm was neutral because its three available vintage
cuts were conservative year-end bounds, so it is not evidence of macro value.
The shallow decision-tree choice is still open: its current `close >= 150`
rule is a transparent control, not a trained or approved production model.
The question and resolution criteria are recorded in
`docs/plans/OPEN_MODEL_QUESTIONS.md` as `Q-MODEL-001`.

The longer public market/SEC extension at
`experiments/luna/multisymbol-public-dev-2020-2025/` covers 4,149 outcomes
from the same three symbols over 2020–2025. Its per-symbol chronological OOS
summary at `experiments/luna/multisymbol-public-oos-regime-2020-2025/` covers
831 held-out decisions. The threshold-tree control scored **53.4296%** versus
**48.9771%** for raw price on that OOS slice, with compounded strategy net
returns of **+9.3031%** and **−19.3237%**, respectively, under the existing
2-bps development convention. This is exploratory only: it does not resolve
`Q-MODEL-001`, prove profitability, or correct the market clock limitation.

The training-only entity-threshold control is recorded at
`experiments/luna/trained-entity-tree-2020-2025/`, with its OOS summary at
`experiments/luna/trained-entity-tree-oos-regime-2020-2025/`. It selected
  different thresholds for each symbol from training data only and matched the
  fixed tree’s 53.4296% OOS accuracy, so the fixed `150` threshold is not
  validated as a universal value.
- The calendar/cost diagnostic for that trained control shows 47.41% accuracy
  in 2022 and compounded net return falling from +363.09% at 2 bps to +39.82%
  at 5 bps and −81.01% at 10 bps. It is retained as negative stability
  evidence, not a profitability or promotion claim.

The workstation’s real-data historical paper replay is now extended to
2018–2025 using the existing strict walk-forward ridge and durable local
virtual-account path. The corrected frozen public run is retained at
`experiments/luna/workstation-paper-replay-2018-2025-frozen-v2/`, with the
original frozen inputs at
`experiments/luna/workstation-paper-replay-2018-2025-frozen/inputs/`. The v2
run was then restarted from its persisted checkpoints and produced the same
account state hashes without duplicate effects.
Each symbol has 2,011 daily bars, 1,824 walk-forward predictions, next-session
open target rebalances, next-session close marks, 95% allocation, and 2 bps
slippage. Starting from $100,000 per isolated account, the marked results were:

- AAPL: baseline **$372,486.44 / +272.4864% / −40.3874% max drawdown**;
  SEC-informed **$204,288.14 / +104.2881% / −38.3380%**.
- MSFT: baseline **$404,867.88 / +304.8679% / −23.8158%**;
  SEC-informed **$251,546.30 / +151.5463% / −38.0375%**.
- AMZN: baseline **$87,714.15 / −12.2858% / −59.5901%**;
  SEC-informed **$168,199.60 / +68.1996% / −50.4025%**.

Across three separate $100,000 accounts, the equal-capital totals were
**$865,068.47 (+188.3562%)** for baseline and **$624,034.03 (+108.0113%)**
for SEC-informed. These are marked local simulations, not broker paper or
live returns, and are not a claim that SEC information improves the model:
the informed arm loses to baseline on AAPL and MSFT and wins on AMZN. The
public input snapshots are hashed and the independent repeat matched all
prediction metrics, fills, NAVs, and account state hashes exactly. The
corrected v2 accounts also persist a run fingerprint and atomic per-session
checkpoint; restarting the completed run produced the same state hashes with
no duplicate effects. Frozen cost sensitivity across the three separate
accounts produced aggregate marked totals of **$951,632.84 at 0 bps**,
**$865,068.47 at 2 bps**, **$750,119.78 at 5 bps**, and **$592,973.35 at
10 bps** for baseline, versus **$675,630.91**, **$624,034.03**,
**$553,544.34**, and **$453,524.03** for SEC-informed. The
source clock limitation remains: adjusted Yahoo bars have no source-native
historical knowledge timestamps, while SEC facts use filed date as knowledge
time.

The replay harness is `scripts/run_workstation_paper_replay.py` (SHA-256
`2637a2f91f2405a5ad8772eda9ceb05b5ab7e94db2348cde6573a3008e8553a4`).

Real AAPL/SEC workflow `33146074713` produced 1,988 evaluated walk-forward predictions:

- price-only directional accuracy: **53.3702%**;
- price + current small SEC-fundamental feature set: **51.8612%**;
- delta: **-1.5091 percentage points**.

The current tiny SEC-fundamental set hurts this baseline. Do not claim KG predictive value from it. Historical simple long/cash metrics are also not a realistic cost-complete strategy result.

Existing zero-money paper proof remains:

- 2026-08-26 signal persisted;
- 2026-08-27 simulated next-open fill: **BUY 305 AAPL @ 310.61209779052734**;
- marked NAV: **$101,210.2061** from $100,000 starting cash.

That proves signal -> persistent state -> simulated execution -> marked account, not profitability.

## Active durable issues

- #12 master working local predictive quant workstation
- #26 workstation MVP + empirical iteration
- #27 versioned knowledge lanes + parallel full-information laboratory
- #28 component registry/manifests/DAG
- #29 historical PIT data lanes
- #30 parallel arm scheduler/shared outcomes
- #31 scoring/router/shadow paper
- #32 workstation experiment/lineage UI
- #19 temporal KG + PIT-safe RAG
- #21 local model research/training
- #18 continuous local paper refresh
- #17 browser workstation UX

## Next exact action

The shared executioner is ready. **Do not redesign its benchmark/outcome semantics inside candidate lanes.**

The initial parallel Luna worker wave is complete. The next bounded research
wave against #29, #19 and #21 is:

1. clean walk-forward/OOS ablation for the new SEC-fundamentals arm;
2. source-native historical clocks for market/news/macro inputs;
3. pinned financial news replay with publication/first-seen clocks;
4. dated supplier/customer/competitor evidence suitable for historical scoring;
5. stronger local model families, contextual routing, and explicit OOS/regime splits.

The scope decision for longer history, broader equities, crypto, FX, and
prediction markets remains open; see `docs/plans/OPEN_SCOPE_QUESTIONS.md`.

Each worker should emit immutable versioned temporal component artifacts and/or arm executors. The lab then assembles the fixed PIT benchmark and expands/runs explicit or matrix arms concurrently.

First substantive experiment family:

`price | +fundamentals | +news/hype | +events | +supply/competitors | +macro | +RAG | +bounded-KG | combined | contextual router`

across multiple symbols/regimes. Subsequent realized market prices remain the objective judge.

## Safety scope

- Local simulated paper: **ENABLED**.
- Parallel per-arm shadow paper: **ENABLED as simulation**.
- Broker-hosted paper: **not used**.
- Live capital: **DISABLED / out of scope**.
- Existing private/sealed holdout contents must not be inspected or optimized against without explicit authorization.

## Required read order for a fresh implementation session

1. `AGENTS.md`
2. this file
3. `docs/handoffs/LATEST.md`
4. #27, then #28–#32
5. #29/#19/#21 for candidate work
6. `finance_quant/lab/`, `tests/test_lab_*.py`, `scripts/run_lab_mutation_probes.py`
7. `finance_quant/workstation/` and `tests/test_workstation_product.py`
8. older assurance material only when relevant to a concrete product bug
