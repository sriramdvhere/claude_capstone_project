# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (create and activate a virtualenv first)
pip install -r requirements.txt

# Run the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run all tests
pytest

# Run a single test file
pytest tests/test_expenses_api.py

# Run a single test by name
pytest tests/test_expenses_api.py::test_create_valid_expense_returns_201
```

The database file path defaults to `./expenses.db` and is controlled by the `DB_PATH` environment variable.

## Architecture

**Layered Modular Monolith** — four strict layers that communicate only with the layer directly below:

```
HTTP Client
    └── API Router       app/main.py          (FastAPI route handler + middleware)
          └── Validation app/models.py         (Pydantic field validators)
                └── Service  app/service.py    (use-case orchestrator, UUID generation)
                      └── Repository app/repository.py  (SQLite data access)
                                └── SQLite     app/database.py
```

### Layer responsibilities

- **`app/models.py`** — Three Pydantic models: `ExpenseCreate` (inbound), `ExpenseRecord` (domain/DB entity), `ExpenseResponse` (API response). All business-rule validation lives here via `@field_validator`. Uses `PydanticCustomError` so the exact requirement error strings reach the response without Pydantic's "Value error, " prefix.

- **`app/service.py`** — Single function `create_expense()`. Generates a UUID v4, constructs an `ExpenseRecord`, and delegates to the repository. Propagates `DBError` / `DBUnavailableError` to the caller without catching them.

- **`app/repository.py`** — `insert()` wraps every SQLite write in an explicit transaction. Maps `sqlite3.OperationalError` → `DBUnavailableError` (HTTP 503) and all other `sqlite3.Error` → `DBError` (HTTP 500). `amount` is stored as `TEXT` to avoid floating-point precision loss.

- **`app/database.py`** — `DB_PATH` is read from the environment at call time (not import time) so tests can override it with `monkeypatch.setenv`. WAL mode is enabled on every new connection.

- **`app/errors.py`** — Overrides FastAPI's default 422 handler. All Pydantic / FastAPI validation errors return HTTP 400. A completely absent request body returns 400 with `"Request body is required"`.

- **`app/main.py`** — Wires middleware in this order (last-added is outermost): `RequestLoggerMiddleware` → `MaxBodySizeMiddleware` → route handler. Body size limit is 10 KB enforced via `Content-Length`. The lifespan runs `init_db()` on startup.

### Error response shape

All error responses share one envelope:
```json
{"error": "...", "details": ["<message>", ...]}
```

### Testing

Tests use `FastAPI TestClient` with a per-test isolated SQLite file via the `test_client` fixture in `tests/conftest.py`. The fixture sets `DB_PATH` to a `tmp_path` file via `monkeypatch.setenv` and triggers `init_db()` through the FastAPI lifespan.

## Docs and rules

- Requirements: `docs/requirements.md` — source of truth for validation rules and error strings.
- Architecture: `docs/architecture.md`
- Agent rules: `.claude/rules/` — structure instructions for requirements, architecture, design review, implementation plans, and peer code reviews.

## Hooks

A `PostToolUse` hook runs `.claude/hooks/log-file-changes.py` after every `Write` or `Edit` tool call. This is defined in `.claude/settings.json`.
