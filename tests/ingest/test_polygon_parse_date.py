"""Mutation-targeted tests for ``finance_quant.ingest.polygon._parse_date``.

Each test pins a specific branch/operation in ``_parse_date`` so that a
mutated copy of the function is caught.

Mutant map (function body, see ``polygon.py``):

    if isinstance(value, (int, float)):          # M1: drop ``float``
        return _to_utc_ms(int(value))            # M2: drop ``int(...)``
    if isinstance(value, str):
        if value.isdigit():                      # M3: drop branch / flip to else
            return _to_utc_ms(int(value))        # M4: drop ``int(...)``
        if "T" in value:                         # M5: drop / flip
            return datetime.fromisoformat(
                value.replace("Z", "+00:00"))    # M6: drop the .replace(...)
        return datetime.fromisoformat(value)\
            .replace(tzinfo=timezone.utc)        # M7: drop the .replace(...)
    raise ValueError(f"unsupported date value: ...")  # M8: drop the raise
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from finance_quant.ingest.polygon import _parse_date


UTC = timezone.utc
IST = timezone(timedelta(hours=5, minutes=30))


def test_epoch_millis_int_returns_utc_datetime() -> None:
    """M1/M2: ``int`` epoch-millis must become a tz-aware UTC datetime via
    ``_to_utc_ms``. Killing this also kills M2 (no int() coercion) because
    a Python ``int`` would still work, but a ``float`` input in the next
    test covers M1+M2 together."""
    result = _parse_date(1704067200000)  # 2024-01-01T00:00:00Z
    assert result == datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
    assert result.tzinfo is UTC


def test_epoch_millis_float_returns_utc_datetime() -> None:
    """M1+M2: a ``float`` epoch-millis must be accepted (M1: drop ``float``
    from the isinstance tuple) and coerced via the int() call (M2).

    The function path is ``_to_utc_ms(int(value))`` which first truncates
    the float to a whole millisecond, then divides by 1000.0. We use a
    value whose truncated ms form is unambiguous and also assert the
    sub-millisecond is dropped, pinning the exact truncation behavior.
    """
    result = _parse_date(1704067200000.7)
    # 1704067200000.7 -> int -> 1704067200000 ms -> 2024-01-01T00:00:00Z
    expected = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
    assert result == expected
    assert result.tzinfo is UTC
    # If M2 (drop int()) were applied, fromtimestamp(1704067200000.7 / 1000.0)
    # would still produce the same datetime because the float / 1000 path
    # is identical in effect for these magnitudes; M1 (drop float) is
    # killed by the fact that a float input reaches this branch at all
    # rather than raising ValueError from the final ``raise``.


def test_epoch_millis_string_returns_utc_datetime() -> None:
    """M3/M4: an all-digit string must hit the ``isdigit`` branch and be
    converted to ms, not run through ``fromisoformat`` (which would raise)."""
    result = _parse_date("1704067200000")
    assert result == datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
    assert result.tzinfo is UTC


def test_iso_date_only_returns_utc_midnight() -> None:
    """M7: a bare date like ``"2024-01-02"`` must end up tz-aware at UTC
    midnight. A mutation that drops the ``.replace(tzinfo=timezone.utc)``
    leaves a naive datetime, which is not equal to the aware target."""
    result = _parse_date("2024-01-02")
    assert result == datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
    assert result.tzinfo is not None
    assert result.tzinfo == UTC


def test_iso_datetime_with_z_returns_utc_datetime() -> None:
    """M5/M6: a ``Z``-suffixed ISO datetime must take the ``T`` branch and
    produce the correct UTC instant.

    Note on M6 (``drop .replace("Z", "+00:00")``): on Python 3.11+,
    ``datetime.fromisoformat`` accepts ``Z`` natively, so the replace is a
    no-op on this interpreter and the two paths produce identical results.
    The assertion below is still correct; it just doesn't discriminate the
    two implementations on >=3.11. (On <=3.10 this assertion would catch
    the missing replace via the ValueError that ``fromisoformat`` raises on
    an unstripped ``Z``.)"""
    result = _parse_date("2024-01-02T00:00:00Z")
    assert result == datetime(2024, 1, 2, 0, 0, 0, tzinfo=UTC)
    assert result.utcoffset() == timedelta(0)


def test_iso_datetime_with_offset_preserves_offset() -> None:
    """M5: a non-Z offset string must also take the ``T`` branch. We assert
    the *parsed* tzinfo is preserved (the function does not normalize to
    UTC for the ``T`` branch) so this test pins the exact branch and
    output."""
    result = _parse_date("2024-01-02T05:30:00+05:30")
    assert result == datetime(2024, 1, 2, 5, 30, 0, tzinfo=IST)
    assert result.utcoffset() == timedelta(hours=5, minutes=30)


def test_invalid_string_raises_value_error() -> None:
    """A non-numeric, non-ISO string must raise ``ValueError`` from
    ``datetime.fromisoformat``."""
    with pytest.raises(ValueError):
        _parse_date("not-a-date")


def test_invalid_type_raises_value_error() -> None:
    """M8: any value that is not ``int``/``float``/``str`` must reach the
    explicit ``raise ValueError(...)``. Mutating the raise away (replacing
    it with ``pass`` or returning ``None``) would let these fall through
    and either return None or raise a different exception type.

    We cover four distinct unsupported types so the test fails on any of:
    - removing the raise (return None)
    - removing the raise and letting the implicit ``return`` happen
    - weakening the ValueError to a different exception
    """
    for bad in (None, [], {}, b"1704067200000", SimpleNamespace(t=0)):
        with pytest.raises(ValueError):
            _parse_date(bad)


def test_bool_is_treated_like_int() -> None:
    """``isinstance(True, int)`` is True in Python; document the behavior so
    a future "tighten the isinstance check" mutation is caught.

    This does not target a specific mutant — it is a behavior pin."""
    result = _parse_date(True)  # bool -> 1 -> epoch 1ms -> 1970-01-01T00:00:00.001Z
    assert result == datetime(1970, 1, 1, 0, 0, 0, 1000, tzinfo=UTC)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
