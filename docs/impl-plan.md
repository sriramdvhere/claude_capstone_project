# Implementation Plan: Expense Tracker — US-001 Add Expense

## 1. Plan Metadata
- **Source**: `docs/architecture.md`
- **Status**: Draft
- **Last Updated**: 10 Aug 2026
- **Prepared By**: Implementation Planner Agent
- **Planning Horizon**: US-001 MVP — single sprint, single developer

---

## 2. Planning Assumptions and Constraints

- Architecture baseline is `docs/architecture.md` (Layered Modular Monolith: Router → Validation → Service → Repository).
- Design review findings DR-001, DR-002, and DR-003 are HIGH severity and are treated as mandatory implementation requirements, not optional improvements.
- Technology stack is fixed: Python 3.11+, FastAPI 0.110+, Pydantic v2, SQLite via `sqlite3` stdlib, uvicorn.
- `amount` is stored as `TEXT` in SQLite to preserve exact decimal representation (design review resolution of OQ-03, recorded as ACH-006 in `docs/design-review.md`).
- Database file path is read from a `DB_PATH` environment variable with a default of `./expenses.db` (design review resolution of OQ-01, recorded as ACH-009).
- SQLite WAL mode must be enabled at repository startup as a mandatory initialisation step (design review ACH-010).
- Maximum request body size is 10 KB (design review ACH-008).
- No authentication or authorisation is in scope for US-001 (NFR-004, A-04).
- A single developer executes tasks; tasks noted as parallelisable in Section 4 may be done concurrently where tooling permits.
- The `GET /health` liveness endpoint (OQ-02 in architecture) is explicitly out of scope for US-001.
- All seven exact error message strings from requirements Section 8 must be hard-coded in the Validation Layer. No Pydantic default messages may reach the caller.
- `pytest` is the test framework; tests must be runnable with `pytest` from the project root without additional arguments.

---

## 3. Dependency-Ordered Task List

| Order | Task ID | Task Name | Priority | Depends On | Outcome / Definition of Done | Status |
|------:|---------|-----------|----------|------------|-------------------------------|--------|
| 1 | IMP-001 | Project scaffolding and dependency setup | P0 | None | `app/` package directory and `tests/` directory created; `requirements.txt` lists `fastapi`, `uvicorn[standard]`, `pydantic`, and `pytest`; virtual environment activates without error; `python -m pytest --collect-only` returns no import errors | Ready |
| 2 | IMP-002 | SQLite database module and schema DDL | P0 | IMP-001 | `app/database.py` creates the database at the path from `DB_PATH` env var (default `./expenses.db`); `CREATE TABLE IF NOT EXISTS expenses` DDL defines: `id TEXT PRIMARY KEY NOT NULL`, `amount TEXT NOT NULL`, `category TEXT NOT NULL`, `date TEXT NOT NULL`, `description TEXT NOT NULL DEFAULT ''`; `PRAGMA journal_mode=WAL` is executed on every new connection | Blocked |
| 3 | IMP-003 | Define Pydantic domain models | P0 | IMP-001 | `app/models.py` defines `ExpenseCreate` (input, no `id`), `ExpenseRecord` (full entity including `id` as `UUID`), and `ExpenseResponse` (serialised output matching the FR-004 response shape); `amount` typed as `Decimal` in Python; `id` typed as `uuid.UUID` | Blocked |
| 4 | IMP-005 | Global Error Handler — DR-001 and DR-002 | P0 | IMP-001 | `app/errors.py` registers `@app.exception_handler(RequestValidationError)` that: (a) detects the missing-body case (error location is `body` with type `missing`) and returns HTTP 400 with `{"error": "Validation failed", "details": ["Request body is required"]}`; (b) all other Pydantic validation errors return HTTP 400 with `{"error": "Validation failed", "details": [...]}` using the custom messages from the Validation Layer; no HTTP 422 is returned to any caller under any input | Blocked |
| 5 | IMP-004 | Validation Layer with exact error messages — DR-003 | P1 | IMP-003 | `app/validation.py` (or Pydantic `@field_validator` decorators on `ExpenseCreate`) enforces all field constraints with the **exact** strings from requirements Section 8: `"amount must be greater than zero"` (amount zero or negative), `"amount must be a valid number"` (non-numeric amount), `"category is required"` (blank or whitespace-only), `"date is required"` (absent), `"date must be in YYYY-MM-DD format"` (invalid format), `"description must not exceed 500 characters"` (too long); whitespace-only `category` is rejected by calling `.strip()` before length check or using Pydantic v2 `strip_whitespace=True`; `category` max 100 characters enforced; `description` max 500 characters enforced | Blocked |
| 6 | IMP-006 | Expense Repository | P1 | IMP-002, IMP-003 | `app/repository.py` exposes `insert(record: ExpenseRecord) -> ExpenseRecord`; parameterised SQL (`?` placeholders) used for all queries (NFR-004); INSERT is wrapped in an explicit transaction; on success the transaction is committed and the persisted record is returned; on general SQLite failure a custom `DBError` is raised; on transient or operational failure a custom `DBUnavailableError` is raised; no raw `sqlite3` exception escapes the repository boundary; `amount` is serialised to `str` on INSERT and deserialised to `Decimal` on SELECT | Blocked |
| 7 | IMP-007 | Expense Service | P1 | IMP-004, IMP-006 | `app/service.py` exposes `create_expense(data: ExpenseCreate) -> ExpenseRecord`; generates a UUID v4 via `uuid.uuid4()` from the Python stdlib (FR-002); constructs an `ExpenseRecord`; calls `repository.insert`; returns the persisted record to the caller; propagates `DBError` and `DBUnavailableError` upward without swallowing them | Blocked |
| 8 | IMP-008 | API Router — POST /expenses | P1 | IMP-005, IMP-007 | `app/main.py` mounts the `POST /expenses` route; the `FastAPI()` instance is configured with a 10 KB maximum request body size (NFR-004); a valid request returns HTTP 201 with the `ExpenseResponse` JSON (FR-004); `DBError` is mapped to HTTP 500; `DBUnavailableError` is mapped to HTTP 503; no HTTP 422 appears for any input; the Global Error Handler from IMP-005 is registered on the same `app` instance | Blocked |
| 9 | IMP-009 | Request Logger middleware | P2 | IMP-001 | A FastAPI middleware registered in `app/main.py` logs every request with: ISO 8601 timestamp, HTTP method, path, response status code, and latency in milliseconds (NFR-008); validation failures (HTTP 400) are logged at `WARN` level; unhandled exceptions are logged at `ERROR` level with a full stack trace; Python `logging` module is used, not `print` statements; wire the middleware into `app/main.py` before IMP-011 runs | Blocked |
| 10 | IMP-010 | Unit tests for Validation Layer | P1 | IMP-004 | `tests/test_validation.py` covers: valid happy-path input accepted; `amount=0` raises `"amount must be greater than zero"`; `amount=-1` raises same; non-numeric `amount` (e.g., `"abc"`) raises `"amount must be a valid number"`; blank `category` (`""`) raises `"category is required"`; whitespace-only `category` (`"   "`) raises `"category is required"`; `category` exceeding 100 characters raises an error; absent `date` raises `"date is required"`; `date` in wrong format (e.g., `"22-07-2026"`) raises `"date must be in YYYY-MM-DD format"`; `description` exceeding 500 characters raises `"description must not exceed 500 characters"`; absent `description` is accepted and defaults to empty string | Blocked |
| 11 | IMP-011 | Integration tests for POST /expenses | P1 | IMP-008, IMP-009, IMP-010 | `tests/test_expenses_api.py` uses FastAPI `TestClient` with an isolated SQLite database (in-memory or temp-file via `DB_PATH` pytest fixture); tests cover: AC-001 (valid expense returns 201 with all fields including a UUID `id`); AC-002 (invalid or zero amount returns 400 with exact error string); AC-003 (missing mandatory fields returns 400 identifying absent fields); missing request body returns 400 with `"Request body is required"`; simulated DB failure returns 503; no test scenario produces an HTTP 422 response | Blocked |
| 12 | IMP-012 | Acceptance criteria verification and sign-off | P1 | IMP-011 | AC-001, AC-002, and AC-003 all pass when executed against a running `uvicorn` server; DR-001 verified — no HTTP 422 is returned for any input variation; DR-002 verified — missing body returns HTTP 400 with message `"Request body is required"` exactly; DR-003 verified — all error strings produced by the API match requirements Section 8 verbatim; project linting passes (`ruff` or `flake8`); no partial records exist in `expenses.db` after any failed request | Blocked |

---

## 4. Blocked Task Register

| Task ID | Blocked By | Why Blocked | Unblock Condition | Owner | Notes |
|---------|------------|-------------|-------------------|-------|-------|
| IMP-002 | IMP-001 | `app/database.py` must be placed inside the `app/` package, which does not exist until scaffolding is complete | IMP-001 complete; `app/` directory created | Developer | Can be worked in parallel with IMP-003 and IMP-005 once IMP-001 is done |
| IMP-003 | IMP-001 | Pydantic models belong in `app/models.py`; the package must exist before the module can be created | IMP-001 complete | Developer | Can be worked in parallel with IMP-002 and IMP-005 once IMP-001 is done |
| IMP-005 | IMP-001 | The `FastAPI()` app instance that receives the `@app.exception_handler` registration must be created in `app/main.py` first | IMP-001 complete; `app/main.py` with a `FastAPI()` instance initialised | Developer | HIGH finding DR-001 and DR-002 are addressed here; this task is on the critical path |
| IMP-004 | IMP-003 | Field validators decorate fields on `ExpenseCreate`; the model must be defined before validators can be attached | IMP-003 complete | Developer | HIGH finding DR-003 is addressed here; all seven exact error strings must be implemented in this task |
| IMP-006 | IMP-002, IMP-003 | The repository requires the `expenses` table to exist (IMP-002) and the `ExpenseRecord` model to be importable (IMP-003) | IMP-002 and IMP-003 both complete | Developer | `amount` must be converted from `Decimal` to `str` on INSERT and from `str` to `Decimal` on SELECT |
| IMP-007 | IMP-004, IMP-006 | The service orchestrates validated input and repository writes; both the Validation Layer (IMP-004) and Repository (IMP-006) must be ready for the service to call | IMP-004 and IMP-006 both complete | Developer | |
| IMP-008 | IMP-005, IMP-007 | The router wires together the Global Error Handler (IMP-005) and the Expense Service (IMP-007); both must be implemented before the endpoint can be assembled | IMP-005 and IMP-007 both complete | Developer | The 10 KB body size limit must be set when constructing the `FastAPI()` instance or via Starlette middleware |
| IMP-009 | IMP-001 | The middleware attaches to the FastAPI `app` instance; the project must be scaffolded first | IMP-001 complete; wire into `app/main.py` no later than IMP-008 | Developer | P2 — does not block functional tasks but must be wired in before IMP-011 for NFR-008 compliance |
| IMP-010 | IMP-004 | Unit tests import and exercise the Validation Layer directly; the validators must be implemented first | IMP-004 complete | Developer | |
| IMP-011 | IMP-008, IMP-009, IMP-010 | Integration tests exercise the full request stack including middleware logging; all layers must be wired together | IMP-008, IMP-009, and IMP-010 all complete | Developer | Use `TestClient` with an isolated DB via a pytest fixture that overrides the `DB_PATH` environment variable |
| IMP-012 | IMP-011 | Verification runs against a live server; all automated tests must pass before sign-off can proceed | IMP-011 complete with zero test failures | Developer | Closing this task confirms that HIGH findings DR-001, DR-002, and DR-003 are resolved |

---

## 5. Milestones and Checkpoints

- **Milestone 1 — Foundation Ready** (IMP-001, IMP-002, IMP-003, IMP-005 complete): The `app/` package exists and imports cleanly; the SQLite `expenses` table schema matches the DDL specification; Pydantic models instantiate without error; any Pydantic validation error returns HTTP 400 — never HTTP 422 — from the FastAPI application. This milestone confirms the three P0 foundations are in place before business logic is built on top of them.

- **Milestone 2 — Business Logic Complete** (IMP-004, IMP-006, IMP-007 complete): `create_expense()` can be called with a valid `ExpenseCreate`, writes a record atomically to SQLite, and returns an `ExpenseRecord` with a UUID; all seven validation error messages match requirements Section 8 exactly; whitespace-only `category` is rejected; `amount` round-trips correctly as `TEXT` through the repository. This milestone confirms all four layers (Validation, Service, Repository, Data) are functional end-to-end before the HTTP interface is layered on top.

- **Milestone 3 — API Endpoint Live** (IMP-008, IMP-009 complete): `POST /expenses` returns `201 Created` with the full expense JSON for a valid request; all error scenarios return the correct HTTP status codes (400, 500, 503); request logging appears on stdout with correct log levels. This milestone confirms the application is runnable and API-testable.

- **Milestone 4 — Verified and Signed Off** (IMP-010, IMP-011, IMP-012 complete): All unit and integration tests pass; AC-001, AC-002, and AC-003 are verified against a running server; no HTTP 422 response is produced by any input; all error strings match requirements Section 8 verbatim; HIGH findings DR-001, DR-002, and DR-003 are closed.

---

## 6. Risks to Delivery Sequence

- **Pydantic v2 custom validator syntax (DR-003)**: Pydantic v2 changed the validator API from `@validator` to `@field_validator` with different error-raising conventions. Incorrect use will silently produce Pydantic's own default error strings instead of the required custom messages, causing AC-002 and AC-003 to fail. Mitigation: implement IMP-004 before wiring to the router; verify each of the seven message strings explicitly in IMP-010 unit tests before proceeding to IMP-011.

- **Missing-body detection in RequestValidationError (DR-002)**: Identifying the specific case where the entire request body is absent requires inspecting the `RequestValidationError` details for an error with `loc == ("body",)` and `type == "missing"`. If this detection logic is incorrect, the missing-body case will either return a generic 400 message or a 422. Mitigation: add a dedicated test case for a completely absent body in IMP-011 and confirm the exact 400 response with the message `"Request body is required"` before IMP-012 closes DR-002.

- **Decimal-to-TEXT round-trip precision for `amount`**: Storing `amount` as `TEXT` preserves decimal precision but requires a consistent serialisation strategy. A mismatch between how the value is stored (`"45.50"` vs `"45.5"`) and how it is returned in the JSON response could produce trailing-zero inconsistencies. Mitigation: define a single canonical serialisation function in `app/repository.py`; include amount round-trip assertions in IMP-010 and IMP-011.

- **Body size limit enforcement mechanism**: FastAPI does not expose a simple `max_body_size` constructor parameter. Enforcing 10 KB requires a custom Starlette middleware or a third-party package. If the approach is not decided before IMP-008, the implementation may omit this NFR-004 control. Mitigation: resolve the implementation approach (see Section 7, Open Question 2) before starting IMP-008; include a test with a payload exceeding 10 KB in IMP-011.

- **Integration test database isolation**: Integration tests that write to the development `expenses.db` will pollute real data and produce order-dependent test failures. Mitigation: configure a pytest fixture that sets `DB_PATH` to a temporary file or `":memory:"` before each test session and tears it down afterwards; document this as a required fixture in IMP-011.

---

## 7. Open Questions

- **OQ-02 (carried from `docs/architecture.md`)**: Should a `GET /health` liveness endpoint be delivered within US-001 or deferred to a post-MVP story? This does not block any task in the current plan. Recommended resolution: defer to a separate story; document the decision in `docs/architecture.md` Section 8 (Operational Readiness). Owner: Developer. Expected resolution: before Milestone 3.

- **Body size limit implementation approach**: FastAPI/Starlette does not provide a native `max_body_size` parameter on `FastAPI()`. The implementation approach must be decided before IMP-008 begins. Recommended resolution: implement a lightweight Starlette middleware that reads the `Content-Length` request header and returns HTTP 413 if it exceeds 10 240 bytes; document this in `app/main.py`. Owner: Developer. Expected resolution: before starting IMP-008.

- **`amount` JSON response serialisation format**: The FR-004 response example shows `"amount": 45.50` as a JSON number. With `amount` stored as `TEXT` in SQLite, the response serialisation path must decide whether to return a `float`, `Decimal`, or formatted string. Recommended resolution: type `amount` as `Decimal` in `ExpenseResponse` and configure Pydantic to serialise it as a JSON number using `model_config = ConfigDict(json_encoders={Decimal: float})`; verify that `45.50` and `45.5` are handled consistently in IMP-011. Owner: Developer. Expected resolution: during IMP-003.

---

## 8. Approval
- **Decision**: Pending
- **Approved By**: —
- **Approval Date**: —
