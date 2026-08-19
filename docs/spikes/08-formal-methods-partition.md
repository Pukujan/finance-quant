# Spike #8 — Quant-specific formal-methods partition: properties vs PBT vs TLA+ vs selective Lean proof

Issue: Pukujan/finance-quant#8
Status: **DECIDED 2026-08-19** — ADOPT tiered partition (sec. 2) + fossil-core#176 catalog format (live at contracts/properties/finance-quant-properties-v1.json with validation test); ADOPT PromotionLadder.tla plan; DEFER Lean proofs (timeboxed checker-soundness attempt post-slice); REJECT single-tier. Decision recorded on issue #8 under owner auto-delegation (owner-reversible).
Serves invariants: all of I1-I8, by assigning each the *cheapest enforcement tier that
can actually carry it*. Consumes: fossil-core#176 (external assurance machinery).

---

## 1. The partition principle

Formal methods die from over-application. The decision this spike must produce is a
**partition map**: every invariant gets exactly one primary enforcement tier, with
deeper tiers reserved for the few properties whose failure is catastrophic *and* whose
models are small enough to verify.

Tier ladder (cheap -> expensive):
- **T0 compile-time/static** — types, the temporal-effect checker (#3), schema
  validation, lint rules. Runs per keystroke/PR.
- **T1 property-based testing** — Hypothesis-style generative tests + stateful
  (rule-based) testing of services. Runs per CI.
- **T2 stateful/generative fault campaigns** — the adversarial harness (#9):
  model-based poisoning fixtures. Runs nightly/weekly.
- **T3 model checking (TLA+)** — exhaustive-ish exploration of *protocol* state
  machines (promotion, sealing, ledger retry/resume). Runs on spec change.
- **T4 selective theorem proving (Lean)** — small kernel properties with unbounded
  payoff, e.g., temporal checker soundness claims. Runs rarely; artifacts persist.

## 2. Proposed partition (the deliverable — owner amends)

| Property / invariant | Primary tier | Deeper tier justified? | Why |
|---|---|---|---|
| I1a no feature uses kt > t (expression level) | **T0** temporal checker | **T4** prove checker soundness: "accepted exprs have correct kt_bound" — small kernel, huge blast radius | checker is the single choke point for all lanes (#7) |
| I1b data layer never returns post-kt facts | **T1** PBT on PITStore.as_of (random vt/kt queries vs in-memory gold model) | T2 poison fixtures (restatements, D2 storm from #2) | interface is narrow; model-based test is natural |
| I2 run record completeness/determinism | T1 schema + double-run diff (#5 contract #8) | — | mechanical, no theorem needed |
| I3 holdout sealing lifecycle (seal -> open -> score -> log) | **T3 TLA+** | — | this IS a small concurrent state machine with adversarial agents; model-checking shines (#9 owns the protocol, #8 models it) |
| I4 fill semantics conformance | T2 poison drills + contract tests (#5 sec. 3/5) | — | numeric realism is empirical, not provable |
| I5 lanes cannot promote / write authority | T0 capability types (no promotion API in lane sandbox) + T1 auth tests | T3 if promotion protocol is TLA+-modeled anyway | mostly access control; least exotic tier works |
| I6 risk veto mechanical | **T1 PBT grafted onto LEAN bridge**: generate adversarial order streams (oversize, oversize-after-loss, correlated burst) -> invariant "position/loss never exceeds limit" holds | T4 candidate later: prove the pure-risk-checker function (it's a pure function of state+intent -> allow/deny) | pure core + IO shell makes T4 feasible later without T4 now |
| I7 no deletion of failures/revisions | T1 ledger API tests (no delete path exists) + infra (append-only store config) | — | enforcement is architectural |
| I8 promotion ladder transitions exact | **T3 TLA+** (same spec as I3's; one spec models both sealing and ladder) | — | few states, catastrophic transitions, classic TLC bait |
| retry/resume never duplicates authority (#4 adversarial #16) | T1 idempotency-key PBT | **T3** include in the same TLA+ spec | retry semantics are where real systems actually break |

Cross-check with fossil-core#176: property-driven dev, mutation testing, hidden
holdouts, TLA+, Lean live **there** as machinery. This repo's decision is only *which
properties ride which tier* and which proofs are quant-specific enough to live here
(I1a soundness, risk-checker totality) vs upstream.

## 3. Concrete artifacts the spike/Phase B should produce

1. `contracts/properties/finance-quant-properties-v1.json` — machine-readable partition
   table. **Format aligned with fossil-core#176 (verified 2026-08-19)**: property
   records carry stable `property_id`, statement, severity, semantic owner, executable
   oracle/test refs, mutation scope, optional TLA+/Lean refs, hidden-acceptance flag,
   lifecycle status. We reuse their catalog conventions (and their PR rule:
   "Properties / Property impact: PRESERVE|STRENGTHEN|CHANGE / Oracle") instead of
   inventing a parallel `invariants.yaml`. CI refuses a trial whose referenced property
   has no harness.
2. T1 suite v1: `as_of` PBT vs gold model (uses #2 fixture), risk-veto PBT vs
   adversarial order generator, ledger idempotency PBT.
3. T3 spec v1: `PromotionLadder.tla` — states:
   `SEALED_HOLDOUT_IDLE / SEALED / CAMPAIGN_RUNNING / SCORED / REVIEW /
   PAPER APPROVED / TINY_LIVE_APPROVED`, plus ledger-retry actions; invariants:
   "no transition skips REVIEW with outcome ADOPT", "seal cannot reopen except via
   SCORED", "retry never forks two authority records." TLC on a 3-agent model is
   minutes of compute.
4. T4 candidate statement (state, don't prove yet): `checker_sound : forall e t,
   accepts(checker, e, t) -> kt_bound(e) <= t`. If the Lean route via fossil-core#176
   is turnkey, one timeboxed attempt; otherwise DEFER the proof, keep the property.

## 4. Options scored

| Option | I1-I8 coverage | Cost | Failure mode | Verdict lean |
|---|---|---|---|---|
| A. Tiered partition as above (recommended) | ++ | medium | requires discipline to not gold-plate T3/T4 | **recommended** |
| B. Everything PBT | + | low | protocol bugs (ladder, sealing) are exactly what PBT finds late | REJECT as sole tier |
| C. TLA+ everything (spec-first shop) | + on paper | very high | specs rot when the PD loop is faster than spec maintenance; REJECT | REJECT |
| D. Vibes + integration tests | 0 | low now | catastrophic later, and Phase C has no teeth | REJECT |

## 5. Interaction with other spikes (must be consistent at reconciliation)

- #3's checker is T0; its soundness property is the **top T4 candidate** (sec. 2, row 1).
- #5's contract tests are the execution-side T2 corpus.
- #9's adversarial campaign is precisely the T2 tier productized; its sealed-lifecycle
  is the T3 spec's subject. **#8 and #9 decisions should point at each other.**
- #7 lanes inherit all tiers transitively: a lane proposal is only a Tier-0-acceptable
  string until it climbs the ladder.

## 6. Vertical-slice impact

- `invariants.yaml` + T1 suite v1 + TLA+ spec v1 are small, concrete, and unblock the
  slice's "mechanically enforced temporal/risk invariants" claim (master issue, Done-when).
- T4 proofs are explicitly NOT in the slice.

## 7. Evidence gaps before decision

- ~~Read fossil-core#176~~ **Done (2026-08-19).** Key imports into this spike:
  their Lean-first zones are lifecycle/pack/promotion semantic kernels ("small timeless
  semantic laws"; explicitly NOT the whole Python implementation) — our T4 candidate
  (checker soundness) fits the same pattern; their TLA+-first zones are durable-store/
  redaction and projection/rebuild — our promotion/sealing spec is the quant analog
  and should borrow their spec style (bounded TLC config, invariant IDs linked back to
  property catalog); their holdout doctrine (properties public, cases private, only
  aggregate receipts public) is exactly what #9 adopts. Residual gap: confirm the
  property-catalog JSON schema file exists on fossil-core main (issue lists it as a
  Phase-0 checkbox, possibly not yet merged) and mirror its field names.
- Owner's appetite for TLA+ upkeep: the spec is ~200-400 lines; someone must own it.

## 8. Recommendation

**ADOPT option A** with the partition table (sec. 2) as the decision text. **ADOPT**
the three concrete artifacts (sec. 3) into Phase B. **DEFER all T4 proofs** except a
timeboxed checker-soundness attempt if fossil-core#176's Lean machinery proves
turnkey. **REJECT** single-tier strategies in both directions (B, C, and D).
