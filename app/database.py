"""
SQLite database module.

DB_PATH is read from the DB_PATH environment variable at call time
(not at import time) so that tests can override it via monkeypatch.setenv.
"""
import os
import sqlite3

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS expenses (
    id          TEXT PRIMARY KEY NOT NULL,
    amount      TEXT NOT NULL,
    category    TEXT NOT NULL,
    date        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
)
"""


def get_db_path() -> str:
    """Return the database file path from the environment (DR-009)."""
    return os.environ.get("DB_PATH", "./expenses.db")


def get_connection() -> sqlite3.Connection:
    """
    Open a SQLite connection to the configured database path.
    WAL mode is enabled on every new connection (DR-010 / ACH-010).
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Create the expenses table if it does not already exist."""
    conn = get_connection()
    try:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()
