from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import PostgresSettings, get_settings


DEFAULT_POOL_MIN_SIZE = 2
DEFAULT_POOL_MAX_SIZE = 10


class DatabaseSession:
    """Owns a Postgres connection pool. Single source of truth for connection
    management — repositories never construct connections themselves.

    The pool is created closed so wiring is cheap; lifespan opens it explicitly.
    """

    def __init__(
        self,
        settings: PostgresSettings,
        min_size: int = DEFAULT_POOL_MIN_SIZE,
        max_size: int = DEFAULT_POOL_MAX_SIZE,
    ):
        self._settings = settings
        self._pool = ConnectionPool(
            conninfo=self._conninfo(),
            min_size=min_size,
            max_size=max_size,
            kwargs={"row_factory": dict_row},
            open=False,
        )

    def _conninfo(self) -> str:
        return (
            f"host={self._settings.host} "
            f"port={self._settings.port} "
            f"user={self._settings.user} "
            f"password={self._settings.password} "
            f"dbname={self._settings.database} "
            f"connect_timeout={self._settings.connect_timeout_seconds}"
        )

    def open(self) -> None:
        self._pool.open()
        self._pool.wait()

    def close(self) -> None:
        self._pool.close()

    @contextmanager
    def transaction(self) -> Iterator[psycopg.Cursor]:
        """Unit of Work bound to a pooled connection. Commits on success,
        rolls back on exception. All repository calls inside this block share
        the same transaction (ACID across multi-row writes)."""
        with self._pool.connection() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    yield cursor

    @contextmanager
    def read_cursor(self) -> Iterator[psycopg.Cursor]:
        """Read-only cursor. No explicit transaction — the pooled connection
        is returned cleanly after use."""
        with self._pool.connection() as connection:
            with connection.cursor() as cursor:
                yield cursor


def build_database_session() -> DatabaseSession:
    return DatabaseSession(get_settings().postgres)
