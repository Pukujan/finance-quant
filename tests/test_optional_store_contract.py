"""Shared contract tests for optional PIT store adapters.

Exercises TimescalePITStore, XTDBPITStore, and ArcticPITStore through a common
interface.  Tests run only when the module is importable **and** the caller
passes ``--run-optional-stores`` or sets ``FQ_TEST_OPTIONAL_STORES=1``.

When a real backend is not available the tests use mocks/stubs so that the
contract surface (method names, signatures, return types) is still validated.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from finance_quant.pit.fixtures import generate
from finance_quant.pit.store import MemoryGoldStore

pytestmark = pytest.mark.optional_store


def _try_import_timescale():
    try:
        from finance_quant.pit.timescale import TimescalePITStore
        return TimescalePITStore
    except ImportError:
        return None


def _try_import_xtdb():
    try:
        from finance_quant.pit.xtdb import XTDBPITStore
        return XTDBPITStore
    except ImportError:
        return None


def _try_import_arctic():
    try:
        from finance_quant.pit.arctic import ArcticPITStore
        return ArcticPITStore
    except ImportError:
        return None


STORE_METHODS = {"put", "as_of", "revisions_between", "snapshot_pin"}


def _assert_has_methods(cls, methods):
    for m in methods:
        assert hasattr(cls, m), f"{cls.__name__} missing method '{m}'"


class _MockPsycopgConn:
    def __init__(self):
        self._rows: list[tuple] = []

    def execute(self, sql, params=None):
        result = MagicMock()
        if "CREATE TABLE" in sql.upper():
            result.fetchall.return_value = []
            return result
        if "INSERT" in sql.upper():
            if params is not None:
                self._rows.append(params)
            result.fetchall.return_value = []
            return result
        if "SELECT" in sql.upper():
            result.fetchall.return_value = list(self._rows)
            return result
        result.fetchall.return_value = []
        return result

    def close(self):
        pass


class TestTimescaleImport:
    def test_module_importable(self):
        cls = _try_import_timescale()
        assert cls is not None, "finance_quant.pit.timescale not importable"

    def test_has_contract_methods(self):
        cls = _try_import_timescale()
        if cls is None:
            pytest.skip("timescale not importable")
        _assert_has_methods(cls, STORE_METHODS)


class TestXTDBImport:
    def test_module_importable(self):
        cls = _try_import_xtdb()
        assert cls is not None, "finance_quant.pit.xtdb not importable"

    def test_has_contract_methods(self):
        cls = _try_import_xtdb()
        if cls is None:
            pytest.skip("xtdb not importable")
        _assert_has_methods(cls, STORE_METHODS)


class TestArcticImport:
    def test_module_importable(self):
        cls = _try_import_arctic()
        assert cls is not None, "finance_quant.pit.arctic not importable"

    def test_has_contract_methods(self):
        cls = _try_import_arctic()
        if cls is None:
            pytest.skip("arctic not importable")
        _assert_has_methods(cls, STORE_METHODS)


class TestTimescaleMockContract:
    TimescalePITStore = _try_import_timescale()

    @pytest.fixture(autouse=True)
    def _patch_connect(self):
        if self.TimescalePITStore is None:
            pytest.skip("timescale not importable")
        self.mock_conn = _MockPsycopgConn()
        with patch("psycopg.connect", return_value=self.mock_conn):
            yield

    def test_put_and_snapshot_pin(self):
        if self.TimescalePITStore is None:
            pytest.skip("timescale not importable")
        store = self.TimescalePITStore("mock://dsn")
        store._conn = self.mock_conn
        try:
            for r in generate()[:10]:
                store.put(r)
            pin = store.snapshot_pin()
            assert isinstance(pin, str)
            assert len(pin) == 64
        finally:
            store.close()

    def test_as_of_returns_visible(self):
        if self.TimescalePITStore is None:
            pytest.skip("timescale not importable")
        store = self.TimescalePITStore("mock://dsn")
        store._conn = self.mock_conn
        gold = MemoryGoldStore()
        try:
            for r in generate()[:30]:
                store.put(r)
                gold.put(r)
            result = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-10", "2024-01-10")
            expected = gold.as_of("bar", ["AAA"], "2024-01-02", "2024-01-10", "2024-01-10")
            assert [r.canonical() for r in result] == [r.canonical() for r in expected]
        finally:
            store.close()

    def test_revisions_between(self):
        if self.TimescalePITStore is None:
            pytest.skip("timescale not importable")
        store = self.TimescalePITStore("mock://dsn")
        store._conn = self.mock_conn
        gold = MemoryGoldStore()
        try:
            for r in generate()[:20]:
                store.put(r)
                gold.put(r)
            result = store.revisions_between("2024-01-01", "2024-12-31")
            expected = gold.revisions_between("2024-01-01", "2024-12-31")
            assert len(result) == len(expected)
        finally:
            store.close()


class TestXTDBMockContract:
    XTDBPITStore = _try_import_xtdb()

    @pytest.fixture(autouse=True)
    def _patch_connect(self):
        if self.XTDBPITStore is None:
            pytest.skip("xtdb not importable")
        self.mock_conn = _MockPsycopgConn()
        with patch("psycopg.connect", return_value=self.mock_conn):
            yield

    def test_put_and_snapshot_pin(self):
        if self.XTDBPITStore is None:
            pytest.skip("xtdb not importable")
        store = self.XTDBPITStore("mock://dsn")
        store._conn = self.mock_conn
        try:
            for r in generate()[:10]:
                store.put(r)
            pin = store.snapshot_pin()
            assert isinstance(pin, str)
            assert len(pin) == 64
        finally:
            store.close()

    def test_as_of_matches_gold(self):
        if self.XTDBPITStore is None:
            pytest.skip("xtdb not importable")
        store = self.XTDBPITStore("mock://dsn")
        store._conn = self.mock_conn
        gold = MemoryGoldStore()
        try:
            for r in generate()[:30]:
                store.put(r)
                gold.put(r)
            result = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-10", "2024-01-10")
            expected = gold.as_of("bar", ["AAA"], "2024-01-02", "2024-01-10", "2024-01-10")
            assert [r.canonical() for r in result] == [r.canonical() for r in expected]
        finally:
            store.close()

    def test_revisions_between(self):
        if self.XTDBPITStore is None:
            pytest.skip("xtdb not importable")
        store = self.XTDBPITStore("mock://dsn")
        store._conn = self.mock_conn
        gold = MemoryGoldStore()
        try:
            for r in generate()[:20]:
                store.put(r)
                gold.put(r)
            result = store.revisions_between("2024-01-01", "2024-12-31")
            expected = gold.revisions_between("2024-01-01", "2024-12-31")
            assert len(result) == len(expected)
        finally:
            store.close()


class TestArcticMockContract:
    ArcticPITStore = _try_import_arctic()

    @pytest.fixture(autouse=True)
    def _skip_if_unavailable(self):
        if self.ArcticPITStore is None:
            pytest.skip("arctic not importable")

    def test_put_and_snapshot_pin(self, tmp_path):
        if self.ArcticPITStore is None:
            pytest.skip("arctic not importable")
        store = self.ArcticPITStore(uri=f"lmdb://{tmp_path / 'adb'}")
        for r in generate()[:10]:
            store.put(r)
        pin = store.snapshot_pin()
        assert isinstance(pin, str)
        assert len(pin) == 64
        store.close()

    def test_as_of_matches_gold(self, tmp_path):
        if self.ArcticPITStore is None:
            pytest.skip("arctic not importable")
        store = self.ArcticPITStore(uri=f"lmdb://{tmp_path / 'adb'}")
        gold = MemoryGoldStore()
        for r in generate()[:30]:
            store.put(r)
            gold.put(r)
        result = store.as_of("bar", ["AAA"], "2024-01-02", "2024-01-10", "2024-01-10")
        expected = gold.as_of("bar", ["AAA"], "2024-01-02", "2024-01-10", "2024-01-10")
        assert [r.canonical() for r in result] == [r.canonical() for r in expected]

    def test_revisions_between(self, tmp_path):
        if self.ArcticPITStore is None:
            pytest.skip("arctic not importable")
        store = self.ArcticPITStore(uri=f"lmdb://{tmp_path / 'adb'}")
        gold = MemoryGoldStore()
        for r in generate()[:20]:
            store.put(r)
            gold.put(r)
        result = store.revisions_between("2024-01-01", "2024-12-31")
        expected = gold.revisions_between("2024-01-01", "2024-12-31")
        assert len(result) == len(expected)


class TestDumpRecordsContract:
    def test_memory_gold_dump_records(self):
        gold = MemoryGoldStore()
        for r in generate()[:5]:
            gold.put(r)
        dump = gold.dump_records()
        assert len(dump) == 5
        first = dump[0]
        for key in ("namespace", "instrument_id", "vt", "kt", "payload",
                     "source", "revision", "ingest_run_id", "superseded_by"):
            assert key in first, f"dump_records missing key '{key}'"

    def test_sqlite_dump_records(self, tmp_path):
        from finance_quant.pit.store import SQLiteBitemporalStore
        store = SQLiteBitemporalStore(tmp_path / "test.db")
        gold = MemoryGoldStore()
        for r in generate()[:5]:
            store.put(r)
            gold.put(r)
        dump = store.dump_records()
        assert len(dump) == 5
        assert dump == gold.dump_records()
        store.close()
