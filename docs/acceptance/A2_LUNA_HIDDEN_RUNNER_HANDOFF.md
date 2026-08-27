# A2 Luna Authorized Hidden-Acceptance Runner Handoff

Issue: #16  
Assurance phase: A2  
Runtime: LEAN commit `185c691b89f28bd68e48d53c02147415134975f0` under the A1 `ADOPT_WITH_CONSTRAINTS` scope.

## Mission

Execute one authorized private A2 hidden-acceptance campaign against the **frozen public evaluation candidate** and return only a public `SealRecord`, aggregate-only `SafeAcceptanceReceipt`, exact candidate artifact SHA-256, and aggregate operational identities. This worker is an assurance worker only; it may not enable paper/live authority or grant HITL promotion.

The authoritative `public_eval_sha` and candidate artifact SHA-256 are recorded in the durable public handoff after `.github/workflows/a2-candidate-freeze.yml` passes. Never substitute a later branch head or working tree.

## Isolation and secrecy

Exact hidden cases, labels, expected outputs, case IDs, counts, traces, paths, and oracle internals remain private in `Pukujan/finance-quant-holdout` or its approved sealed store. They must not be copied to the public repo, ordinary logs, chat, or GitHub Actions.

Stage inputs with an authorized stager, then execute the actual scorer with candidate/sealed/runtime inputs read-only, output writable only, no GitHub/provider/brokerage/MLflow/SSH/cloud credentials, and no general network. The scorer must have exactly one aggregate result writer. Development of runner mechanics uses synthetic private fixtures only and consumes no real seal use.

## Frozen public contract

The private evaluator is derived only from public Issue #16, `contracts/trading/autonomous-trader-v0.json`, `contracts/properties/finance-quant-properties-v1.json`, `docs/plans/A2_AUTONOMOUS_TRADER_V0.md`, and the public A2 tests. Do not change public semantics after inspecting candidate behavior.

The registered A2 hidden suite must independently falsify the already-public classes, including PIT decision safety; risk non-widening; order/fill/account invariants; exact accounting; duplicate/reorder/drop handling; crash/restart atomicity; session N→N+1 continuity; deterministic replay from stored evidence; runtime/fixture binding; read-only operator authority; and fail-closed capability authority. Exact private cases and counts remain secret.

The A2 SealRecord must use:

- `case_set_id` beginning with `A2-`;
- `eval_harness_sha` equal to the exact frozen public evaluation commit;
- `scorecard_ref = issue-16-a2-public-contract-v1`;
- `max_uses = 1`.

The aggregate passing receipt must contain exactly the standard SafeAcceptanceReceipt fields, use `use_number = 1`, have empty `failure_classes`, and expose only these two metrics, both equal to `1.0`: `conformant`, `evaluated`.

## Exact candidate artifact

From two independent clean public clones:

```bash
PUBLIC_EVAL_SHA=<exact frozen SHA from public handoff>
git cat-file -e "${PUBLIC_EVAL_SHA}^{commit}"
git archive --format=tar --prefix=finance-quant/ "$PUBLIC_EVAL_SHA" > a2-public-candidate.tar
sha256sum a2-public-candidate.tar
```

Both archives must have the exact candidate SHA-256 recorded by the public `a2-candidate-freeze` receipt. Any mismatch stops before case load. The scoring environment must independently verify LEAN commit `185c691b89f28bd68e48d53c02147415134975f0`.

## Public preflight before any seal use

Run from the immutable candidate extraction:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q \
  tests/test_a2_contracts.py \
  tests/test_a2_account.py \
  tests/test_a2_session.py \
  tests/test_a2_execution_session.py \
  tests/test_a2_strategy.py \
  tests/test_a2_risk.py \
  tests/test_a2_authority.py \
  tests/test_a2_controlled_campaign.py \
  tests/test_a2_property_stateful.py \
  tests/test_a2_metamorphic.py \
  tests/test_a2_chaos.py \
  tests/test_a2_replay.py \
  tests/test_a2_operator.py \
  tests/test_a2_hidden_acceptance.py
python scripts/a2_trader_mutation_gate.py --output /tmp/a2-mutation-receipt.json
python -m scripts.verify_a2_hidden_acceptance --help
```

Also require the public exact-head A2 assurance, five-run LEAN clean determinism, and five-run multi-session clean determinism workflows to be green. Any failure blocks the seal without consuming use 1.

## Private synthetic runner tests before real use

At minimum prove fail-closed behavior for credential/network isolation, read-only mounts, altered candidate bytes, altered seal commitment, wrong LEAN pin, wrong public evaluation SHA, wrong scorecard, use budget/reuse, one-shot writer, extra/leaking receipt fields, non-finite/duplicate/unapproved aggregate metrics, crash before/after commit, and public-verifier round-trip. Retained stdout/stderr/artifacts must remain aggregate-only.

## One real sealed run

Only after all public and synthetic preconditions pass: validate seal commitment/use budget; atomically claim use 1; execute the full registered private A2 corpus exactly once; aggregate internally; commit one receipt; export only the canonical public SealRecord, aggregate receipt, and non-secret package/hash identities. Do not automatically rerun a failure or invalid result.

Public verifier command:

```bash
python -m scripts.verify_a2_hidden_acceptance \
  --seal-record /path/to/a2-seal-record.json \
  --safe-receipt /path/to/a2-safe-receipt.json \
  --candidate-artifact-hash '<frozen 64-hex sha256>' \
  --public-eval-sha '<frozen 40-hex git SHA>'
```

## Allowed return to the public project

```text
A2 hidden runner: COMPLETE | BLOCKED
public_eval_sha: <frozen public SHA>
candidate_artifact_hash: <sha256 or NONE>
scorer_package_hash: <sha256 or NONE>
evaluator_hash/revision: <aggregate-safe identity or NONE>
sealed_bundle_hash: <sha256 or NONE>
seal_record: <public aggregate JSON or NONE>
safe_acceptance_receipt: <public aggregate JSON or NONE>
public_verifier: PASS | FAIL_CLOSED | NOT_RUN
seal_use_consumed: YES | NO
notes: <aggregate-only; no hidden details>
```

A passing hidden receipt still does **not** authorize unattended paper. The public project must recheck every conjunctive A2 gate and then obtain a separate explicit human `HITL_PROMOTION` before durable authority can move from `NONE` to `PAPER`.
