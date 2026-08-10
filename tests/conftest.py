"""
Shared pytest fixtures for the Expense Tracker test suite.

The test_client fixture:
  1. Points DB_PATH at a temporary file (isolated from the dev database).
  2. Enters the TestClient context, which triggers the FastAPI lifespan
     startup and runs init_db() against the temp file.
  3. Yields the client for use in tests.
  4. monkeypatch automatically restores DB_PATH after each test.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client(tmp_path, monkeypatch):
    """FastAPI TestClient backed by an isolated per-test SQLite database."""
    db_file = tmp_path / "test_expenses.db"
    monkeypatch.setenv("DB_PATH", str(db_file))

    # Enter the context so lifespan startup (init_db) runs against the temp DB.
    with TestClient(app) as client:
        yield client
