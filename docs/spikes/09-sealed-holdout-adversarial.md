# Spike #9 — Sealed research holdout + adversarial acceptance protocol

Issue: Pukujan/finance-quant#9
Status: **DECIDED 2026-08-19** — ADOPT option A + sec. 3 runbook; SEAL-A max 2/epoch (reuse penalty), SEAL-B once ever; private repo Pukujan/finance-quant-holdout created with seal protocol README; credential audit finding documented on issue #9 (gh token has repo scope — owner to narrow with fine-grained PAT or bucket IAM). REJECT time-only holdout; DEFER escrow. Decision recorded on issue #9 under owner auto-delegation (owner-reversible).
Serves invariants: I3 (holdout stays holdout), I5 (no promotion by prose/score),
I6, I8 (gating), I7 (failures visible). **Phase C's operating system.**

---

## 1. What "sealed" must mean mechanically (not rhetorically)

Threat model: the adversary is *our own tooling* — research agents, search lanes (#7),
and future-us, all of which can read the repo. Defeating inspection by ordinary
coding/research agents (master issue, I3) requires:

1. **Separation:** sealed cases live OUTSIDE this repo — e.g., private repo
   `finance-quant-holdout` or an object-store bucket — with access limited to the
   owner role (GitHub: separate repo, no collaborator overlap with agent tokens;
   bucket: IAM policy minus agent principals). `gh` token on this box has `repo`
   scope — if agents share it, the seal is a courtesy, not a seal. **Owner action item
   regardless of design: agent credentials must not carry holdout access.**
2. **Commitment:** on sealing, publish in-repo: `seal_record := {case_set_id,
   sha256_merkle_root_of_cases, labels_hash, seal_timestamp, eval_harness_sha,
   scorecard_ref}`. Hash commits the project to the cases *before* any candidate is
   evaluated — prevents post-hoc case editing in BOTH directions (us cherry-picking,
   or accusing a lane's sponsor of tuning).
3. **Execution environment:** scoring runs in a clean runner (container/CI job) that
   mounts the sealed set + the candidate artifact + the reference interpreter (#3) —
   and holds NO OTHER credentials (no network beyond package pinning, no MLflow write
   except a single append-only result row via a one-shot token).
4. **Declassify path:** cases may become public only via an explicit `RETIRE_CASE`
   event logged in FOSSIL (#6) with reason; retired cases never rejoin the sealed pool.

Number/rhythm proposal: 2 sealed sets, staggered — `SEAL-A` usable at most twice per
project epoch, `SEAL-B` touched once ever, at the final promotion gate. Reuse of a
sealed set is itself a logged event with deflation penalty applied to the score
(freshholdout-style re-use control).

## 2. Case content (what the sealed sets contain)

Curated/train-case-style versions of every Phase C adversarial theme from issue #1,
PLUS honest hard cases (no poison, just regime shifts):

| # | Adversarial theme (from master issue) | Case shape |
|---|---|---|
| 1 | future leakage / shifted timestamps | labels/features placed with kt violations the checker must catch; a candidate that passes = checker broken |
| 2 | revised fundamentals + publication lag | D2-style restatement storm (#2 harness) with gold as-of answers |
| 3 | survivorship-biased universe | universe extract missing delisteds; candidate metrics must change vs full universe — if "same", candidate read the bias in |
| 4 | same-bar impossible fills | order intent at bar t fills at bar t close — contract violation (#5 sec. 3.4) must trip |
| 5 | stale/delisted instruments | trading a suspended name must be rejected/held per contract |
| 6 | split/dividend errors | adjustment-mode trap cases; receipts must show correct handling |
| 7 | timezone/calendar boundaries | DST switch, half-day, exchange holiday exercises |
| 8 | missing/duplicate/out-of-order bars | ingestion/pipeline must flag; no silent interpolation |
| 9 | holdout contamination | honey cases: sentinel labels watch for a candidate "suspiciously perfect" on sealed-vs-unsealed delta |
| 10 | graph feature leakage | late-announced edge (from #6 drill) must not influence as-of features |
| 11 | failed-trial deletion / selective reporting | harness attempts delete via ledger facade — must fail closed (I7) |
| 12 | parameter-search overfitting | garden-of-forking-paths probe: N=200 random variants of the candidate; if best beat median by less than deflated threshold, score = "search artifact" |
| 13 | transaction-cost/slippage sensitivity | score reported across the contracted model family (#5 sec. 3.3), incl. 2x stress |
| 14 | risk-limit override attempts | generated order storms + agent-instruction injection text trying to exceed limits; veto must hold (I6) |
| 15 | retry/resume duplicate authority | kill/resume mid-scoring; exactly one authority record (#4) |
| 16 | regime shift (honest hard) | sealed window chosen in a volatility/regime cluster disjoint from research window |

## 3. The adversarial campaign protocol (Phase C runbook, draft)

```
0. PRE-REGISTER   acceptance criteria + deflation thresholds + per-case expected
                  failure semantics, committed in-repo BEFORE seal opens. (I5)
1. SEAL           owner seals cases off-repo; publishes seal_record (sec. 1.2).
2. NOMINATE       candidate = run_record chain ending in a model/strategy artifact;
                  must already pass T0+T1 checks (#8) on UNSEALED data.
3. RUN            sealed harness executes: feature build -> reference/interpreter
                  eval -> LEAN execution eval (#5) -> risk drills -> retry drill.
4. SCORE          dual report: (a) headline vs pre-registered bars; (b) FULL
                  diagnostic dump incl. per-case deltas, cost sensitivity curve,
                  trial-count ledger of everything that touched the research data
                  (deflation input). Failed/invalid reported identically (I7).
5. REVIEW         FOSSIL PromotionReview (#6): owner renders ADOPT | CONSTRAIN |
                  REJECT with evidence links. Agent lanes MAY NOT be reviewers.
6. LOG+GATE       result + review hashes appended to an acceptance log whose tail
                  hash is what the next ladder rung cites (promotion ladder, #1).
```

## 4. Options scored

| Option | I3 strength | Leak-proofing vs own agents | Cost | Verdict lean |
|---|---|---|---|---|
| A. Off-repo sealed store + hash commitments + clean-runner protocol (recommended) | ++ | ++ | medium (mostly ops discipline) | **recommended** |
| B. Encrypted-in-repo cases (symmetric key held by owner) | + | + | low | acceptable fallback; but key hygiene on this box becomes the seal — verify agent sessions cannot read the keyring |
| C. Time-based holdout only ("nobody saw 2024 yet") | 0 | 0 | ~0 | REJECT: reproduces the classic "validation becomes training" decay; the master issue already rules this out in spirit |
| D. Third-party/escrowed evaluation | ++ | ++ | high + external dependency | DEFER until promotion to real capital is on the table |

Note (honest limit): against an adversary with the owner's own interactive session,
no software seal holds; the protocol secures the *agent/tooling* surface and creates
tamper-evidence, which is the stated goal (I3: "ordinary coding/research agents").

## 5. Vertical-slice impact

- Phase B needs: seal_record format + one sealed mini-set (tiny — 50 bars of synthetic
  poison) + the clean-runner harness skeleton wired to the ledger. The B1-B5 baselines
  then pass through a *toy* version of the full protocol, proving the plumbing before
  any real strategy is judged by it — this is exactly the master issue's "boring
  baselines establish whether the plumbing and evaluation protocol are trustworthy."
- The full 16-theme case library builds up during the slice and is Phase C's entry
  condition.

## 6. Evidence gaps before decision

- Owner picks seal storage (private repo vs bucket) and re-runs the credential audit
  (sec. 1.1 — agent tokens, keychain scope). This is a one-hour ops decision with more
  I3 impact than any code.
- Decide reuse policy numbers (my "2x / 1x" above are placeholders).
- Coordinate with #8: the SEAL->SCORE->REVIEW lifecycle is the TLA+ model's subject;
  names/states must match.

## 7. Recommendation

**ADOPT option A** with the runbook (sec. 3) as decision text, staging seals A and B,
tamper-evident commitments, clean-runner execution, pre-registered criteria, and
agent-excluded review. **REJECT C** outright. Defer D to the capital-promotion era.
Make the credential audit the first checkbox of the decision.
