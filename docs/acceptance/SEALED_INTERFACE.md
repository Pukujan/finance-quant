# Sealed Acceptance Interface

Issue #9's exact cases and labels live only in private `Pukujan/finance-quant-holdout`.
The public project records only `SealRecord` commitments and `SafeAcceptanceReceipt`
aggregates, implemented in `finance_quant.acceptance.seal`.

Clean-runner requirements:

1. Mount one sealed case set read-only, the candidate artifact read-only, and the
   reference interpreter image.
2. Carry no provider, brokerage, MLflow, GitHub, or general network credentials.
3. Validate the case Merkle root and labels hash against the public `SealRecord` before
   executing any candidate.
4. Emit exactly one safe aggregate receipt through the one-shot result writer.
5. Enforce use counters: `SEAL-A` max two per epoch; `SEAL-B` exactly one.

The current host's coarse `gh` PAT can read private repositories; it is not a valid
clean runner identity. Use a fine-grained credential excluding the holdout repository,
or a separate IAM-scoped object store identity, before real cases are populated.

## A1 opaque hidden-acceptance ingress

Issue #15 / assurance phase A1 reuses the same authority boundary. Ordinary agents and
public CI must never checkout, search, print, upload, or otherwise inspect the private
execution cases or labels. The authorized clean runner may emit only a public
`SealRecord` plus one aggregate-only `SafeAcceptanceReceipt`.

The public verifier is `finance_quant.acceptance.a1_hidden`. It fails closed unless:

- the seal and receipt use their exact public schemas with no extra fields;
- the receipt `case_set_id` and commitment hash match the public seal record;
- the receipt candidate artifact hash exactly matches the public artifact expected by
  the evaluation request;
- the seal use budget permits the reported use number;
- the hidden status is `pass`; and
- a passing receipt contains no failure classes.

`.github/workflows/a1-hidden-acceptance.yml` is a manual **receipt-ingress verifier**, not
a sealed-case runner. It accepts only the public seal JSON, aggregate receipt JSON, and
candidate artifact hash, then invokes the fail-closed verifier. It has no reason or
permission to access the holdout repository and cannot by itself satisfy
`HIDDEN_ACCEPTANCE`.

A1 hidden acceptance is complete only when an authorized external clean runner executes
the sealed corpus without exposing its cases/labels and the resulting aggregate receipt
passes this public verifier for the exact candidate artifact under evaluation. Public
fixtures, synthetic hidden cases, or a locally fabricated receipt are not substitutes.
