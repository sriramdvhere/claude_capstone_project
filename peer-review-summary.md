# Peer Code Review Summary

## 1. Review Metadata
- **Scope**: Local unpushed commits on `feature/US-001-add-expense` (6 commits ahead of `main`)
- **Requirements Baseline**: `docs/requirements.md`
- **Review Status**: Completed
- **Overall Recommendation**: Ready for PR with Minor Fixes
- **Last Updated**: 10 Aug 2026

---

## 2. Change Scope

### Files Reviewed
- `app/database.py`
- `app/errors.py`
- `app/main.py`
- `app/models.py`
- `app/repository.py`
- `app/service.py`
- `tests/conftest.py`
- `tests/test_expenses_api.py`
- `tests/test_service.py`
- `tests/test_validation.py`
- `requirements.txt`

### Checks Run
- `python -m pytest tests/ -v --tb=short` — **75 / 75 tests passed** (5.32 s, Python 3.13.0, pytest 8.3.5)
- Dependency version review against known CVE databases — no known critical or high vulnerabilities found for the pinned lower bounds in `requirements.txt` (fastapi ≥ 0.110.0, pydantic ≥ 2.0.0, uvicorn ≥ 0.27.0, httpx ≥ 0.24.0, pytest ≥ 7.0.0)

---

## 3. Findings Register

| ID | Severity | Area | File / Symbol | Observation | Recommendation |
|----|----------|------|---------------|-------------|----------------|
| PCR-001 | High | Error Handling | `app/repository.py — insert` | `get_connection()` is invoked **before** the `try/except` block. If `sqlite3.connect()` or the `PRAGMA journal_mode=WAL` call raises `sqlite3.OperationalError` (e.g., DB directory missing, file-permission error), the exception propagates as a raw `sqlite3.OperationalError` to `main.py`. The endpoint only catches `DBUnavailableError` and `DBError`, so the raw exception reaches FastAPI's default unhandled-exception path and returns an unstructured response — violating NFR-002 (structured error on persistence failure) and NFR-006 (consistent JSON error shape). | Move `conn = get_connection()` inside the `try` block. `sqlite3.OperationalError` from the connection phase will then be caught by the existing `except sqlite3.OperationalError` handler and re-raised as `DBUnavailableError`, returning a well-formed HTTP 503 response. |
| PCR-002 | Low | Correctness | `app/models.py — validate_date` | `datetime.strptime(v, "%Y-%m-%d")` accepts non-zero-padded values such as `"2026-2-1"` because Python's `%m` and `%d` directives do not require two digits. Requirements FR-007 and Section 8 specify the strict `YYYY-MM-DD` format (implying zero-padded month and day). No test covers this input. | Add a `re.fullmatch(r'\d{4}-\d{2}-\d{2}', v)` pre-check before the `strptime` call and raise `PydanticCustomError("date_invalid_format", "date must be in YYYY-MM-DD format")` if the pattern does not match. Add a corresponding test for `"2026-2-1"`. |
| PCR-003 | Low | Security | `app/main.py — MaxBodySizeMiddleware` | Body-size enforcement relies exclusively on the `Content-Length` request header. A client using HTTP chunked transfer encoding (which omits `Content-Length`) bypasses this check entirely and can send an arbitrarily large body, partially undermining NFR-004. This is a documented design trade-off (impl-plan OQ-2). | Document the residual risk explicitly in the module docstring. For future hardening, consider reading the raw request body stream up to the byte limit and short-circuiting instead of relying on the header alone. No code change required before PR unless the team treats this as a blocker. |
| PCR-004 | Low | Test Coverage | `tests/test_expenses_api.py` | No integration test asserts the specific error message when `amount` is entirely absent from the JSON body (distinct from `amount: null`, `amount: 0`, or `amount: "abc"`). The `errors.py` handler maps the Pydantic `missing` error for `amount` to `"amount is required"`, but no HTTP-level test verifies this message string. `test_no_422_for_missing_fields` sends `{}` and checks only the status code. | Add a test: POST `{"category": "Food", "date": "2026-07-22"}` (no `amount` key) and assert `response.status_code == 400` and `"amount is required" in response.json()["details"]`. |
| PCR-005 | Low | Dependency Safety | `requirements.txt` | All five packages specify open-ended lower-bound versions with no upper bound (e.g., `fastapi>=0.110.0`, `pydantic>=2.0.0`). Future automated installs could pull in a major-version release with breaking changes, leading to unexpected CI failures. | Pin each package to a compatible range (e.g., `fastapi>=0.110.0,<1.0.0`) or generate a lock file (`pip freeze > requirements-lock.txt`) to ensure reproducible builds across environments. |

---

## 4. Coverage and Risk Notes

- **Happy path coverage**: adequate — `test_create_valid_expense_returns_201`, `test_create_valid_expense_response_contains_all_fields`, and related tests exercise the full successful path from HTTP request to DB insert and response serialisation.
- **Edge case coverage**: adequate — validators are exercised at both the model level (`test_validation.py`) and the HTTP level (`test_expenses_api.py`) for zero/negative/non-numeric amounts, blank/whitespace/overlong category, absent/malformed/impossible-calendar dates, overlong description, missing body, and multiple simultaneous missing fields. One gap exists (see PCR-004): missing `amount` field at the HTTP level is not asserted on the error message.
- **Error handling notes**: The `DBUnavailableError` / `DBError` abstraction is well-designed and correctly wired at the endpoint level. The single gap (PCR-001) is that `get_connection()` sits outside the `try` block in `repository.insert`, meaning a connection-time `sqlite3.OperationalError` escapes as an unwrapped raw exception. All other error paths (validation failures, 503, 500, 413) are correctly handled and tested.
- **Security notes**: No secrets, credentials, or sensitive values are present in source or test files. SQL injection is prevented via parameterized queries (SQLite `?` placeholders) throughout `repository.py`. Input sanitisation is performed at the Pydantic model boundary before any persistence occurs. MaxBodySizeMiddleware provides partial payload-flood protection (PCR-003). No authentication or authorisation is required for the MVP scope per NFR-004 and assumption A-04.
- **Dependency safety notes**: No known critical or high CVEs found for fastapi ≥ 0.110.0, pydantic ≥ 2.0.0, uvicorn ≥ 0.27.0, httpx ≥ 0.24.0, or pytest ≥ 7.0.0 as of the review date. The absence of upper-bound version pins is flagged as a low-severity stability risk (PCR-005) rather than a security issue.

---

## 5. Final Recommendation

- **Outcome**: Ready for PR with Minor Fixes
- **Required fixes before PR**:
  - PCR-001 — Move `conn = get_connection()` inside the `try` block in `app/repository.py — insert` so that connection-time `sqlite3.OperationalError` is caught and wrapped as `DBUnavailableError`, returning a structured HTTP 503 response.
- **Optional improvements**:
  - PCR-002 — Add regex pre-check in `validate_date` to reject non-zero-padded dates such as `"2026-2-1"` and add a corresponding test.
  - PCR-003 — Document the chunked-transfer-encoding bypass risk in `MaxBodySizeMiddleware`; plan body-stream limiting for post-MVP hardening.
  - PCR-004 — Add an integration test asserting `"amount is required"` when `amount` is absent from the request body.
  - PCR-005 — Add upper-bound version constraints to `requirements.txt` or introduce a lock file for reproducible builds.
