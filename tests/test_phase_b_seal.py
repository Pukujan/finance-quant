import pytest

from finance_quant.acceptance.phase_b_seal import (
    SealEpochError,
    SealRecord,
    SealType,
    SealValidationError,
    validate,
)


def make_root(n: int = 0) -> str:
    return f"{n:064x}"


def test_seal_record_valid():
    record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
    assert record.merkle_root == make_root(1)


def test_seal_record_bad_root_length():
    with pytest.raises(ValueError):
        SealRecord(merkle_root="short", epoch=1, seal_type=SealType.SEAL_A)


def test_validate_root_match():
    root = make_root(1)
    record = SealRecord(merkle_root=root, epoch=1, seal_type=SealType.SEAL_A)
    assert validate(root, record) is record


def test_validate_root_mismatch():
    record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
    with pytest.raises(SealValidationError):
        validate(make_root(2), record)


def test_seal_a_max_two_per_epoch():
    registry = {1: {SealType.SEAL_A: 2}}
    record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
    with pytest.raises(SealEpochError):
        validate(make_root(1), record, registry)


def test_seal_b_exactly_one_per_epoch():
    registry = {1: {SealType.SEAL_B: 1}}
    record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B)
    with pytest.raises(SealEpochError):
        validate(make_root(1), record, registry)


def test_seal_b_zero_is_error():
    registry = {}
    record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_B, count_in_epoch=2)
    with pytest.raises(SealEpochError):
        validate(make_root(1), record, registry)


def test_seal_a_under_limit_ok():
    registry = {1: {SealType.SEAL_A: 1}}
    record = SealRecord(merkle_root=make_root(1), epoch=1, seal_type=SealType.SEAL_A)
    assert validate(make_root(1), record, registry) is record
