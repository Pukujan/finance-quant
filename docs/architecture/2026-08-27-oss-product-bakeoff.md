# OSS Product Architecture Bakeoff — 2026-08-27

Status: **DECISION**  
Branch at reassessment start: `bootstrap/oss-autonomous-trader-replatform`  
Durable start head: `7d371e3ee9b035e3a1c8c131966d6b17835bbca8`  
Frozen A2 evaluation SHA: `1ecc470cd6e0e23bf1d439f51e4e2c39674f02c4`  
Frozen A2 candidate SHA-256: `446fdc1a0c87db3a6a2ab4e94fab3d7e9f8fd389cc41676be12c3803b1f2d093`  
Pinned LEAN: `185c691b89f28bd68e48d53c02147415134975f0`  

## Executive decision

Adopt a **finance-quant authority spine with replaceable OSS product/research services**, rather than replacing finance-quant with a single trading platform.

The target workstation is:

1. **finance-quant core authority** — bitemporal/PIT truth, local paper-account truth, risk/promotion authority, immutable receipts/replay, provenance contracts, temporal knowledge semantics, and conformance/assurance;
2. **QuantConnect LEAN** — pinned execution/backtest simulator behind the already validated adapter contract;
3. **Qlib** — primary feature/model/research workflow substrate behind finance-quant PIT snapshot and compiler boundaries;
4. **RD-Agent** — isolated research/coding orchestrator for generating research hypotheses/code and invoking Qlib, with no account/broker/promotion authority and no runtime role in trading decisions;
5. **Open Papertrade** — frontend/product-experience donor, operated as a separate AGPL service/fork and rewired to finance-quant APIs; its trading ledger and unqualified RAG authority are not adopted;
6. **OpenBB Platform** — optional separate AGPL data-acquisition service for fundamentals/macro/text/provider breadth, materialized into finance-quant PIT storage before research or decision use;
7. **Polygon** — retained direct market/corporate-action adapter and provenance path;
8. **MLflow/Qlib Recorder** — experiment visualization/artifact mirror, while finance-quant's append-only experiment ledger remains semantic truth;
9. **FinGPT** — optional text-model/sentiment research dependency only; never temporal truth and never a production decision-time dependency without explicit artifact/provenance conformance;
10. **FinRL-X** — benchmark/reference/optional portfolio-proposal donor, not the workstation substrate or paper-account authority;
11. **AgenticTrading** — protocol/decision-log/reference donor only unless its custom license is separately approved; its current paper-agent path is not an implemented local-paper substrate.

No upstream component receives trading or promotion authority by being able to emit orders, weights, forecasts, retrieval results, or UI commands.

## Why no single platform wins

### FinRL-X majority-substrate hypothesis — rejected

FinRL-X is real, current code rather than only a paper: it has data adapters, strategies, a `bt`-based backtest engine, portfolio/risk utilities, dashboards, Docker assets, and an Alpaca trading manager. However:

- its default Alpaca account base URL is `https://paper-api.alpaca.markets`, so its paper path is **broker-hosted Alpaca paper**, not finance-quant's authoritative local simulated ledger;
- its backtest engine uses its own `bt`-based capital/cost/weight semantics rather than the already frozen LEAN conformance contract;
- its initial FinRL-X public release is recent (v1.0.0, 2026-03-25), and current issues include missing `apply_risk_limits`, missing `create_strategy`, dependency incompatibility and a vulnerability report;
- replacing the A2 execution/account path with it would invalidate rather than reuse the five-run LEAN determinism, restart/replay, mutation/differential/metamorphic/chaos, and hidden-acceptance evidence.

Decision: **ADAPT/REFERENCE_ONLY**, not majority substrate.

Evidence:
- https://github.com/AI4Finance-Foundation/FinRL-Trading/releases
- https://github.com/AI4Finance-Foundation/FinRL-Trading/issues
- `src/backtest/backtest_engine.py`
- `src/trading/alpaca_manager.py`

### Open Papertrade product-shell hypothesis — accepted with a hard authority split

Open Papertrade is the strongest product/UX donor in the evaluated set. Current code includes a Next.js frontend, Django API, configurable starting buying power, portfolio/trades/history/watchlists, charting, backtest builder/results, coaching, SEC-filings research, hybrid dense/sparse retrieval, reranking, citations, and local/Ollama-compatible model support.

It cannot be adopted as the authoritative backend unchanged:

- `ExecuteTradeView` accepts a client-supplied `price`, then mutates buying power/holdings and writes the trade;
- the RAG data model has filing date and ingest timestamps but no bitemporal revision/supersession authority;
- retrieval filters ticker/form/section/fiscal-year but has no mandatory decision-time `knowledge_cut`;
- it is AGPL-3.0, while finance-quant is currently proprietary, so code-copying into the core would create avoidable licensing coupling.

Decision: **ADAPT** the frontend and selected retrieval presentation/evaluation mechanics as a separate service/fork. **DELETE/DO NOT ADOPT** its authoritative trading-ledger path. finance-quant remains the only local-paper account authority.

Evidence:
- https://github.com/Open-Papertrade/Open-Papertrade
- `backend/users/models.py`
- `backend/users/views.py`
- `backend/filings/models.py`
- `backend/filings/services/retrieval.py`

### Qlib + RD-Agent custom-A6 replacement hypothesis — accepted

Qlib already supplies mature feature/model workflows, task management, training, online-model management, backtest/research components, and an MLflow-backed recorder. RD-Agent is explicitly integrated around automated R&D and supports isolated Docker execution for model/quant coding. Current upstream activity includes a 2026-07 PR specifically titled `fix(qlib): isolate holdout evaluation from iterative research feedback`.

The planned custom A6 research/model factory should therefore **not** duplicate generic experiment search, model training orchestration, task management, or MLflow plumbing.

The non-negotiable finance-quant boundary is:

`finance-quant PIT snapshot + feature IR -> Qlib dataset/task -> RD-Agent/Qlib research sandbox -> frozen candidate artifact + full provenance -> finance-quant evaluation/assurance -> observe-only output -> later explicit promotion`

RD-Agent may use an LLM to propose research/code, but the deployed trading artifact must be frozen, reproducible, trained/evaluated on declared local data, and must not depend on a remote LLM or unrecorded hidden knowledge at trading runtime. Old A6 wording that prohibited useful research-agent assistance is superseded by this artifact/runtime boundary; promotion requirements are not weakened.

Decision: **REPLACE** planned custom research/model orchestration with **ADAPT Qlib + RD-Agent**; **KEEP** finance-quant PIT/provenance/evaluation/promotion authority.

Evidence:
- https://github.com/microsoft/qlib
- https://github.com/microsoft/qlib/blob/main/qlib/workflow/online/manager.py
- https://github.com/microsoft/qlib/blob/main/docs/component/recorder.rst
- https://github.com/microsoft/RD-Agent
- https://github.com/microsoft/RD-Agent/blob/main/docs/installation_and_configuration.rst

### OpenBB / FinGPT / Open Papertrade RAG PIT-safety hypothesis — only through a finance-quant temporal gateway

None of the inspected RAG/data stacks is a sufficient bitemporal authority as shipped.

- OpenBB standardizes raw provider access; it does not make every provider response historically first-knowable or revision-correct.
- FinGPT's current multisource RAG flow retrieves Google/news context into CSVs and supports pretrained/adapter LLMs; that is useful research tooling, not a decision-time temporal ledger.
- Open Papertrade has strong retrieval mechanics but no mandatory `knowledge_cut` or supersession model.

They can be made safe only by **materializing source data/documents into finance-quant first**, with first-known time and revision lineage, then filtering eligible records/chunks before vector/BM25/rerank/generation. A current-document vector store must never be queried directly by a historical decision path.

Decision: **KEEP/EXTEND** finance-quant as temporal knowledge authority; **ADAPT** external acquisition, embeddings, rerankers and UX behind it.

## Trading-mode taxonomy

These modes are separate products/contracts and must never share an ambiguous `paper=true` flag.

| Mode | Authoritative account | Data clock | May mutate local paper account? | Credentials | Current authority |
|---|---|---|---|---|---|
| `BACKTEST` | isolated historical simulator/run artifact | historical/replay | **No** | none required | allowed only as research/evaluation |
| `LOCAL_SIMULATED_PAPER` | finance-quant `VirtualAccountStore` SQLite ledger | ongoing real/replayed market clock | **Yes, only after explicit paper authority** | no broker credentials | **disabled; authority NONE** |
| `BROKER_HOSTED_PAPER` | external broker paper ledger (e.g. Alpaca) | broker/live market clock | local state is mirror/reconciliation only | broker API credentials required | **not authorized/not implemented** |
| `LIVE` | external broker live account | live | only through future reconciliation policy | live broker credentials | **disabled; no live authority** |

A backtest may not spend paper cash. A hosted paper account may not silently become the local ledger. A local simulated paper session may not require or expose broker credentials. Live execution remains a separate owner-authorized capability.

---

# Layer-by-layer bakeoff

## 1. Market / fundamental / macro / text data acquisition

**Current finance-quant:** Polygon adapter for bars/corporate actions with injectable transport, pagination/rate-limit behavior, source/revision/ingest receipt and bitemporal record mapping.

**Candidates:** OpenBB Platform/providers; Polygon direct; FinGPT/FinNLP text collectors; Open Papertrade Yahoo/Finnhub/EDGAR adapters; FinRL-X data package.

**Decision:** **KEEP Polygon; ADAPT OpenBB; ADAPT selected text/EDGAR collectors; DELETE duplicate provider-specific plumbing when OpenBB is adequate.**

**Evidence/maturity/activity/license:**
- OpenBB is a large, active Python project (updated 2026-08-27; pushed 2026-07-30 in the checked repository metadata), with provider plugins for market, fundamentals, economics and alternatives. Platform/core/provider packages inspected are AGPL-family; provider terms also apply. https://github.com/OpenBB-finance/OpenBB
- OpenBB's provider registry explicitly enumerates provider credentials and capabilities. `assets/extensions/provider.json`.
- Open Papertrade is young (created 2026-02; pushed 2026-07) and AGPL-3.0; useful adapters exist but are coupled to its product backend.
- FinGPT is MIT and active, but its data/RAG paths are research-centric and may call external search/LLM services.

**Windows/local usability:** OpenBB can run as Python/REST locally; default recommendation is a Docker service under WSL2. Polygon remains native Python. Text collectors run in a research/data worker, not core.

**Integration boundary:** provider response -> canonical raw receipt -> finance-quant normalizer -> bitemporal append -> immutable snapshot pin. Research/strategy code never calls OpenBB/Polygon/EDGAR directly at decision time.

**PIT/lookahead:** provider timestamps are not automatically first-known timestamps. Each adapter must derive or conservatively assign `kt` from an auditable release/acceptance/fetch fact. For SEC documents use filing acceptance/publication time, not fiscal period end. Revisions are append-only.

**Provenance:** source/provider endpoint, request parameters with secrets redacted, fetched/accepted time, raw content hash, parser version, normalization version, ingest run, revision/supersession, license/entitlement metadata.

**Authority/security:** provider credentials live only in acquisition service env/secret mounts; never in UI, RD-Agent, model artifact or SessionReceipt. Data services have no account write path.

**Migration cost:** medium. OpenBB broadens coverage but requires canonical mapping and provider-by-provider PIT tests.

**Required conformance tests:** canned-provider differential fixtures; pagination/retry; secret redaction; timestamp/first-known boundary tests; revision/supersession; future-release poison; snapshot determinism; provider outage/partial response; entitlement/source-manifest checks.

**Custom code eliminated:** future bespoke wrappers for every fundamentals/macro provider; duplicated HTTP/auth/routing for providers already supported by OpenBB.

## 2. PIT / bitemporal data authority

**Current:** `BitemporalRecord`, `MemoryGoldStore`, `SQLiteBitemporalStore`, `(vt, kt)` queries, append-only corrections, revision/supersession, snapshot pins.

**Candidates:** Qlib PIT data support; OpenBB storage/output; Open Papertrade Django models; FinRL-X datasets; generic databases.

**Decision:** **KEEP. No evaluated OSS project replaces this authority.** Qlib remains downstream of the snapshot/compiler boundary.

**Evidence:** finance-quant's store selects the latest revision visible under the knowledge-time bound and its in-memory store serves as a correctness oracle. Qlib has PIT-related record types, but finance-quant already has broader explicit revision/source/ingest semantics and assurance tied to them.

**Maturity/license:** local code is project-specific and already tested; underlying SQLite is mature/public-domain. Qlib is MIT but is a consumer, not authority.

**Windows/local:** excellent; SQLite is the simplest local workstation default.

**Integration boundary:** all external data/knowledge enters this authority before it can become a historical feature, label, KG edge, retrieval chunk, model input or decision input.

**PIT/lookahead:** this layer owns the no-lookahead invariant. `event/valid time <= decision time` is insufficient unless `known_at <= decision time` also holds.

**Provenance:** immutable snapshot hash must flow into Qlib run specs, model manifests, retrieval receipts and SessionReceipts.

**Authority/security:** read-only snapshots to downstream workers; only controlled ingestion owns append privilege.

**Migration cost:** none/low; extend rather than replace.

**Conformance tests:** existing memory-vs-SQLite differential; poisoned future revision; old-knowledge reconstruction; same-vt later-kt revision; snapshot hash determinism; crash/reopen; malformed temporal interval; namespace-specific first-known rules.

**Custom code eliminated:** none. This is differentiating authority code.

## 3. Research / features / model training

**Current:** finance-quant feature IR/checker, Qlib compiler boundary, workflow/experiment primitives, planned custom A6 learner/factory.

**Candidates:** Qlib, RD-Agent, FinRL-X, FinGPT, ordinary sklearn/LightGBM/PyTorch through Qlib.

**Decision:** **KEEP feature/PIT compiler authority; REPLACE generic custom factory/orchestration with Qlib + RD-Agent; ADAPT FinRL-X/FinGPT only as benchmarks or model candidates.**

**Maturity/activity/license:** Qlib is MIT, mature and very widely used; current repo remains active. RD-Agent is MIT, active, and tightly aligned with Qlib. FinRL-X is Apache-2.0 but substantially newer. FinGPT is MIT and active but pretrained-model-centric.

**Windows/local:** Qlib is Python-local. RD-Agent currently documents Linux-only support and recommends Docker; WSL2/Docker is therefore the supported Windows route. Local GPU is optional by model choice.

**Integration boundary:** RD-Agent cannot query production stores directly. It receives a mounted immutable experiment bundle containing dataset snapshot pin, approved feature IR, split policy, cost model, code base, resource limits and output directory. Qlib trains/evaluates. Outputs are copied into a quarantine/artifact store with hashes before finance-quant validates them.

**PIT/lookahead:** Qlib datasets must be produced from a finance-quant knowledge cut/snapshot. Any Qlib-native data source used outside that boundary is research-only and cannot support a promotion claim.

**Provenance:** code SHA, environment lock/container digest, dataset manifest/snapshot hash, feature IR hash, model config, seeds, split policy, costs, RD-Agent prompt/model/provider identifiers if an agent generated code, candidate artifact hash, training logs and parent run.

**Authority/security:** RD-Agent gets no broker credentials, no account DB write permission, no holdout contents, and no promotion endpoint. Remote LLM credentials, if used for research, are isolated to the research worker and never required by deployed trading runtime.

**Migration cost:** medium, but lower than building a factory. The main work is a narrow finance-quant Qlib/RD-Agent job protocol and artifact manifest.

**Conformance tests:** deterministic dataset export; feature compiler differential; train/test time-bound poison; split leakage; repeated seeds; resource/network sandbox tests; artifact hash/reload; agent cannot access account/holdout/credentials; parent-vs-candidate evaluation; runtime dependency audit proving promoted model does not need research LLM.

**Custom code eliminated:** generic trial loop, model/task scheduler, MLflow-oriented training plumbing, generic model search/coding agent, much of the originally planned A6 factory.

## 4. Temporal knowledge graph

**Current:** explicit bitemporal graph design plus `GraphEdge(valid_from, valid_to, known_at)` and filter-before-projection rule.

**Candidates:** no evaluated trading platform has equivalent temporal authority. Qlib/FinRL-X can consume graph-derived features; generic graph stores could later be projections.

**Decision:** **KEEP semantic authority. ADAPT a graph database only if scale proves SQLite/columnar projections insufficient.**

**Maturity:** current graph code is intentionally small but its temporal rule matches the project invariant. Avoid introducing a graph DB merely for visualization.

**Windows/local:** SQLite/Parquet/NetworkX-style derived projections are simple. A graph service would add operational cost and is deferred.

**Integration boundary:** bitemporal edge records are authoritative in finance-quant; graph indexes/projections are rebuildable caches keyed by snapshot/knowledge cut.

**PIT/lookahead:** filter eligible edges by both validity and first-known time **before** neighborhood expansion, aggregation, centrality, embedding or RAG retrieval.

**Provenance:** edge source/content hash, extraction rule/model version, valid interval, first-known time, revision/supersession, projection build hash.

**Authority/security:** KG is observe-only initially. Any future VETO/reweight/propose capability remains behind issue #20 and separate HITL gates.

**Migration cost:** low now; medium only if adding a graph database.

**Conformance tests:** poisoned future edge; valid-earlier/known-later; superseded edge; differential naive oracle; graph-build determinism; metamorphic node-order invariance; cache rebuild equivalence; no graph output changes prior decisions in observe-only mode.

**Custom code eliminated:** bespoke scalable graph storage/indexing if a later OSS graph engine is adopted; temporal semantics remain custom.

## 5. RAG / retrieval

**Current:** planned PIT-safe retrieval and temporal KG; no production RAG authority yet.

**Candidates:** Open Papertrade filings RAG; FinGPT RAG/models; local embedding/reranker libraries; OpenBB data sources.

**Decision:** **ADAPT retrieval algorithms/UI; build/KEEP a thin finance-quant bitemporal knowledge gateway as authority.**

**Required authoritative record:** document/chunk identity, source URI, content hash, effective/valid interval, `known_at`, revision, `supersedes/superseded_by`, ingest run, parser version/hash, chunker version/hash, embedding model/version/hash, embedding input hash, source/license metadata.

**Query receipt:** query text/hash, decision time/knowledge cut, eligible snapshot hash, filters, dense/sparse/rerank model/config hashes, returned chunk IDs/content hashes/scores and generator/model hash if generation occurs.

**PIT algorithm:** `temporal eligibility -> candidate corpus -> dense/sparse retrieval -> fusion/rerank -> generation`. Never `retrieve current corpus -> filter citations afterward`.

**Windows/local:** Open Papertrade supports local/Ollama-compatible providers; vector/BM25 retrieval can be local. Start with SQLite/FTS or an in-process vector index over the temporally eligible snapshot; optimize only after profiling.

**Authority/security:** retrieval is evidence, not trading authority. LLM output never directly mutates account/risk/promotion state. Historical research may not call web search at decision time.

**Migration cost:** medium. The retrieval math is reusable; temporal eligibility/provenance must be inserted underneath it.

**Conformance tests:** future-document poison; amendment/revision; same document known later; embedding rebuild equivalence; BM25/dense temporal corpus equality; ranking only over eligible IDs; citation/content-hash match; refusal on empty eligible corpus; generator cannot introduce uncited decision facts; network denied during historical replay.

**Custom code eliminated:** custom hybrid-search/reranker UI and generic agentic RAG loop can be borrowed/adapted from Open Papertrade; temporal authority remains custom.

## 6. Portfolio / risk

**Current:** finance-quant portfolio intent/risk gate and invariant that risk may approve exact requested exposure or reduce/veto, never widen it.

**Candidates:** FinRL-X portfolio/risk utilities, Qlib portfolio strategies, LEAN portfolio models.

**Decision:** **KEEP finance-quant risk/promotion authority; ADAPT OSS portfolio optimizers as proposal producers.**

**Integration boundary:** model/optimizer outputs target weights/intents -> canonical finance-quant intent -> risk/policy gate -> execution adapter. Optimizers never receive an account write handle.

**PIT:** covariance/returns/risk inputs must be snapshot-bound; no optimizer may fetch current data independently during historical/replay evaluation.

**Provenance:** optimizer/library version, inputs/snapshot, constraints, objective, solver/version/seed, pre-risk proposal and post-risk decision.

**Authority/security:** risk is a capability boundary. External code can propose; only finance-quant can accept/veto and later authorize execution.

**Migration cost:** low-medium.

**Conformance tests:** no-widen property; notional/leverage/position limits; invalid/NaN proposal fail-closed; solver nondeterminism bounds; stressed costs/liquidity; optimizer attempts forbidden field; differential pure reference kernel.

**Custom code eliminated:** advanced portfolio construction algorithms already present in Qlib/FinRL-X may be avoided; policy kernel remains custom.

## 7. Execution simulator

**Current:** validated, pinned LEAN execution adapter plus independent reference simulator and A1/A2 conformance evidence.

**Candidates:** LEAN, FinRL-X `bt` engine, AgenticTrading backtester, Open Papertrade backtester.

**Decision:** **KEEP LEAN.** Other simulators are research/reference only unless they independently pass the execution contract.

**Maturity/license:** LEAN is mature and Apache-2.0 with active development. finance-quant has already validated the exact pinned commit for deterministic daily-bar next-eligible-open semantics.

**Windows/local:** strong Docker/.NET/Windows support; already proven in this repo.

**Integration boundary:** canonical intents/events in; canonical orders/fills/fees/terminal state out. LEAN is not account/promotion authority; authoritative fill effects are committed by finance-quant's local ledger transaction.

**PIT:** simulator receives only time-eligible market/corporate-action events from the replay/PIT boundary.

**Provenance:** LEAN commit/container digest/config, input manifest/hash, adapter version, output receipt/hash.

**Authority/security:** no broker credentials in local simulation. Live brokerage modules remain unused.

**Migration cost:** zero. Replacing is high because evidence must be rerun under explicit conformance and a new hidden policy, not by assumption.

**Conformance tests:** preserve existing A1/A2 unit/stateful/differential/metamorphic/determinism/clean-env/chaos/mutation tests; future candidate replacements must pass equivalent gates before evidence transfers.

**Custom code eliminated:** no custom matching engine beyond tiny independent oracle.

## 8. Local paper account versus broker-hosted paper account

**Current:** `VirtualAccountStore` SQLite ledger with configurable creation cash, persistence, orders/fills/cash ledger, idempotent duplicate handling, exact NAV, restart/replay and atomic SessionReceipt commit.

**Candidates:** Open Papertrade ledger; FinRL-X Alpaca account; AgenticTrading Alpaca view; LEAN brokerage/account abstractions.

**Decision:** **KEEP local ledger. REJECT Open Papertrade ledger as authority. ADAPT Alpaca only as a future distinct broker-hosted-paper service.**

**Key product behavior:** starting capital is configurable only when creating a local account. Reopening an account with a conflicting `initial_cash` is an error; this prevents accidental portfolio reset.

**Broker-hosted paper design:** broker ledger is authoritative externally; finance-quant stores mirrored/reconciled events and must display reconciliation status. Broker-hosted paper uses separate account IDs, credentials and receipts. It may never masquerade as `LOCAL_SIMULATED_PAPER`.

**PIT:** local simulated fill prices come from validated execution inputs; a browser request cannot declare the fill price.

**Provenance:** account ID/mode, initial-capital receipt, order/intent/fill IDs, source event, execution engine, fees, marks, session chain.

**Authority/security:** local paper uses no brokerage credential. Hosted paper credentials live in a broker adapter with least privilege. Live credentials are absent until a future owner-authorized capability.

**Migration cost:** low for UI exposure; medium-high for future broker reconciliation.

**Conformance tests:** existing account state machine; configurable initial cash/no reset; duplicate/conflicting fill; crash between execution/account/receipt boundaries; hosted-vs-local namespace separation; credential-negative tests; reconciliation drift alarms.

**Custom code eliminated:** none in local authority. Future broker SDK HTTP plumbing can be upstream-provided.

## 9. Frontend / operator experience

**Current:** roadmap-only custom shell; no proper frontend implementation.

**Candidates:** Open Papertrade Next.js frontend; AgenticTrading dashboard; FinRL-X Streamlit/dashboard; MLflow/Qlib UI for experiments.

**Decision:** **REPLACE the planned from-scratch general product shell with an ADAPTED Open Papertrade frontend service/fork.** Keep MLflow as a linked/embedded experiment view where useful. AgenticTrading supplies interaction/decision-log ideas only.

**Why:** Open Papertrade is closest to the desired visible workstation: portfolio/account/trade/history, charts, backtest UX, research/RAG, local model-provider configuration and Windows-oriented local setup.

**License:** AGPL-3.0. Keep the derivative frontend in a clearly separate service/repository/package with its source obligations satisfied. Do not copy its backend ledger into proprietary finance-quant core.

**Integration boundary:** typed finance-quant API/events are the only source for account/trades/fills/PnL/decision receipts, project authority, PIT/RAG evidence and approved command requests. UI state is a cache/view, never truth.

**PIT:** historical views include explicit `as_of/knowledge_cut/snapshot` badges. RAG/backtest requests carry a cut; frontend cannot omit it for historical mode.

**Provenance:** every decision/account/research view exposes source run/session/snapshot/artifact hashes.

**Authority/security:** no DB credentials in browser; no direct broker key storage; CSRF/auth only if multiuser mode is retained. For the local workstation, delete social/copy-trading/email-verification/gamification surfaces unless later desired.

**Migration cost:** medium; mainly API replacement and feature pruning, much less than building charts/workflows from scratch.

**Conformance tests:** OpenAPI/client schema; read-model parity with authoritative SQLite; browser E2E; forbidden direct price/fill mutation; authority-negative endpoint tests; stale snapshot indication; restart reconnect; no secrets in frontend bundle/logs.

**Custom code eliminated:** most bespoke dashboard/navigation/charting/backtest/RAG/account UI; social/copy modules are deleted rather than integrated.

## 10. Local runner / deployment

**Current:** Python project plus LEAN container/workflows; product runner not assembled.

**Candidates:** Docker Compose patterns from FinRL-X/Open Papertrade; RD-Agent Docker execution; native Python/WSL; OpenBB REST; Ollama.

**Decision:** **ADAPT Docker Compose as the default local workstation, with PowerShell entrypoint for Windows and WSL2/Docker as the supported heavy-workload path.**

**Default services:** `finance-quant-core`, `workstation-ui`, `lean-runner`, `research-worker` (Qlib + RD-Agent), optional `openbb-data`, optional `mlflow`, optional `ollama`. SQLite/Parquet volumes are local and bind-mounted with explicit ownership.

**Integration:** services communicate over localhost/private Compose network with narrow APIs; authoritative SQLite files are not concurrently mounted read-write into arbitrary services.

**PIT/provenance:** image digests and env-lock hashes become run provenance.

**Security:** secret mounts/env are service-specific; UI receives none; RD-Agent receives research-model keys only when explicitly configured; LEAN local simulator receives no broker credentials.

**Migration cost:** medium.

**Conformance tests:** clean WSL2/Docker bring-up; no-secret baseline; volume persistence; stop/restart; service unavailability; schema migration; port collision/config diagnostics; Windows path handling; deterministic demo fixture.

**Custom code eliminated:** custom process supervisor, custom model-server bootstrap and ad-hoc environment instructions.

## 11. Experiment / model observability

**Current:** append-only `ExperimentLedger` with reproducibility-complete `RunSpec`; MLflow adapter boundary planned.

**Candidates:** Qlib Recorder/MLflow; RD-Agent logs; AgenticTrading decision logs; Open Papertrade report views.

**Decision:** **KEEP finance-quant ledger as semantic/audit truth; ADAPT Qlib Recorder + MLflow as visualization/artifact mirror.**

**Evidence:** Qlib has an explicit `QlibRecorder` abstraction and concrete `MLflowExpManager`/`MLflowRecorder`, so finance-quant does not need to recreate experiment tracking UI/storage.

**Integration boundary:** begin/finalize authoritative run in finance-quant ledger; mirror parameters/metrics/artifacts to MLflow after/beside commit. MLflow deletion/edit must not erase finance-quant evidence.

**PIT/provenance:** dataset snapshot, feature IR, code/env, split/cost, seed, agent origin, parent run and artifact hash are mandatory before a run can support promotion.

**Authority/security:** MLflow/RD-Agent can display and generate artifacts but cannot mark a model promoted. Promotion receipts remain finance-quant authority.

**Migration cost:** low-medium.

**Conformance tests:** ledger-to-MLflow mirror idempotency; missing provenance fails; MLflow outage does not corrupt ledger; artifact hash mismatch; restore UI from ledger/artifacts; no promotion endpoint in observability service.

**Custom code eliminated:** generic experiment dashboard, artifact-browser implementation, most metrics plotting.

## 12. Security / credential boundaries

**Current:** capability/promotion authority framework; A2 explicitly forbids brokerage credentials and keeps frontend operator-only.

**Candidates:** upstream auth/secret handling is supportive only; no candidate replaces policy.

**Decision:** **KEEP and strengthen finance-quant authority. Isolate credentials by service.**

**Boundary matrix:**
- core authority: local DB/PIT write credentials; no broker or remote-LLM key required;
- UI: no raw service/database/broker secrets;
- OpenBB data service: only data-provider credentials it needs;
- research worker: optional LLM/model registry keys, read-only immutable dataset mounts, no account DB write, no broker credentials, no hidden holdout;
- LEAN local runner: no broker credentials;
- future broker-paper adapter: paper-only broker credentials, no live endpoint capability unless separately promoted;
- live adapter: does not exist in current authorized deployment.

**PIT/provenance:** secret values are never hashed into public receipts; credential identity/scope may be represented by non-secret key IDs/config hashes.

**Migration cost:** medium because Compose/service capabilities must be explicit.

**Conformance tests:** secret scanning; environment allowlist; file-permission tests; network egress policy for historical/research runs; attempted account access from RD-Agent/OpenBB/UI fails; attempted broker path in local mode fails; frontend bundle/log redaction; future paper credential cannot target live base URL.

**Custom code eliminated:** duplicated auth where single-user localhost mode does not need it. Security-critical authority checks remain custom.

## 13. Licensing / maintenance

**Current finance-quant:** `pyproject.toml` declares `Proprietary`.

**Candidate licenses/maintenance posture verified 2026-08-27:**

| Project | License posture | Activity/maturity signal | Role |
|---|---|---|---|
| QuantConnect LEAN | Apache-2.0 | mature, active; already pinned/validated here | KEEP execution dependency/service |
| microsoft/qlib | MIT | mature, very large adoption; active 2026 | ADAPT dependency |
| microsoft/RD-Agent | MIT | active; Docker-centric; Linux-only documented | ADAPT isolated service/dependency |
| OpenBB | Platform/core/provider code inspected is AGPL-family; provider terms vary | large/active | ADAPT separate service |
| Open Papertrade | AGPL-3.0 | young but substantial full-stack implementation | ADAPT separate frontend fork/service |
| FinRL-X / FinRL-Trading | Apache-2.0 | active but new v1.0 and current rough-edge issues | REFERENCE/optional adapter |
| FinGPT | MIT | active, pretrained/research oriented | optional research dependency |
| AgenticTrading | custom OpenMDW-1.0 (`NOASSERTION` in GitHub metadata) | highly active but young; paper-agent execution currently disabled | reference/protocol donor only pending license review |

**Decision:** permissive dependencies may be imported/pinned normally when boundaries fit. AGPL components are separate network/process services or separate-source frontend forks with their license obligations satisfied. AgenticTrading code is not copied into core without explicit license review. Provider/data entitlements are recorded per ingest source and are not implied by software license.

**Windows/local:** the main compatibility constraint is RD-Agent Linux-only support, handled by WSL2/Docker. Qlib/OpenBB/Python and Open Papertrade Node/Django are otherwise locally operable.

**Maintenance policy:** integration PRs pin an upstream tag/commit/container digest; upgrades run layer-specific conformance. No `latest` tag for execution/research authority dependencies. Security update exceptions may be fast-tracked but still require minimum conformance.

**Migration cost:** low now if service boundaries are established before code import.

**Conformance tests:** SPDX/license manifest; third-party notice generation; dependency vulnerability scan; upstream-pin drift detector; provider-terms metadata; clean build from lockfiles; AGPL service source provenance.

**Custom code eliminated:** broad commodity features are delegated without converting the core into a fork-maintenance burden.

---

# Target architecture

```text
                           +-----------------------------+
                           | Open Papertrade-derived UI  |
                           | operator/research only      |
                           +--------------+--------------+
                                          |
                                  typed local API/events
                                          |
+----------------+       +----------------v------------------+       +--------------------+
| OpenBB service | ----> |          finance-quant core       | <---- | Polygon / EDGAR    |
| provider creds | raw   | PIT/bitemporal + knowledge cuts   | raw   | direct adapters    |
+----------------+       | risk/promotion + account/receipts |       +--------------------+
                         +--------+-------------+-------------+
                                  |             |
                   immutable PIT  |             | canonical execution bundle
                   snapshot       |             v
                                  |      +--------------------+
                                  |      | pinned LEAN runner |
                                  |      | no broker creds    |
                                  |      +---------+----------+
                                  |                |
                                  |        orders/fills receipt
                                  |                |
                                  |       authoritative commit
                                  v
                      +-----------+------------+
                      | research worker         |
                      | Qlib + RD-Agent         |
                      | optional FinGPT/models  |
                      | no account/holdout auth |
                      +-----------+-------------+
                                  |
                        frozen artifacts/metrics
                                  v
                      +-----------+-------------+
                      | finance-quant experiment|
                      | ledger + assurance      |
                      +-----------+-------------+
                                  |
                            mirror/read-only
                                  v
                             MLflow UI
```

### Service versus dependency/fork decisions

- **finance-quant core:** repository/core package; retained.
- **LEAN:** separate pinned runner/container/process; no fork unless an explicit conformance blocker appears.
- **Qlib:** pinned Python dependency inside the research worker; existing finance-quant compiler remains the boundary.
- **RD-Agent:** separate isolated research-worker process/container; initially upstream dependency, not fork.
- **Open Papertrade:** separate AGPL frontend fork/service. Reuse the frontend and selected RAG UX; replace authoritative backend calls with finance-quant APIs. Do not merge its ledger into core.
- **OpenBB:** separate AGPL REST/data service, optional in minimal install. Materialize outputs into finance-quant.
- **MLflow:** separate local observability service; non-authoritative.
- **Ollama/other local model runner:** optional separate service; non-authoritative.
- **FinGPT:** optional pinned library/model in research worker; never default runtime dependency.
- **FinRL-X:** no default service. Keep as benchmark/reference and potentially import individual portfolio/research components after conformance.
- **AgenticTrading:** no default dependency. Use design/protocol ideas and external-agent API concepts; do not copy code pending license review.

# Code retained, replaced, and deleted

## Retain

- `finance_quant/pit/*` bitemporal model/store and snapshot pins;
- Polygon canonical adapter and ingest provenance contract;
- feature IR/checker and Qlib compiler boundary;
- temporal KG valid/known-time semantics;
- `VirtualAccountStore`, SessionReceipt, replay/session machinery;
- pinned LEAN adapter and independent reference simulator;
- risk/no-widen and capability/promotion framework;
- experiment `RunSpec`/append-only ledger as audit truth;
- property catalog, hidden/sealed acceptance boundary, mutation/differential/metamorphic/determinism/chaos gates;
- project-state/handoff machinery.

## Replace / stop building

- from-scratch general model/research factory -> Qlib + RD-Agent;
- from-scratch general experiment UI/storage -> Qlib Recorder/MLflow mirror;
- from-scratch general product shell/charts/account/research UX -> Open Papertrade-derived frontend service;
- bespoke wrappers for every fundamental/macro provider -> OpenBB where suitable;
- generic hybrid-RAG/reranker mechanics -> adapted Open Papertrade/standard OSS components, but only after finance-quant temporal eligibility.

## Explicitly do not adopt

- Open Papertrade request-supplied-price trade authority;
- Open Papertrade current-document RAG as historical temporal truth;
- FinRL-X Alpaca account as the local paper ledger;
- FinRL-X `bt` backtester as a replacement for frozen LEAN without a new conformance campaign;
- AgenticTrading's current paper path as a local autonomous paper implementation;
- direct web/current-document retrieval in historical decision paths;
- MLflow, Qlib, RD-Agent, UI, KG or LLM as promotion/account authority.

# Revised sequencing

The numeric assurance IDs remain stable to preserve contracts/evidence, but they are now **assurance profiles, not a strict implementation chronology**. Observe-only product/research capabilities may be built before unattended-paper promotion because they do not widen trading authority.

1. **A1 — complete.** LEAN selected/validated; preserve evidence.
2. **A2 public implementation/assurance — complete and frozen.** Hidden seal consumed/passed. **Do not rerun. Do not request HITL yet.** Trading authority remains NONE.
3. **W1 — local workstation substrate, authority NONE.** Establish explicit runtime modes, typed core API/read models, Open Papertrade-derived UI boundary, local runner/service manifest, data-service boundary, PIT-safe knowledge/RAG record contract, and account/decision visibility. No unattended paper.
4. **A4 observation work may begin after/inside W1** rather than waiting for A3 unattended-paper reliability. Temporal KG/RAG is observe-only and has zero trading authority.
5. **A6 research-factory work may begin after W1 PIT/provenance boundaries** rather than waiting for KG authority escalation. Replace the old from-scratch orchestration with Qlib + RD-Agent. Candidate models remain observe-only and cannot trade.
6. **A2 HITL promotion remains a later explicit owner decision.** Only after the visible workstation and revised boundaries are understood should the owner decide whether to enable unattended local paper.
7. **A3 multi-session unattended-paper reliability** runs only after that promotion and continues to use the frozen local ledger/LEAN semantics unless a replacement separately passes conformance.
8. **A5 KG authority escalation** remains later and gated: observe -> veto -> bounded reweight -> propose, with HITL at each escalation.
9. Incremental model/knowledge promotion and shadow/live readiness remain later; live capital stays disabled.

This reordering does **not** retroactively change A2's validated behavior or evidence. It only delays authority widening while product/research layers are assembled under authority NONE.

# Immediate implementation order

1. Add explicit runtime-mode contract (`BACKTEST`, `LOCAL_SIMULATED_PAPER`, `BROKER_HOSTED_PAPER`, `LIVE`) and fail-closed authority mapping.
2. Add bitemporal knowledge/RAG eligibility/provenance contract and tests; integrate it with temporal KG semantics.
3. Add read-only core API projections for account/session/decision/PIT/research state.
4. Establish the Open Papertrade frontend fork/service boundary and replace its trade/RAG authority calls with core APIs.
5. Add Docker/WSL2 local runner manifest with service-specific secrets.
6. Add OpenBB acquisition adapter/service with canonical materialization tests.
7. Add Qlib/RD-Agent research job protocol and immutable experiment bundle/artifact manifest.
8. Mirror finance-quant experiment ledger into Qlib Recorder/MLflow.
9. Only after those observe-only slices pass conformance, revisit A2 HITL as an owner decision.

# Authority checkpoint after this decision

- trading authority: **NONE**
- unattended local paper: **DISABLED**
- broker-hosted paper: **NOT AUTHORIZED**
- live capital: **DISABLED**
- frontend: **OPERATOR/RESEARCH ONLY**
- KG/RAG/model: **OBSERVE/RESEARCH ONLY**
- A2 hidden acceptance: **PASSED, seal use 1/1 consumed; MUST NOT be rerun**
