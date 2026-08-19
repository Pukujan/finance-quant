# Spike #5 — LEAN execution bridge + fill/slippage/order semantics contract

Issue: Pukujan/finance-quant#5
Status: **DECIDED 2026-08-19** — ADOPT LEAN as sole execution truth with generated algorithms + sec. 3 contract; Qlib backtest triage-only; REJECT bespoke engines; DEFER zipline fallback. Decision recorded on issue #5 under owner auto-delegation (owner-reversible).
Serves invariants: I4 (backtest != execution truth), I6 (risk veto mechanical),
I8 (promotion gating)

---

## 1. Verified state of the world (2026-08-19)

- **LEAN** (QuantConnect/Lean, ~21.3k stars, Apache-2.0): event-driven C# engine with
  Python support (pythonnet), dotnet 10, `lean` CLI (`pip install lean`, Docker-based
  local runs, verified), pluggable models at every semantic point that matters:
  fill models, slippage models, fee models, buying-power/margin models, brokerage
  models (order-type support, market hours), plus an exhaustive regression-test suite
  (13k+ commits, active).
- LEAN already enforces things ad-hoc engines get wrong: market hours/early closes,
  same-bar fill discipline, stale data detection, delisting events, split/dividend
  adjustment modes, buying-power rejects. This is precisely the Phase C adversarial
  list for execution — a strong argument for adopting LEAN over a bespoke simulator.
- Linux containers first-class; Windows local runs supported via CLI + Docker.

## 2. What the bridge must be (and must NOT be)

The danger pattern: research dataframe -> hand-rolled loop -> "backtest". That path
re-implements (badly) everything LEAN already models, and then its numbers disagree with
LEAN's anyway — two execution truths, violating I4 in spirit.

Proposal: **one execution truth, reached through one bridge.**

```
Tier-2 manifest (memo #3)
      |
      v
[ StrategyCompiler ] --emits--> LEAN Python algorithm (generated, never hand-edited)
      |                            + config.json (pinned data, brokerage model,
      v                                 fill/slippage/fee models, risk modules)
[ OrderIntent log ] <------------ every signal->order decision, with kt context
      |
      v
[ ExecutionReceipt ]   normalized fills, fees, rejects, margin events -> ExperimentLedger (#4)
```

- The strategy side emits **order intents**, not fills. LEAN decides fills.
- The bridge owns a **semantics contract** (sec. 3) — a versioned, test-locked document.
- LEAN's own data feeds: for Phase B we run LEAN over the **same manifest-pinned extract**
  (#2/#4) via a custom data source / Lean `PythonData` or pre-converted LEAN-format data.
  Using QC's cloud data for research would fork the data lineage — not allowed under I2.

## 3. Fill/slippage/order semantics contract (the deliverable)

A versioned contract doc + conformance tests. Minimum contents:

1. **Order lifecycle**: intent -> risk-check (I6, *before* LEAN sees it, defense in depth —
   plus LEAN buying-power) -> submission -> fill/reject/expiry. Every transition logged.
2. **Fill model selection is explicit per run** and recorded in the run record:
   e.g. `EquityFillModel` semantics (marketable limit behavior, same-bar rules,
   volume-share caps if configured). "Default" is a banned word in the contract; every
   run names its models and their parameterization.
3. **Slippage/fee models**: named, parameterized, and *adversarially stressed* (#9):
   constant, spread-proportional, volume-impact; the acceptance campaign demands
   sensitivity analysis across them (a strategy that only works at zero fees is
   reported as such, loudly).
4. **Same-bar discipline**: an order submitted from data of bar `t` fills no earlier
   than bar `t+1` open (daily) or LEAN's documented intrabar rules (minute) — the bridge
   tests this explicitly with a poisoned fixture (Phase C #4).
5. **Corporate actions & delistings**: adjustment mode (`Raw` vs `SplitAdjusted` vs
   `TotalReturn`) is part of the run record; delisting events must appear in receipts.
6. **Timezone/calendar**: all timestamps exchange-local-then-UTC-dual-stamped; market
   hours from the pinned calendar, tested at DST edges and half-days (Phase C #7).
7. **Shorts/borrow**: availability and cost explicit; "infinite borrow at zero cost" is a
   named debug model, never a default.
8. **Determinism**: same extract + same algorithm + same config = same fills byte-for-byte.
   Tested by double-run diff in CI (I2).

## 4. Options scored

| Option | I4 execution realism | I2 determinism | Cost | Verdict lean |
|---|---|---|---|---|
| A. LEAN + generated algorithm + contract + fixture data | ++ | ++ | medium-high | **recommended** |
| B. LEAN via QC cloud data | ++ | 0 (lineage fork) | low | REJECT under I2 |
| C. Qlib backtest as the execution truth | 0/+ (daily topk semantics, thin fill model) | + | low | acceptable for *feature triage* reporting only; never acceptance |
| D. Bespoke Python event engine | - | 0 | high | REJECT |
| E. zipline/zipline-reloaded | + (pipeline API nice; maintenance thin, slippage/fill less complete) | + | medium | DEFER (fallback if LEAN bridge collapses) |

## 5. Bridge verification tasks for the spike

1. **Hello-PIT**: run generated LEAN algorithm over fixture extract; confirm fills equal
   a hand-computed expected ledger for a 4-symbol, 60-day toy (signed arithmetic, no ML).
2. **Poison drills** (from #9's list, execution subset): duplicate bars, missing bar,
   out-of-order bar, price spike 100x, halted symbol, delisted symbol mid-holding —
   each must produce a *specific, contracted* receipt (reject/hold/liquidate), not a crash
   or a silent fill.
3. **Double-run determinism** check (contract item 8).
4. **Parity probe**: same Tier-2 manifest compiled to (i) LEAN and (ii) Qlib backtest —
   not to make them equal (they won't be; different fill philosophies) but to have a
   documented, tested explanation of every systematic difference. The parity doc becomes
   part of the contract.

## 6. Vertical-slice impact

- Phase B step 5 ("LEAN backtest execution with realistic costs/fills") is entirely this
  bridge + contract. Slice needs: StrategyCompiler MVP (manifest -> LEAN Python),
  one custom data path for fixture extracts, ExecutionReceipt normalization into the
  ExperimentLedger (#4), contract v0.1 with conformance tests 1-4.

## 7. Evidence gaps before decision

- None blocking for *adopting LEAN as execution engine*; evidence tasks above are
  build-verify, not explore.
- If tiny-live ever enters scope (promotion ladder), brokerage model choice becomes a
  real decision; out of scope for this spike beyond recording "LEAN supports it."

## 8. Recommendation

**ADOPT A**: LEAN as the sole execution/backtest engine; generated algorithms only;
same-bar and model-naming discipline contract; fixture-data bridge; determinism and
poison-drill conformance tests are part of "done." **REJECT** Qlib-as-execution-truth
for acceptance (keep for triage) and bespoke engines. Contract sec. 3 goes into the
issue as decision text.
