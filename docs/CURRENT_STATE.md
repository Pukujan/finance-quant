# Current project state

<!-- MACHINE-STATE: architecture=ADAPTIVE_MODULAR_QUANT_PORTFOLIO_ENGINE status=CONTRACT_RECONCILIATION_BEFORE_PARALLEL_BUILD active_issue=35 -->

## Latest durable continuation package

Read `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md` before resuming architecture/implementation work. It captures the full 2026-08-28 design session and the newest correction that occurred after #35/#36 were initially written.

## Active product direction

The product is now best framed as a **local adaptive modular multi-strategy quantitative portfolio engine**:

`heterogeneous signals -> model/meta weights -> forecast distributions/ranks -> portfolio allocation -> local zero-money paper -> realized outcomes -> weight/version evolution`

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
At decision time `T`, every participating signal/model may use only information legitimately knowable at `T`. The engine combines independent versioned strategy/signal providers, decides how much trust each deserves under the current context, converts forecasts into explicit target allocations/trades/cash, executes only local simulated paper, and updates future strategy credibility from subsequently realized outcomes.

**MarketState, temporal KG/RAG, news/epistemics and vendor pre-quantized feeds are optional signal-provider families, not the product itself.** Price/momentum/breakout/volatility/fundamental/macro strategies must fit the same engine without requiring MarketState.

Forward paper is a continuous benchmark, not a later deployment stage. Every executable credible strategy/policy should begin accumulating prospective paper history as soon as it can produce a valid decision.

Live capital remains out of scope.

## Immediate architecture reconciliation

Architecture proposal #35 and foundation issue #36 were written before the final strategy-centric clarification and may over-center the Market State Fabric.

Before broad implementation, the next session must reconcile #35/#36 around the parent structure:

```text
Adaptive Quantitative Portfolio Engine
    ├── Signal Provider Framework
    │     ├── price / momentum / breakout / volatility
    │     ├── fundamentals / macro
    │     ├── vendor quantified data
    │     ├── MarketState / epistemics / trends
    │     ├── KG / RAG / exposure / analog retrieval
    │     └── future signal families
    ├── Forecast / Model Expert Framework
    ├── MetaWeight / Context Router
    ├── Portfolio Policy Framework
    ├── Execution / Persistent Paper Accounts
    └── Outcome / Learning / Versioning
```

Do not silently make `MarketState` a mandatory universal input in the walking skeleton. A simple technical strategy must traverse the same permanent engine.

Likely shared contracts to settle in #36 include:

- `SignalProvider` / immutable `SignalArtifact` or `SignalVector`;
- `ForecastDistribution`;
- `StrategySpec`;
- meta/router weight state;
- `PortfolioIntent`;
- paper execution/fill objects;
- `CanonicalOutcome`;
- immutable artifact/version identity.

This should be a short contract correction, not a new assurance program.

## Fixed laboratory remains authoritative

The working workstation and fixed experiment laboratory are already merged to `main`.

`finance_quant.lab` continues to own canonical historical snapshots/outcomes, PIT cuts, scoring, evaluation identity, router timing and simulated-account truth. Candidate components may propose signals, state, retrieval, forecasts, strategy/meta weights and portfolio policies; they do not own the answer key.

Stable fixed-lab flow:

`publish immutable components -> assemble PIT benchmark -> run exact-version arms -> join same canonical outcome -> score -> ExperimentLedger -> prior-resolved-only routing -> isolated paper accounts`

Existing lab correctness semantics, component/evaluation hashes, mutation probes and paper-account invariants remain in force. Do not redesign them inside candidate lanes unless a concrete integration bug requires a centrally coordinated change.

## Existing empirical baseline retained

The workstation remains runnable:

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
Existing real AAPL/SEC workflow produced 1,988 walk-forward predictions:

- price-only directional accuracy: **53.3702%**;
- price + current small SEC-fundamental set: **51.8612%**;
- delta: **-1.5091 percentage points**.

The current tiny SEC structured feature set hurt the baseline. Do not claim KG predictive value from it.

Existing zero-money paper proof remains:

- 2026-08-26 signal persisted;
- 2026-08-27 simulated next-open fill: BUY 305 AAPL @ 310.61209779052734;
- marked NAV about $101,210.21 from $100,000.

That proves signal -> persistent state -> simulated execution -> mark, not profitability.

The current adjusted Yahoo historical lane is not strict raw PIT truth because later corporate actions can retroactively restate adjusted history. #29 should supply raw OHLCV + separately timestamped corporate actions.

## Strategy/meta-engine direction

The important object is not one permanent strategy but a versioned strategy specification combining:

- signal/provider versions + signal weights;
- model/expert versions + model weights;
- horizon/context/regime weighting;
- portfolio policy and risk parameters;
- execution/cost/rebalance assumptions.

Weights may initially be static controls, then evolve through inspectable prior-resolved-only methods such as exponentially weighted experts, rolling optimization, Bayesian/model averaging or contextual routers.

The system must preserve complete trial/version genealogy so AI-generated strategy search does not become automated backtest overfitting.

Do not optimize only directional accuracy or raw return. Evaluate forecast skill and portfolio skill separately, and decompose market/factor exposure from genuine selection/timing value where feasible.

## Portfolio engine direction

#38 owns forecast-to-allocation behavior.

The system must answer:

- where to invest;
- how much to invest;
- how much cash to hold;
- how to diversify by real economic/factor/theme exposure;
- what to buy/sell/hold;
- whether switching is worth transaction costs;
- when to rebalance;
- when to abstain/no-trade;
- how liquidity/correlation/risk constraints change raw forecast conviction.

`PortfolioIntent` is the immutable handoff from forecasts/meta-strategy to paper execution and records target weights, trade deltas, cash target, expected return/risk/cost, turnover, binding constraints and provenance.

Initial competing policy families remain:

1. equal-weight top-K;
2. edge/confidence-weighted top-K with caps;
3. volatility-scaled/risk-budgeted;
4. mean-variance/robust convex allocation with turnover/cost penalties;
5. explicit cash/no-trade threshold.

Each policy should receive identical upstream forecasts/cost assumptions and accumulate its own persistent forward paper history.

## Market State / epistemic provider direction

#37 remains a candidate signal-provider family, not the parent engine.

Useful layered representation:

`SourceArtifact -> Observation -> Claim/Proposition -> Evidence -> bitemporal EpistemicState -> MarketBeliefState -> Derived MarketState -> BenchmarkedKnowledge -> PredictiveKnowledge`

Factual reliability, market attention, economic materiality, exposure/transmission confidence and predictive usefulness remain separate.

`TrendState` should retain level, robust percentile/z-score, multi-horizon velocity, acceleration, noise, trend shape, structural-break probability, novelty, persistence, saturation/decay and cross-source confirmation rather than one generic hype score.

The ontology remains a stable core + versioned domain modules. Graph relations retain valid/knowledge time, provenance, confidence/materiality, and graph expansion stays typed/bounded.

## Raw vs pre-quantized data

The engine must support both custom extraction and already structured/quantized providers.

Potential data/source families include:

- raw market OHLCV/corporate actions;
- SEC filing text/XBRL;
- ALFRED/FRED macro vintages;
- GDELT/open event data;
- GitHub/Hugging Face activity for relevant technical/adoption signals;
- optional commercial RavenPack/LSEG MarketPsych/LSEG MRN/FactSet-Alexandria style feeds;
- social attention sources where licensing/coverage is appropriate.

Vendor scores are optional signal adapters, not hard dependencies. We do not need to recreate every professional extraction system before testing useful strategies.

## Local architecture / OSS direction

Use a modular monolith with process-isolated heavy workers, not microservices by default.

Own unique semantics; reuse commodity machinery:

- fixed `finance_quant.lab` / ExperimentLedger;
- existing paper account substrate;
- retained LEAN execution/backtest integration where useful;
- Parquet/ZSTD + DuckDB + Polars for local historical analytics;
- one retrieval engine initially (OpenSearch or lighter Qdrant where appropriate);
- LightGBM/XGBoost + transparent linear/ranking baselines;
- Qlib only where it materially accelerates research;
- local LLM runtime for extraction/classification where justified;
- RDFLib/pySHACL/OWL/PROV/RO-Crate-style export for #39 after useful lineages exist;
- no Kafka/Kubernetes/distributed lakehouse before actual workload demands them.

## SWE / multi-agent execution

Use typed shared contracts and durable work packets as synchronization boundaries for AI coding agents.

Every work packet should declare issue/dependencies, owned files/modules, typed inputs/outputs, forbidden authority, focused acceptance tests and required product proof/experiment/paper artifact.

Use stronger reasoning/integration agents for temporal semantics, statistical leakage, architecture, hard debugging and adversarial review; parallelize bounded adapters, signal providers, model executors, tests and UX. Agent/model routing should eventually be empirical rather than permanent Sol=Luna role assignment.

There is no direct Luna connector in the current ChatGPT environment; Luna must be launched externally.

## Verification strategy

Tests protect the product; assurance is not the roadmap.

Risk-targeted stack:

- lint/format + strict typing/import rules;
- typed contracts/schema round-trips;
- focused TDD/integration tests;
- property/invariant tests for universal semantics;
- metamorphic tests for PIT/reordering/dedup/retrieval invariance;
- targeted mutation probes for tiny bugs that could create fake alpha/account corruption;
- deterministic replay for experiment identity;
- Lean/SMT only for concrete hard invariants not credibly covered by executable tests;
- historical WFO + forward paper judge investment usefulness.

Correctness gates software merging. Noisy alpha metrics gate research promotion.

## Major adversarial risk

AI coding makes strategy generation cheap and therefore increases the danger of **automated strategy-selection overfitting**.

Do not implement `generate thousands -> choose best historical Sharpe -> declare winner`.

Preserve every attempted strategy/version and the number/search process that produced it. Use strict walk-forward chronology, appropriate untouched evaluation, multiple-testing/backtest-overfitting discipline and prospective paper evidence.

The engine must be allowed to conclude that sophisticated providers have zero useful weight.

## Active durable issues

- #12 — master workstation/product
- #27 — fixed versioned/full-information research lab
- #29 — historical PIT data lanes
- #19 — temporal KG + PIT-safe RAG
- #21 — local model research/training
- #18 — continuous local paper refresh
- #17/#32 — workstation/lineage UX
- #35 — architecture proposal; **must be reconciled with latest adaptive-engine correction**
- #36 — walking skeleton/API contracts/agent work graph; **must generalize beyond mandatory MarketState**
- #37 — Market State/epistemics/trends/exposures signal-provider family
- #38 — portfolio allocation + diversified forward paper
- #39 — reproducible Research Evidence Bundle

## Next exact action

1. Read `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`.
2. Reconcile #35/#36 and this current state so the adaptive multi-strategy engine is clearly the parent concept and MarketState is optional.
3. Freeze the smallest correct signal/strategy/meta/forecast/portfolio contracts and walking skeleton.
4. Prove the skeleton with a simple price/momentum/breakout/volatility vertical slice that does not require KG/news.
5. Resume #29/#37/#19/#21/#38 workers in parallel behind those contracts.
6. Put every executable credible strategy/policy into local forward paper immediately.
7. Surface signal weights, meta weights, forecasts, target allocation, fills, realized outcomes and version evolution in the workstation.
8. Add #39 audit/export only after useful lineages exist.

The initial parallel Luna worker wave is complete. The next bounded research
wave against #29, #19 and #21 is:

1. clean walk-forward/OOS ablation for the new SEC-fundamentals arm;
2. source-native historical clocks for market/news/macro inputs;
3. pinned financial news replay with publication/first-seen clocks;
4. dated supplier/customer/competitor evidence suitable for historical scoring;
5. stronger local model families, contextual routing, and explicit OOS/regime splits.

The scope decision for longer history, broader equities, crypto, FX, and
prediction markets remains open; see `docs/plans/OPEN_SCOPE_QUESTIONS.md`.
## Success criterion

The project succeeds as an investment system if the local adaptive engine can produce reproducible, PIT-correct strategies whose signal/model/policy weighting demonstrates stable incremental usefulness under strict walk-forward research and continues to produce useful cost/risk-adjusted behavior in immutable prospective paper portfolios.

It is not a requirement that MarketState/KG/RAG survive. It is a requirement that the engine objectively learn which components deserve weight.

## Required read order for a fresh session

1. `AGENTS.md`
2. this file
3. `docs/handoffs/SESSION_2026-08-28_ADAPTIVE_QUANT_ENGINE.md`
4. #35
5. #36
6. `docs/handoffs/LATEST.md`
7. #27 + fixed lab contracts/tests
8. relevant candidate issue (#29, #37/#19, #21, #38, #32/#17, #39)
9. `finance_quant/lab/`, `tests/test_lab_*.py`, mutation probes
10. `finance_quant/workstation/` and its product tests
11. older assurance material only when relevant to a concrete product bug
