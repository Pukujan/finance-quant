# Handoff — product executioner merged to main

Date: 2026-08-28
Branch: `main`
Active issue: #27
Product mode: local research + zero-money simulated paper only; no broker/live capital

## Merge state

Clean product integration PR #34 is merged to `main`.

Merged product commit: `9fb53a7974ada959b3ed3bd7d7efe135e6e98848`.

The merge was built directly on the previous `main` rather than merging the long-lived bootstrap branch. Obsolete A1/A2 assurance workflows/contracts, hidden-acceptance machinery, formal/TLA promotion material, and old assurance handoffs were deliberately excluded. Dirty integration PR #33 is closed and unmerged.

Before merge, the exact PR head passed:

- `lab-control-plane`: lab correctness tests, targeted semantic mutation probes, candidate CLI smoke, workstation regression;
- repository `tests`: full pytest + smoke;
- `phase-b`: benchmark, 3-run determinism drill, and `verify --phase-b`.

During clean integration, two pre-existing Windows Phase-B path bugs were exposed and fixed: external temporary receipt paths no longer crash report generation, and ephemeral LEAN temp-directory paths are normalized before determinism comparison.

## Fixed executioner now on main

`finance_quant.lab` owns the benchmark/evaluation semantics. Candidate code does not own historical labels, PIT cuts, scoring, evaluation identity, router timing, or paper-account truth.

Stable flow:

`publish immutable PIT components -> assemble fixed historical benchmark -> expand explicit/bounded arms -> parallel predictions -> same canonical realized outcome -> ExperimentLedger -> prior-OOS-only router -> isolated shadow paper`

Public CLI:

```text
python -m finance_quant lab publish-component SPEC.json PAYLOAD.json --registry .lab-state/registry --output artifact.json
python -m finance_quant lab assemble-benchmark EVALUATION.json COMPONENTS.json --registry .lab-state/registry --output benchmark.json
python -m finance_quant lab run benchmark.json candidates.json --state-dir .lab-state --parallel 16 --output result.json
```

The lab supports multiple simultaneous versions of one lane, exact `(lane, artifact_hash)` arm selection, bounded matrix expansion, canonical full-information scoring, actual evaluation-content hashing, and independent persistent shadow-paper accounts.

`finance_quant.workstation` is also on `main` and remains the visible real-data research/paper baseline.

## Who does what now

**Core/integration owner:** preserve and evolve the fixed laboratory contracts, integrate candidate work, resolve cross-lane conflicts, run merge gates, and keep `main` coherent.

**Luna/subagents:** implement and execute candidate lanes/models against those contracts. Luna may spawn many workers, but candidate workers must not redesign benchmark/outcome semantics locally.

Use `docs/plans/LUNA_CANDIDATE_PROTOCOL.md` as the implementation brief.

## Next exact implementation wave

Spawn candidate workers in parallel against #29, #19 and #21:

1. raw OHLCV + timestamped splits/dividends/corporate actions;
2. SEC filing text/amendments;
3. ALFRED-style macro vintages;
4. historical financial news/events + syndication dedup + hype/attention features;
5. temporal supplier/customer/competitor/product relationships;
6. bounded temporal KG traversal and PIT-safe RAG;
7. stronger local predictive model families.

Each worker publishes immutable versioned component artifacts and/or arm executors. Then run the first real family:

`price | +fundamentals | +news/hype | +events | +supply/competitors | +macro | +RAG | +bounded-KG | combined | contextual router`

across multiple symbols/regimes using the same canonical subsequent market outcomes.

## Important boundaries

- Software correctness passing does not imply predictive value.
- Negative OOS results are retained.
- Do not inspect the private/sealed holdout without explicit authorization.
- Do not add broker/live-capital authority.
