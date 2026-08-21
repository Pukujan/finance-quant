# Phase B Owner Decision Gates — Slice 1 Real Ingest

**Status:** Awaiting owner decisions before Slice 1 (real vendor ingest) may start  
**Scope:** Decisions that establish the source, population, cost, runtime, and CI shape of the first canonical Phase B fixture.  
**Decision authority:** Repository owner. Engineering may recommend and prepare, but must not silently choose a vendor, universe, spending limit, Python runtime, or fixture policy.

## 1. Gate summary

All five gates below must be explicitly checked off before Slice 1 begins. The chosen values become part of the fixture provenance and must be recorded in the ingest run and manifest inputs. Changing any of them after data is fetched requires a new ingest run and normally a new fixture manifest hash.

| Gate | Owner must decide | Recommended default | Rollback / reversible alternative | Issue mapping |
|---|---|---|---|---|
| G1 | Vendor: Polygon, Alpaca, or another approved source | **Polygon.io** as canonical authority | Prototype with Alpaca; keep the PIT contract vendor-neutral; re-ingest and re-freeze with Polygon | #1, #2 |
| G2 | Universe: S&P 100, Nasdaq-100, or a named custom list | **S&P 100**, with the exact dated constituent list pinned; use Nasdaq-100 if the benchmark priority is technology/growth exposure | Replace the symbol manifest and re-ingest; never silently change symbols inside an existing fixture | #1, #2, #7 |
| G3 | Monthly data budget ceiling, including tax/overage margin | **Owner-confirmed ceiling of $100/month** for the initial Polygon path; do not authorize paid usage without a key and ceiling | Cap requests at the approved tier, reduce universe/history, pause real ingest, or use Alpaca/synthetic fixtures | #1, #10 |
| G4 | Python pin: 3.11 or 3.12 | **Python 3.12**, matching `.github/workflows/phase-b.yml` today; validate Qlib and dependency wheels before broad ingest | Pin 3.11 consistently in CI and project metadata if Qlib compatibility requires it; regenerate environment lock/fixture only as needed | #1, #4, #10 |
| G5 | CI fixture strategy: full or reduced universe | **Reduced fixture in pull-request CI** (5–20 symbols, short range); full owner-approved fixture on scheduled/nightly or release verification | Move full-fixture verification to nightly/manual CI, or temporarily run reduced fixture everywhere while preserving the full manifest separately | #1, #2, #10 |

The $100 recommendation is a proposal, not authorization. The owner should replace it with an explicit amount and currency if different.

## 2. Decision details and trade-offs

### G1 — Vendor confirmation

**Recommended choice: Polygon.io.** The Phase B plan identifies Polygon as the primary authority because its daily aggregates and corporate-action endpoints fit the adapter, and its timestamp/provenance story is intended to support the `vt`/`kt` PIT contract. `.env.example` already names `POLYGON_API_KEY` and `POLYGON_BASE_URL`, and the adapter's source defaults to `polygon`.

**Trade-offs:** Polygon incurs approximately the plan's stated `$49–$199/month` research-tier range for broader access, requires secret management, and remains subject to API availability/field behavior. Alpaca is cheaper or free for a prototype and can validate the adapter boundary, but has shorter history and weaker corporate-action/fundamental coverage. A different vendor may improve cost or coverage, but requires an explicit field mapping and a new receipt/provenance review. Scraped/Yahoo data is not an acceptable authority because it does not establish defensible knowledge time and conflicts with #2.

**Rollback:** Use Alpaca only as a labeled prototype, or use a deterministic synthetic fixture for contract tests. Keep `source.vendor`/receipt values truthful; do not relabel Alpaca rows as Polygon. Any vendor switch requires re-ingest and a new manifest hash.

**Blocked until decided:** finalize the production transport/configuration and secret name; implement vendor-specific request and response mapping; choose the authoritative corporate-action semantics; estimate request volume and cost; approve the first real API smoke test; and freeze the fixture's source metadata. Slice 1 cannot claim a canonical Polygon fixture while this gate is open.

### G2 — Universe scope

**Recommended choice: S&P 100**, because it is liquid, bounded, recognizable, and smaller operationally than an unconstrained custom universe. The alternative default in the Phase B plan is Nasdaq-100; it is preferable if the owner wants a more technology/growth-concentrated benchmark. A custom list is valid only when the owner supplies the complete symbol list and its effective/as-of date.

**Trade-offs:** S&P 100 offers broad large-cap sector coverage but requires constituent-history care and can introduce survivorship bias if treated as timeless. Nasdaq-100 is similarly liquid and simpler for a focused benchmark, but is less sector-balanced. A custom list can encode the research question precisely, but increases review, symbology, and reproducibility burden. The selected list must be stored as an explicit manifest input, not reconstructed from a live “current constituents” endpoint.

**Rollback:** Change the versioned universe manifest and rerun the minimum ingest. Do not mutate symbols in place or mix universes under one fixture hash. If the full universe is too costly, retain the owner-approved universe definition and run a reduced CI projection from it.

**Blocked until decided:** choose symbols and date ranges; resolve ticker/symbology rules; calculate request and storage size; define corporate-action coverage; choose the full and reduced fixture contents; and write acceptance expectations for the adapter and bakeoff.

### G3 — Monthly budget ceiling

**Recommended choice: `$100/month` hard ceiling** for the initial paid-data experiment, with usage monitoring and no automatic tier upgrade. This is within the plan's estimated Polygon research range while leaving room for CI/local reruns; the owner must confirm or replace it.

**Trade-offs:** A low ceiling reduces financial risk but may force a smaller universe, shorter history, manual fixture freezes, or Alpaca prototyping. A higher ceiling supports the planned 100-symbol/five-year ingest and reruns but increases recurring spend and does not by itself solve temporal or data-quality issues. CI should not repeatedly hit a paid live API; canonical fixtures should be reused and verified by hash.

**Rollback:** Stop live requests, reduce symbols/date range, switch to Alpaca, or use checked-in/synthetic fixtures. If the expected request volume cannot be demonstrated to fit the ceiling, do not proceed to full Slice 1.

**Blocked until decided:** select the vendor plan; set request/rerun guards and logging; approve API-key use in local-only workflows; size the full ingest; define whether corporate actions fit the ceiling; and decide whether full data is fetched once and frozen versus re-fetched on demand. This also gates any scheduled live job.

### G4 — Python version pin

**Recommended choice: Python 3.12**, because the existing Phase B workflow explicitly installs 3.12 and runs the benchmark, tests, verification, and smoke checks there. This is a runtime decision, not merely a CI setting: local instructions, project metadata, and dependency lock must agree.

**Trade-offs:** 3.12 minimizes immediate CI drift and is the current tested target, but Qlib or transitive scientific dependencies may have better wheel/compatibility coverage on 3.11. Pinning 3.11 may improve downstream compatibility at the cost of changing the workflow and validating the complete stack again. Neither choice should be inferred from the adapter alone.

**Rollback:** Adopt 3.11 consistently if a dependency compatibility check fails on 3.12. Do not support an unpinned “3.11 or 3.12” matrix for the canonical fixture without deciding which environment owns reproducibility.

**Blocked until decided:** update/confirm `pyproject` and lock metadata; validate `requirements-dev.txt` and Qlib/MLflow installation; align local and CI setup; select the canonical environment for manifest/receipt reproducibility; and run the clean-environment drill.

### G5 — CI fixture strategy

**Recommended choice: reduced fixture for pull requests, full fixture for scheduled/manual or release verification.** The plan already identifies shrinking CI to 20 symbols as a mitigation, while the first-ingest gate below deliberately starts smaller. The reduced fixture must be a deterministic subset with its own manifest and must exercise bars, PIT queries, and corporate-action paths where available.

**Trade-offs:** Full CI gives the strongest coverage and catches universe-scale/request regressions, but increases runtime, storage, API exposure, and flakiness. Reduced CI is fast and safer, but can miss scale, rate-limit, and symbol-specific failures. A full fixture checked into or fetched by CI must be hash-pinned and should not require a live secret on every pull request.

**Rollback:** Keep the full canonical fixture and move its verification to nightly/manual CI; temporarily use the reduced fixture for all PRs. If the full fixture cannot be retained, preserve its manifest/receipt metadata and document the loss rather than silently substituting a different dataset.

**Blocked until decided:** choose fixture paths and manifest policy; design CI cache/artifact handling; decide whether CI needs `POLYGON_API_KEY`; set runtime/storage thresholds; define the workflow triggers; and specify which checks run on reduced versus full data. The current workflow has no explicit live-ingest step and currently runs on Python 3.12, so it cannot be treated as the final policy by implication.

## 3. Minimum viable first ingest (MVFI)

Before attempting the planned 100-symbol/five-year load, run one owner-approved adapter validation ingest with:

- **5 symbols**, selected from the approved universe and recorded by ticker;
- **30 calendar days** (or the nearest 30-day market-data window) with explicit UTC start/end dates;
- daily adjusted bars;
- corporate actions for the same five symbols and date window, where the chosen vendor supports them;
- a fresh `ingest_run_id`, raw/request receipt metadata, and a provisional manifest hash;
- at least one hand-checked `as_of(vt, kt)` query, including a knowledge bound before and after a selected record;
- adapter pagination, rate-limit, empty-result, malformed-response, and authentication/error behavior exercised without exposing the API key;
- the timestamp representation decision resolved: the data contract notes that the adapter emits full UTC timestamps while the current `BitemporalRecord` validation accepts only `YYYY-MM-DD`. Slice 1 must widen validation or normalize both clocks, then pin that choice.

**MVFI pass condition:** all five symbols produce the expected date-bounded rows (allowing documented market holidays), records validate against the PIT contract, source and receipt fields are truthful, no `latest` query is used, and the same inputs produce the same logical payload/manifest when volatile fetch-time fields are controlled or explicitly excluded from the reproducibility comparison. MVFI success authorizes scaling; it does not authorize changing any of the five gates or declaring the full fixture canonical.

## 4. Engineering-blocker matrix

| Decision | Engineering work that must wait | What can proceed safely now |
|---|---|---|
| Vendor | Production adapter authority, live smoke test, vendor-specific corporate-action mapping, budget/request sizing, canonical provenance | Mock-transport adapter tests and contract review |
| Universe | Symbol manifest, symbology mapping, full/reduced fixture contents, storage/request estimates, acceptance sample | Generic adapter and PIT tests using test symbols |
| Budget | Paid-plan selection, live API credentials/use, full-scale range, rerun schedule, CI live-data policy | Cost model with request-count assumptions and synthetic fixtures |
| Python pin | Canonical environment lock, Qlib/MLflow install validation, CI metadata changes, clean-runner reproducibility claim | Version-agnostic documentation and isolated adapter logic, subject to later runtime validation |
| CI strategy | Fixture publication path, CI cache/artifact design, full/reduced thresholds, live-secret policy, workflow changes | Local MVFI design and non-live test workflow |

The following cross-cutting engineering item is independently visible in the data contract but is a **technical prerequisite** for loading the MVFI: resolve the full-timestamp versus day-granularity `BitemporalRecord` compatibility. It should be treated as a Slice 1 implementation gate and reflected in the resulting manifest hash, not papered over by dropping `kt` or using “latest.”

## 5. Owner decision checklist

Copy the selections below into the owner decision record and fill every blank. “Approved” means the owner has made the choice, not merely that engineering has suggested it.

- [ ] **G1 Vendor — approved:** ______________________________
  - [ ] Polygon.io canonical authority
  - [ ] Alpaca prototype/fallback
  - [ ] Other: ______________________________
  - API plan/tier: __________________________
  - Owner initials/date: _____________________

- [ ] **G2 Universe — approved:** _____________________________
  - [ ] S&P 100
  - [ ] Nasdaq-100
  - [ ] Custom list at: ______________________
  - Effective/as-of date and symbol manifest reference: ______________________
  - Owner initials/date: _____________________

- [ ] **G3 Monthly budget ceiling — approved:** _______________
  - Currency: __________  Hard ceiling: __________ per month
  - Overage/auto-upgrade allowed?  [ ] No  [ ] Yes, limit: __________
  - Owner initials/date: _____________________

- [ ] **G4 Python pin — approved:** ___________________________
  - [ ] Python 3.11
  - [ ] Python 3.12
  - Canonical environment/lock reference: ______________________________
  - Owner initials/date: _____________________

- [ ] **G5 CI fixture strategy — approved:** __________________
  - [ ] Full universe in PR CI
  - [ ] Reduced universe in PR CI; full fixture nightly/manual/release
  - Reduced symbols/count: __________________
  - Full fixture verification trigger: __________________
  - Owner initials/date: _____________________

- [ ] **MVFI authorization:** 5 symbols / 30 days approved after G1–G5
  - Symbols: ________________________________________________
  - Start/end: __________________ / __________________
  - Owner initials/date: _____________________

- [ ] **Technical timestamp gate acknowledged:** full UTC timestamps retained by widening PIT validation, or both clocks normalized to UTC dates (select one and document): ______________________________

## 6. Issue map and sequencing

- **#1 (master DAG / Phase B):** owns the Phase B sequence and the Slice 1 vendor/universe inputs. These gates are the explicit owner checkpoint before the DAG advances to real ingest.
- **#2 (PIT storage and bitemporal authority):** binds the `vt`/`kt` contract, source authority, as-of behavior, and no-latest rule. Vendor and universe choices must preserve this boundary; the timestamp precision mismatch is a Slice 1 technical gate.
- **#10 (local-subprocess / reproducibility decision):** informs the Python pin, budget-conscious local execution, fixture freeze, and CI policy. Full live data should not be an implicit per-PR dependency.
- **#4 (Qlib/MLflow boundary):** downstream of the Python pin and canonical fixture; runtime compatibility must be checked before claiming a reproducible Phase B environment.
- **#7 (search bake-off):** not a Slice 1 blocker, but consumes the approved fixture and therefore inherits its universe and manifest decisions.
- **#9 (sealed holdout):** downstream Phase B/Phase C handoff; it must not be built from an unapproved or mutable data universe.
- **#3 (DSL/IR):** downstream consumer; no owner gate here, but its evaluation must use the frozen PIT fixture rather than a live latest-data path.
- **#5 (LEAN):** downstream execution consumer; cost-model and replay work waits for a stable canonical fixture, though it does not determine the vendor.

**Start rule:** Slice 1 may begin real Polygon (or explicitly approved alternative) requests only after all five checklist gates are checked, the MVFI parameters are recorded, and the timestamp compatibility approach is documented. Any subsequent owner change creates a new decision record and triggers re-estimation/re-ingest as appropriate.
