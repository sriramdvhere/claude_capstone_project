---
description: Test conventions that must be followed when reading or modifying any file under tests/ or conftest.py
paths:
  - "tests/**"
  - "conftest.py"
---

# Test Conventions

Read this file before touching any file under `tests/` or `conftest.py`.

---

## Test file responsibilities

| File | Layer under test | What is real | What is mocked |
|------|-----------------|--------------|----------------|
| `tests/test_validation.py` | `app/models.py` field validators | `ExpenseCreate` Pydantic model | Nothing |
| `tests/test_service.py` | `app/service.py` | `app.service.create_expense` | `app.repository.insert` |
| `tests/test_expenses_api.py` | `POST /expenses` HTTP layer | `FastAPI TestClient` + SQLite (temp file) | Repository only when testing error paths (503, 500) |

Tests must stay at their designated layer. Do not reach through a layer boundary (e.g., do not write an HTTP test that also directly calls `ExpenseCreate` to bypass routing, or a service test that opens a real DB connection).

---

## Naming

- Test functions: `test_<subject>_<condition>_<expected_result>` in snake_case.
- Helper factories: `make_<ModelName>(...)` at module level with fully-valid defaults.
- No abbreviations in names.

---

## Test isolation

- API tests must use the `test_client` fixture from `tests/conftest.py`. Do not redefine it.
- The `test_client` fixture points `DB_PATH` at a `tmp_path` file via `monkeypatch.setenv`. Each test gets a fresh database automatically.
- Service tests must mock `app.repository.insert` using `patch("app.repository.insert")`. Use `side_effect = lambda r: r` for the happy path so the mock echoes back the record it receives.
- Validation tests instantiate `ExpenseCreate` directly. No fixtures or mocks needed.

---

## Asserting validation errors

**In `test_validation.py`** (Pydantic level):
```python
with pytest.raises(ValidationError) as exc_info:
    ExpenseCreate(...)
messages = [e["msg"] for e in exc_info.value.errors()]
assert "exact string from requirements Section 8" in messages
```

**In `test_expenses_api.py`** (HTTP level):
```python
assert response.status_code == 400
assert "exact string from requirements Section 8" in response.json()["details"]
```

Error strings **must match `docs/requirements.md` Section 8 verbatim**. Do not paraphrase or approximate.

---

## HTTP response rules

- Validation failures are always HTTP 400, never 422. A test must never allow a 422 response to pass.
- Every 400 response body has shape `{"error": "Validation failed", "details": [...]}`.
- Every 500/503 response body has shape `{"error": "...", "details": [...]}`.
- Assert both `status_code` and `response.json()` keys in the same test when testing error shape.

---

## Section structure inside test files

Group tests with labelled separator comments that reference the requirement being exercised:

```python
# ---------------------------------------------------------------------------
# AC-001 — Happy path
# ---------------------------------------------------------------------------
```

Use requirement IDs (AC-xxx, FR-xxx, DR-xxx, NFR-xxx) in section headings so coverage can be traced back to `docs/requirements.md`.

---

## Mock discipline

- Mock at the layer boundary, not inside it. For service tests, patch `app.repository.insert` — never internal sqlite3 calls.
- For HTTP-layer DB failure tests, patch `app.repository.insert` with `side_effect=DBUnavailableError(...)` or `side_effect=DBError(...)`. Import these from `app.repository`.
- Use `unittest.mock.patch` as a context manager, not as a decorator.

---

## What not to do

- Do not use `monkeypatch` in individual test functions to override `DB_PATH`; that is the `test_client` fixture's responsibility.
- Do not use `@pytest.mark.parametrize`. Write explicit named tests instead so failures identify the exact scenario.
- Do not write tests that assert only on `status_code` without also asserting the response body for error cases.
- Do not import `sqlite3` in test files; the repository and database modules own that boundary.
