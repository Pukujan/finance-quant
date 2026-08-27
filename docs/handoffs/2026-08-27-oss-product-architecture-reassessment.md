# Handoff — OSS product architecture reassessment before A2 HITL

Date: 2026-08-27
Branch: `bootstrap/oss-autonomous-trader-replatform`
Active issue: #16
Assurance phase: A2
Authority: trading `NONE`; unattended paper disabled; live capital disabled

## Why this handoff exists

A2 implementation and assurance are effectively complete, including genuine one-shot sealed hidden acceptance for frozen public evaluation SHA `1ecc470cd6e0e23bf1d439f51e4e2c39674f02c4` and candidate artifact SHA-256 `446fdc1a0c87db3a6a2ab4e94fab3d7e9f8fd389cc41676be12c3803b1f2d093`. The remaining formal A2 gate is `HITL_PROMOTION`.

However, before granting that capability, the owner clarified the intended product: a visible local autonomous quant workstation where the user can configure starting paper cash, ingest real historical/ongoing market information under point-in-time semantics, train/evaluate a local trading model, use temporal knowledge/RAG safely, simulate trades, and inspect account/trades/PnL/decisions through a proper frontend.

The current A2 kernel proves the lower trading substrate but does not yet provide that complete product experience. Therefore **HITL is intentionally on hold** while the project performs an OSS architecture bakeoff. Do not interpret the A2 hidden pass as an instruction to enable unattended paper now.

## What finance-quant already has and should not casually discard

### Validated replatform assets

- LEAN commit `185c691b89f28bd68e48d53c02147415134975f0`, selected `ADOPT_WITH_CONSTRAINTS` for the deterministic daily-bar next-eligible-open slice.
- Finance-quant-owned SQLite virtual account with durable cash, positions, orders, fills, cash ledger, and authoritative SessionReceipts.
- `VirtualAccountStore(path, initial_cash=...)`: a new paper-account DB requires explicit starting cash; an existing DB cannot be silently reset by reopening with a different initial cash amount.
- Exact accounting/NAV reconciliation, duplicate/retry/idempotency protection, crash/restart atomicity, two-session continuity, stored-evidence replay, risk non-widening, PIT-safe baseline decisions, read-only operator evidence projection.
- Five-run clean LEAN determinism and five-run multi-session restart/replay determinism.
- Stateful/property, mutation, differential, metamorphic, clean-environment, chaos/fault, hidden acceptance, and sealed-evidence machinery.
- Aggregate A2 hidden evidence is already stored publicly. Seal use `1/1` is consumed; do not rerun it automatically.

### Reusable pre-replatform research/data assets

These are real existing code, but they are **not yet promoted as the active autonomous-trader product path**:

- `finance_quant/pit/model.py`: bitemporal `BitemporalRecord` with `vt` (valid time) and `kt` (knowledge time), namespaces for bars, fundamentals, corporate actions, universe, and macro.
- `finance_quant/pit/store.py`: `MemoryGoldStore` + durable `SQLiteBitemporalStore`; as-of visibility is constrained by `kt <= K`; revisions are append-only and historical states remain queryable.
- `finance_quant/ingest/polygon.py`: Polygon adapter for daily bars and corporate actions, emitting PIT/provenance fields.
- `finance_quant/dsl/qlib.py`: existing Qlib compiler boundary.
- graph/KG design in `docs/spikes/06-fossil-ontology-graph-features.md`: bitemporal graph-edge discipline and PIT-safe graph-feature rules; full graph DB was previously deferred.
- legacy Phase-B fixtures exist, but they are evaluation fixtures, not a serious production training corpus.

## What is NOT yet a finished product capability

- No polished local daemon/service that continuously runs the trader on the user's PC.
- No product-level config screen/CLI for starting balance, account DB path, universe, provider, frequency, and risk limits.
- No active, populated production historical PIT dataset wired into the A2 trader.
- No fully populated temporal knowledge graph.
- No production RAG path with bitemporal/as-of retrieval authority.
- No trained local trading learner in the active capability. A6 was explicitly reserved for this.
- No polished operator/research frontend. `finance_quant/trader/operator.py` is a read-only HTML/JSON evidence renderer, not the intended dashboard.
- No external real broker credentials or live-capital authority.

## OSS scan — verified candidates

### 1. AI4Finance-Foundation/FinRL-Trading (FinRL-X)

Current README describes it as an AI-native modular/full-stack quant platform with:

- unified data acquisition: Yahoo Finance, FMP, WRDS;
- feature/data processing + SQLite cache;
- ML stock selection and DRL allocation examples;
- backtesting with transaction costs;
- Alpaca live/paper multi-account integration, pre-trade risk checks, and real-time P&L;
- one-command `deploy.sh` flows for backtest and paper trading;
- a weight-centric strategy/execution interface intended to preserve deployment consistency.

Important potential value: this could replace a large amount of custom product/runtime orchestration and gives a direct research→backtest→paper path.

Important gaps for finance-quant: no evidence found yet that its data/knowledge layer satisfies our strict bitemporal `vt/kt` contract, sealed assurance, temporal KG/RAG requirements, or our authority/promotion model. Do not simply replace the validated finance-quant core without a conformance bakeoff.

Repo: `AI4Finance-Foundation/FinRL-Trading`

### 2. Open-Papertrade/Open-Papertrade

Current README describes a maintained Django + Next.js full-stack paper-trading application with:

- virtual portfolios, market/limit orders, holdings, transaction history, alerts;
- live quotes via Finnhub with Yahoo fallback;
- TradingView-style charts/indicators;
- historical strategy backtesting;
- AI coaching over user trade history;
- agentic RAG over SEC 10-K/10-Q/8-K filings with hybrid dense/sparse retrieval, reranking, citations, and refusal behavior;
- local LLM support through Ollama and generic OpenAI-compatible local servers (LM Studio, vLLM, llama.cpp);
- full web frontend plus Django admin.

This is the closest verified repo to the **visible product UX** the owner described.

Important gaps: its README does not establish our bitemporal PIT discipline, temporal KG, locally trained quant learner, sealed assurance, deterministic replay guarantees, or finance-quant promotion authority. License is AGPL-3.0, so code reuse/distribution implications must be evaluated before incorporation. It may be more appropriate as a separate service/reference UX than copied code.

Repo: `Open-Papertrade/Open-Papertrade`

### 3. Open-Finance-Lab/AgenticTrading

Current README describes Agentic Trading Lab as an open-source experimental playground/dashboard for LLM-powered trading agents with:

- agent creation/configuration and external-agent API;
- backtests and paper-trading simulations;
- virtual capital/team-of-agents concepts;
- positions/trades/portfolio/reasoning inspection;
- market benchmarks and leaderboards;
- FastAPI backend + frontend + SQLite storage;
- Alpaca/Robinhood broker infrastructure;
- an included FinAgent orchestration framework with memory and DAG planning;
- roadmap toward managed long-running agents and broader data/broker/MCP connectivity.

Critical caveat visible in the repo layout/README: the shipping dashboard's v2 execution backend identifies backtest as live and paper as a stub, so this should not be assumed to provide a finished production paper execution path today. It is still highly relevant for frontend/agent observability/orchestration patterns.

Repo: `Open-Finance-Lab/AgenticTrading`

### 4. microsoft/qlib + microsoft/RD-Agent

Qlib's current README describes an AI-oriented quantitative investment platform covering:

- data processing;
- model training;
- backtesting;
- alpha seeking, risk modeling, portfolio optimization and order execution;
- supervised learning, market dynamics, RL;
- point-in-time database support;
- online serving/automatic model rolling;
- a model/data/research ecosystem.

RD-Agent's current README describes RD-Agent(Q) as a data-centric multi-agent quant R&D framework for automated factor/model co-optimization. It supports automated factor mining/model optimization and can use Qlib as the quant research substrate; it now also has a frontend for run/trace viewing.

This pair is the strongest current candidate for **research/factor/model automation**, and finance-quant already has a Qlib compiler boundary. It should be evaluated before writing A6's learner/research factory from scratch.

Repos: `microsoft/qlib`, `microsoft/RD-Agent`

### 5. Additional candidates already identified for deeper follow-up

- OpenBB: broad financial data/research/workspace ecosystem; candidate data/research surface, not assumed to be execution authority.
- AI4Finance FinGPT: candidate financial-language/RAG components; must be checked for provenance/PIT compatibility before use.
- Existing LEAN: keep as currently validated execution body unless a new bakeoff proves a broader OSS platform can meet or exceed the frozen execution/account/authority contracts.

## Current working hypothesis — not yet a final decision

Do **not** throw away the finance-quant parts that are unusual and already proven: PIT semantics, authority contracts, exact account/replay evidence, sealed acceptance, mutation/chaos gates, promotion controls.

Instead, investigate turning finance-quant into the **policy/PIT/assurance spine around mature OSS components**:

```text
market / filings / macro / fundamentals
            |
            v
 finance-quant PIT/bitemporal truth
            |
    +-------+--------------------+
    |                            |
    v                            v
Qlib/RD-Agent or FinRL-X     SEC/RAG/knowledge layer
research/model stack         (possibly Open-Papertrade /
    |                         FinGPT-derived components)
    +-------------+--------------+
                  v
          proposal / portfolio
                  v
       finance-quant risk/authority
                  v
                LEAN
                  v
       authoritative paper account
                  v
       operator/research frontend
```

Possible frontend approach: adapt patterns or run a separate UI service based on Open Papertrade or Agentic Trading Lab rather than starting from a blank frontend. Any adoption must preserve the rule that UI/model/agent is never account/fill/promotion authority.

## Required next-session task: OSS architecture bakeoff

Do not continue implementation first. Perform an explicit KEEP / REPLACE / ADAPT / DELETE comparison for each layer:

1. **Data acquisition and storage** — finance-quant PIT + Polygon vs Qlib/FinRL-X/OpenBB data systems. Determine how to populate a real reproducible dataset while preserving `vt/kt` semantics and revisions.
2. **Research/features/model training** — Qlib + RD-Agent vs FinRL-X vs custom A6. Evaluate local/offline feasibility, model provenance, walk-forward support, deterministic artifacts, and whether pretrained/hosted LLM dependencies violate the intended local learner policy.
3. **Knowledge/RAG** — Open Papertrade SEC RAG, FinGPT, and existing temporal-KG design. Determine how retrieval can be `AS OF (vt,kt)` and how textual facts/embeddings/models get versioned so future knowledge cannot leak backward.
4. **Paper account/execution** — keep finance-quant SQLite + LEAN vs FinRL-X/Alpaca paper. Be explicit about two different meanings of paper trading: local simulated ledger vs broker-hosted Alpaca paper account. Decide which product should expose and whether both should exist in stages.
5. **Frontend/operator UX** — Open Papertrade vs Agentic Trading Lab vs a thin custom shell. Compare licensing, APIs, code quality, install complexity, Windows/local support, observability, and authority separation.
6. **Local runner/deployment** — define the actual Windows/WSL/Docker user experience: one command/service, config file/UI, data refresh schedule, starting capital, storage locations, stop/kill switch, logs, restart recovery.
7. **Licensing/security/maintenance** — evaluate licenses (especially AGPL for Open Papertrade), active maintenance, issue velocity, dependency/supply-chain surface, credential handling, and ability to pin/fork/adapt safely.

### Required output from the bakeoff

Produce a decision matrix and recommended target architecture containing:

- layer;
- current finance-quant implementation;
- candidate OSS component(s);
- KEEP / REPLACE / ADAPT / DELETE disposition;
- evidence/reasoning;
- integration boundary;
- license/security/maintenance risk;
- conformance tests required before adoption;
- migration cost;
- what custom code becomes unnecessary.

Then update the master roadmap/issues before implementing the chosen pivot. If the recommended architecture materially changes A2/A3/A4/A6 sequencing, amend the durable plan rather than silently continuing the old ladder.

## Governance during reassessment

- **Do not grant A2 HITL promotion yet.**
- Trading authority remains `NONE`.
- Paper trading remains disabled.
- Live capital remains disabled.
- Do not consume another A2 hidden seal use.
- Do not expose hidden cases.
- Do not discard validated finance-quant evidence until replacement components have passed explicit conformance tests.
- The owner wants an actual visible product, not backend-only completion. Treat dashboard/config/data provenance/model/KG visibility as first-class architecture requirements.

## Read first in a fresh session

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. this handoff
4. issue #12 master roadmap
5. issue #16 and issue #17
6. issues #19/#20/#21 for KG and local learner intent
7. the relevant external OSS READMEs/repositories listed above

The next session should continue with research/architecture disposition, not ask for A2 HITL approval first.
