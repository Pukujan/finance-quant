# A1 Luna Authorized Hidden-Acceptance Runner Handoff

Issue: #15  
Assurance phase: A1  
Prepared from public durable head: `d2d0b24c8ac73e78759732839ae6a12a849b6750`  
Public evaluation code baseline: `4739392b15319bb209d657294834fed4cfb02d29`  
Pinned LEAN runtime commit: `185c691b89f28bd68e48d53c02147415134975f0`

## Mission

Implement and execute the authorized **private** A1 hidden-acceptance runner against the sealed corpus, then export only the public `SealRecord` and aggregate-only `SafeAcceptanceReceipt` required by `finance_quant.acceptance.a1_hidden`.

The runner is an assurance worker, not a promotion or trading authority. A passing receipt grants no paper/live authority by itself.

## Non-negotiable authority boundary

The private runner may read the sealed corpus only inside the authorized holdout environment. It must never copy, print, summarize, upload, commit, paste into chat, or otherwise expose exact hidden cases, labels, case IDs, payloads, expected fills, failure examples, or oracle internals to `Pukujan/finance-quant`, ordinary agent logs, GitHub Actions, or any public artifact.

Do **not** execute the sealed corpus under the standing coarse GitHub PAT. The actual scoring process must run in a clean executor/container with:

- sealed case set mounted read-only;
- candidate artifact mounted read-only;
- reference/runtime image or dependencies mounted read-only;
- no GitHub, provider, brokerage, MLflow, cloud-general, SSH-agent, or general network credentials;
- no writable mount back into the public repository;
- exactly one aggregate result writer.

Luna may implement private runner code in the authorized holdout workspace, but the real sealed execution must occur in the isolated credential-free scoring process above.

## Public contracts to treat as authoritative

Read these from the public evaluation baseline before implementing:

1. `AGENTS.md`
2. `docs/CURRENT_STATE.md`
3. GitHub issue #15
4. `contracts/assurance/capability-assurance-v1.json`
5. `docs/plans/A1_EXECUTION_RUNTIME_CONFORMANCE.md`
6. `contracts/execution/runtime-conformance-v1.json`
7. `docs/acceptance/SEALED_INTERFACE.md`
8. `finance_quant/acceptance/seal.py`
9. `finance_quant/acceptance/a1_hidden.py`
10. `finance_quant/acceptance/uses.py`
11. `tests/test_a1_hidden_acceptance.py`
12. `.github/workflows/a1-hidden-acceptance.yml`

If private holdout instructions conflict with these public authority/receipt constraints, stop and report the conflict without consuming a real seal use.

## Exact candidate artifact binding

Hidden acceptance must be bound to immutable public code, not to a branch name or working tree.

Use public evaluation code baseline:

```text
4739392b15319bb209d657294834fed4cfb02d29
```

Materialize the candidate source artifact deterministically from a clean clone of `Pukujan/finance-quant`:

```bash
PUBLIC_EVAL_SHA=4739392b15319bb209d657294834fed4cfb02d29
git status --porcelain --untracked-files=no | grep -q '^' && { echo 'working tree not clean' >&2; exit 2; } || true
git cat-file -e "${PUBLIC_EVAL_SHA}^{commit}"
git archive --format=tar --prefix=finance-quant/ "$PUBLIC_EVAL_SHA" > a1-public-candidate.tar
sha256sum a1-public-candidate.tar
```

The lowercase 64-hex SHA-256 of **those exact tar bytes** is `candidate_artifact_hash`. Mount the tar or its extracted immutable filesystem read-only in the scoring executor. Do not substitute the Git commit SHA for the SHA-256 artifact hash.

The scoring environment must also verify that the production LEAN dependency under test is exactly commit `185c691b89f28bd68e48d53c02147415134975f0`. Do not float or update the runtime during hidden acceptance.

If deterministic archive bytes cannot be reproduced independently from the same commit, stop before opening the sealed corpus and report `CANDIDATE_ARTIFACT_NONDETERMINISTIC`.

## Seal preparation and budget

Before any real case executes:

1. Locate the authorized A1 sealed set in `Pukujan/finance-quant-holdout` or its approved seal store.
2. Recompute the case Merkle root and labels hash privately.
3. Compare both to the public `SealRecord` fields.
4. Compute the public seal `commitment_hash` using the same canonical JSON semantics as `SealRecord.commitment_hash`.
5. Verify `use_number` is allowed by `max_uses` **before** execution.
6. Record the use atomically in the private ledger so crash/retry cannot silently consume an extra evaluation.

Do not spend a real seal use while developing the runner. All runner unit/integration work must use synthetic private fixtures. Consume the real sealed suite only after the synthetic test battery below is green.

## Required private runner tests before a real sealed run

Implement these tests in the private holdout/runner repository using only synthetic cases and labels:

1. **Credential isolation** — scoring process fails before case load if prohibited credential/environment variables or writable public-repo mounts are present.
2. **Network isolation** — scoring succeeds with network disabled and does not require network access after immutable inputs are staged.
3. **Seal commitment mismatch** — altered case bytes or labels cause `invalid`/fail-closed behavior before candidate execution.
4. **Artifact binding mismatch** — candidate bytes differing from the declared `candidate_artifact_hash` fail before case execution.
5. **Runtime pin mismatch** — any LEAN revision other than `185c691b89f28bd68e48d53c02147415134975f0` fails before case execution.
6. **Use-budget enforcement** — use `0`, use `> max_uses`, and a replayed already-consumed use all fail closed.
7. **One-shot result writer** — exactly one aggregate receipt can be committed; a second write/retry cannot overwrite or append another authoritative result.
8. **Exact receipt schema** — output contains exactly: `case_set_id`, `commitment_hash`, `candidate_artifact_hash`, `status`, `aggregate_metrics`, `failure_classes`, `use_number`.
9. **No leakage fields** — attempts to emit raw cases, labels, case IDs, payloads, expected values, stack-local fixture objects, or arbitrary extra fields are rejected.
10. **Aggregate metric safety** — metric names are unique/non-empty and values are finite numeric values; no per-case metric arrays are emitted.
11. **Pass/failure consistency** — `status=pass` requires empty `failure_classes`; failures use only pre-registered aggregate failure-class names.
12. **Crash before result commit** — leaves no authoritative receipt and cannot claim a pass.
13. **Crash after result commit** — preserves exactly the committed receipt; restart cannot generate a second authoritative receipt for the same use.
14. **Public verifier round-trip** — with synthetic seal/receipt files copied into a separate clean public checkout, the exact command below passes only for a matching passing receipt and fails closed for mismatched seal, candidate hash, use budget, status, extra fields, duplicate/non-finite metrics, or non-empty pass failures.
15. **Log/output redaction** — stdout, stderr, exceptions, test reports, and retained artifacts contain no synthetic raw case/label payloads; the production runner uses the same aggregate-only output path.

The public hidden classes are already specified by issue #15 and `runtime-conformance-v1.json`. The private suite must cover the registered A1 classes without exporting case counts or exact examples. Do not add new public hints derived from hidden failures.

## Public-side preflight commands

Run against the extracted public candidate before opening the sealed suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_a1_hidden_acceptance.py -q
python -m pytest tests/test_runtime_conformance.py -q
python -m scripts.verify_a1_hidden_acceptance --help
```

If a named public test path has moved, find the current public runtime-conformance test module from the pinned evaluation commit and run its full suite. Do not alter tests merely to continue the hidden run.

## Real sealed execution procedure

Only after the synthetic runner tests and public preflight are green:

1. Start a fresh isolated clean executor.
2. Verify there are no prohibited credentials and network is disabled.
3. Mount one sealed case set read-only.
4. Mount `a1-public-candidate.tar` or its immutable extracted tree read-only.
5. Mount the reference/runtime image and verify the LEAN pin.
6. Revalidate the seal commitments and artifact SHA-256.
7. Atomically claim the next permitted seal use.
8. Execute the full registered A1 hidden corpus once.
9. Aggregate results inside the clean executor.
10. Commit exactly one `SafeAcceptanceReceipt` through the one-shot writer.
11. Export only:
    - public `SealRecord` JSON;
    - aggregate-only `SafeAcceptanceReceipt` JSON;
    - the lowercase 64-hex `candidate_artifact_hash`.
12. Destroy the scoring container/workspace and any uncommitted case-level execution output.

## Required output schemas

`SealRecord` must contain exactly:

```json
{
  "case_set_id": "...",
  "case_merkle_root": "<64 lowercase hex>",
  "labels_hash": "<64 lowercase hex>",
  "sealed_at": "...",
  "eval_harness_sha": "...",
  "scorecard_ref": "...",
  "max_uses": 1
}
```

Use the actual authorized `max_uses`; do not change it to match this example.

`SafeAcceptanceReceipt` must contain exactly:

```json
{
  "case_set_id": "...",
  "commitment_hash": "<64 lowercase hex>",
  "candidate_artifact_hash": "<64 lowercase hex>",
  "status": "pass|fail|invalid",
  "aggregate_metrics": [["metric_name", 0.0]],
  "failure_classes": [],
  "use_number": 1
}
```

Do not add timestamps, case counts, per-case scores, fixture names, paths, labels, stack traces, or debug metadata to this public receipt.

## Public verifier round-trip

Before handing the aggregate evidence back, verify it in a clean checkout of the public evaluation baseline:

```bash
python -m scripts.verify_a1_hidden_acceptance \
  --seal-record /path/to/public-seal-record.json \
  --safe-receipt /path/to/safe-receipt.json \
  --candidate-artifact-hash '<64 lowercase hex>'
```

Expected success output is aggregate-only and retains `authority: NONE`. Any nonzero exit is a blocker; do not edit the public verifier or receipt to manufacture a pass.

The same three public values are then submitted to `.github/workflows/a1-hidden-acceptance.yml` via its manual inputs. That workflow is only the public receipt verifier and must never receive holdout credentials or sealed files.

## Failure protocol

If hidden acceptance returns `fail` or `invalid`:

- preserve only the aggregate receipt and authorized aggregate failure classes;
- do not disclose exact failed cases, values, labels, expected outputs, counts, or traces;
- do not rerun automatically;
- do not use the second seal use as an iterative debugger;
- return control to issue #15 with the unchanged public contract and the aggregate result.

If the runner itself is defective, fix it using synthetic fixtures first. A runner defect does not justify opening or printing sealed cases.

## Completion response to the public project

Return only these items:

```text
A1 hidden runner: COMPLETE | BLOCKED
public_eval_sha: 4739392b15319bb209d657294834fed4cfb02d29
candidate_artifact_hash: <sha256 or NONE>
seal_record: <aggregate public JSON or NONE>
safe_acceptance_receipt: <aggregate public JSON or NONE>
public_verifier: PASS | FAIL_CLOSED | NOT_RUN
notes: <aggregate-only operational note; no sealed details>
```

Do not select the runtime, close issue #15, begin issue #16, or enable any trading authority. The public project performs final conjunctive-gate verification and candidate disposition after receipt ingress.