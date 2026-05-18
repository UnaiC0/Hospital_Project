from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.db import schema


class FakeSession:
    def __init__(self, fail_times: int = 0):
        self.fail_times = fail_times
        self.attempts = 0

    def transaction(self):
        return self

    def __enter__(self):
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise RuntimeError("simulated")
        return self.cursor

    def __exit__(self, *args):
        return None

    cursor = MagicMock()


def test_initialize_schema_executes_ddl():
    session = FakeSession()
    schema.initialize_schema(session)
    session.cursor.execute.assert_called_once()
    sql = session.cursor.execute.call_args.args[0]
    assert "CREATE TABLE IF NOT EXISTS triage_records" in sql
    assert "CREATE TABLE IF NOT EXISTS radiology_studies" in sql
    assert "CREATE TABLE IF NOT EXISTS quality_events" in sql
    assert "CREATE TABLE IF NOT EXISTS pipeline_runs" in sql


def test_initialize_with_retry_succeeds_after_failures(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr(schema.time, "sleep", lambda s: sleeps.append(s))
    session = FakeSession(fail_times=2)
    schema.initialize_schema_with_retry(session, attempts=5, delay_seconds=0.01)
    assert session.attempts == 3
    assert sleeps == [0.01, 0.01]


def test_initialize_with_retry_raises_after_exhausting(monkeypatch):
    monkeypatch.setattr(schema.time, "sleep", lambda s: None)
    session = FakeSession(fail_times=99)
    with pytest.raises(RuntimeError, match="PostgreSQL schema initialization failed"):
        schema.initialize_schema_with_retry(session, attempts=3, delay_seconds=0.01)
    assert session.attempts == 3
