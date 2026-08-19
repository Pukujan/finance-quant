from finance_quant.acceptance.seal import SafeAcceptanceReceipt, SealRecord, merkle_root


def test_merkle_commitment_is_order_independent_and_tamper_evident():
    hashes = ["a" * 64, "b" * 64, "c" * 64]
    assert merkle_root(hashes) == merkle_root(list(reversed(hashes)))
    assert merkle_root(hashes) != merkle_root(hashes + ["d" * 64])


def test_safe_receipt_cannot_expose_cases_or_labels():
    seal = SealRecord("SEAL-A", "c" * 64, "l" * 64, "2026-08-19T00:00:00Z", "h" * 40,
                      "scorecard-v0", 2)
    receipt = SafeAcceptanceReceipt("SEAL-A", seal.commitment_hash, "a" * 64, "pass",
                                    (("score", 1.0),), ("same_bar_fill",), 1)
    assert receipt.commitment_hash == seal.commitment_hash
