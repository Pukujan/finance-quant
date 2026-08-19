# Spike #2 — PIT market-data semantics + temporal storage bake-off

Issue: Pukujan/finance-quant#2
Status: **DECIDED 2026-08-19** — ADOPT bitemporal semantics; CONSTRAIN storage bake-off (ArcticDB constraint: Apache-converted versions only); REJECT kdb+/ClickHouse-as-authority/Qlib-provider-as-authority. Decision recorded on issue #2 under owner auto-delegation (owner-reversible).
Serves invariants: I1 (PIT correctness), I2 (reproducibility), I7 (failed trials visible — via immutable revisions)

---

## 1. The semantics decision (precedes storage)

Storage cannot be chosen before the *temporal model* is fixed. Four candidate models:

### A. Bitemporal (valid-time × knowledge-time) — recommended
Every fact carries two timestamps:
- `vt` (valid time): the market/entity time the fact is about (bar close, fiscal period end).
- `kt` (knowledge time a.k.a. `known_at`): the first instant our system could have known it
  (vendor publication time + ingest receipt time, whichever the contract defines — must be pinned).

Reads are always `AS OF (vt, kt)` pairs. This is the only model that directly answers the
I1 question "what did we know at time T about time t?" and the only model that survives
revised fundamentals / restatements (issue #1, Phase C adversarial list) without hacks.

### B. Snapshot/revision log (append-only, single clock + revision ID)
One event-time column + monotonically increasing revision IDs per symbol. Cheaper to build
on plain file storage (Parquet + manifest). Weakness: "as of publication" queries become
join gymnastics against an ingest ledger; restatement analysis is manual.

### C. Valid-time only (event-time column, overwrite on correction)
**Disqualifying under I1/I2**: corrections destroy history; a backtest reran after a
vendor restatement silently changes. Reject as the authority store (fine as a *derived
cache* produced from A/B).

### D. Snapshot-only dataset pinning (hash a frozen extract per experiment)
Common in research (this is essentially what Qlib's binary provider gives you). Necessary
as an *experiment input contract* but insufficient as the **authority**: cannot express
"what was knowable on 2019-03-15" without storing per-day snapshots → prohibitive.

**Recommendation A.** Define the PIT record contract first (§4), then let storage compete
on how well it serves that contract.

## 2. Storage bake-off candidates

| Candidate | Temporal model fit | Ops | License / cost | Notes |
|---|---|---|---|---|
| **XTDB 2.x** | `++` native bitemporal, SQL:2011 `VALID_TIME`/`SYSTEM_TIME`, AS OF queries | Single JVM binary or Docker; Postgres-wire | Apache-2.0 (verified project; edition specifics to re-verify) | Purpose-built for exactly this. Query perf for wide cross-sectional scans is the open risk — must be measured. |
| **TimescaleDB (Postgres)** | `+` implement bitemporal as two timestamp columns + exclusion constraints; no native AS OF | Mature, boring | Apache-2.0 core; some features TSL | Most operable option; bitemporality is hand-rolled (index design + query discipline). |
| **ArcticDB** | `+` versions/snapshots = knowledge-time axis done *by the store*; valid-time is the index | Serverless, S3/LMDB/Azure; Windows/py3.9–3.14 binaries (verified) | **BSL 1.1 — production use requires paid Man Group license**; each release converts to Apache-2.0 on a dated schedule (v4.0→Aug-2025 … v4.5→Aug-2026) (verified) | De-facto industry store for this (Man AHL). Excellent per-symbol time travel. Two-axis PIT still needs a knowledge-time discipline layered on versions. **License is a real constraint for a trading lab → legal decision, not technical.** |
| **Parquet/Delta/Iceberg lake + manifest ledger** | `0/+` everything hand-rolled; Delta/Iceberg give table time-travel by *commit*, which is system-time only | Cheapest storage | Apache-2.0 | Strong as the immutable artifact layer under any choice; weak as a queryable bitemporal authority by itself. |
| **ClickHouse** | `0` no temporal semantics; versioning via `ReplacingMergeTree` is lossy-by-design | Heavy-ish server | Apache-2.0 | Great scan speed; wrong tool for the *authority*. Plausible for derived analytics cache. |
| **kdb+/q** | `+` idiomatic as-of joins (`aj`) | Ops burden, memory-first | Commercial, expensive per core | Industry standard but licensing cost fails "reproducible by a fresh runner" (I2) unless a community/32-bit path is pinned. Likely REJECT on cost/gravity. |
| **Qlib binary provider** | `-` snapshot-style, no knowledge-time model | trivial | MIT | Not an authority candidate; it is a *consumer* format (see memo #4 boundary). |

## 3. Bake-off harness the spike must actually run

Same 6 datasets × same 8 queries × same box, results in this repo as CSV + receipt:

**Datasets:** D1 20y daily OHLCV ~3k US symbols; D2 same with **synthetic restatement
storm** (5% of rows re-published with corrections 30–400 days late — this is the dish that
kills candidates); D3 survivorship-free universe membership changes; D4 corporate actions
stream; D5 fundamentals with publication lag; D6 1-minute bars subset (volume stress).

**Queries:** Q1 full-universe cross-section AS OF (t,t); Q2 single-symbol deep history
AS OF; Q3 "what changed between knowledge-time k1,k2" (diff/revision audit — I7); Q4
restate-and-rerun: rerun a backtest input build at kt, then at kt' after restatements,
and diff; Q5 universe membership AS OF; Q6 point-in-time fundamentals join
(AS OF ε-join on two bitemporal tables); Q7 rolling-window bulk export for training
(the Qlib feed path); Q8 cold repeat of Q1 for latency variance.

**Measures:** wall time p50/p95, storage bytes, correctness on D2/D4/D5 (binary
pass/fail against a reference implementation over the in-memory gold fixture), and
"lines of query code" as an honesty metric for hand-rolled options.

## 4. PIT record contract (the thing being stored)

Draft — this is the asset the spike must nail regardless of storage winner:

```
record := {
  instrument_id    : stable internal symbology (never vendor ticker),
  namespace        : {bar | corporate_action | fundamental | universe | macro | ...},
  vt               : valid-time (exchange/event time, tz-explicit, calendar-pinned),
  kt               : knowledge-time (first-knowable instant; NaT = forbidden),
  payload          : namespace-schema versioned blob/columns,
  source           : {vendor, feed, collection_method},
  ingest_receipt   : {ingest_run_id, landed_at, raw_payload_hash},
  revision         : monotonically increasing per (instrument, namespace, vt),
  superseded_by    : revision | null          -- corrections never delete (I7)
}
```

Hard rules for the owner to ratify or amend:
1. `kt` is defined per source contract (e.g., vendor publication timestamp if provided,
   else first byte received). **Ambiguity in `kt` definition is the #1 PIT failure mode.**
2. All reads go through one `as_of(vt, kt)` API; no code path may read "latest".
3. Corporate actions are events with their own `kt` (announcement ≠ ex-date ≠ effective).
4. Universe membership is data, not config: bitemporal membership intervals.
5. Delisted/suspended instruments remain queryable forever (survivorship, Phase C).

## 5. Vertical-slice impact (what Phase B needs from this decision)

- `PITStore` interface: `as_of(namespace, instruments, vt_range, kt) -> frame`,
  `revisions_between(k1, k2)`, `snapshot_pin() -> dataset_manifest_hash`.
- Canonical fixture (Phase B step 1) = D1–D5 mini versions + gold expected answers.
- Manifest hash is what experiments record (I2) — storage must be able to *prove*
  a revision-stable extract.

## 6. Evidence gaps before decision

- Measured bake-off (§3) — none of the scores above are measured except fit-by-design.
- XTDB 2.x current release/edition terms re-verification (README URL changed; repo reorganized).
- ArcticDB license posture: owner decides accept-BSL-for-research-only, pin a
  converted-Apache version, or drop. This can flip the ranking.
- Actual data source pick (vendor → determines ground truth for `kt` definition).
  Qlib's official bundle is *temporarily disabled* (verified 2026-08-19) with a community
  mirror; do not build the authority on scraped Yahoo data without a licensed path.

## 7. Recommendation (evidence-based, not a decision)

**ADOPT bitemporal semantics (Model A) unconditionally.** For storage, **CONSTRAIN** the
bake-off to {XTDB 2.x, TimescaleDB, ArcticDB (pending license ruling), Parquet+manifest
as the baseline} and run §3. Lean toward XTDB or ArcticDB for the authority with a
Parquet export as the reproducibility pin; keep Timescale as the operability fallback.
REJECT kdb+ (cost vs I2), REJECT ClickHouse-as-authority, REJECT Qlib provider as
anything but a downstream consumer format.
