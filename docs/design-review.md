# Design Review: Expense Tracker — US-001 Add Expense

## 1. Review Metadata
- **Source Document**: `docs/architecture.md`
- **Review Status**: Completed
- **Overall Verdict**: Ready with Conditions
- **Reviewer**: Design Review Agent
- **Last Updated**: 10 Aug 2026

---

## 2. Review Context

### Scope
All ten sections of `docs/architecture.md` were reviewed end-to-end:
- Section 2 (Context and Drivers) — verified architectural driver traceability to `docs/requirements.md`
- Section 3 (High-Level Recommendation) — assessed fitness for scale, complexity, and team constraints
- Section 5 (Key Components and Responsibilities) — checked each component against its requirement obligations
- Section 6 (Data Flow) — traced happy path and failure paths against FR-001 through FR-007, and the error-handling table in requirements Section 8
- Section 7 (Technology Choices) — evaluated FastAPI, SQLite, and `sqlite3` selection rationale
- Section 8 (Cross-Cutting Concerns) — assessed security, reliability, performance, and operability controls
- Section 9 (Risks, Assumptions, Open Questions) — reviewed all three risk items, assumption carry-forwards, and three open questions

### Constraints and Standards
- MVP delivery by a single developer; no cloud infrastructure; no external compliance obligations
- Performance target: 500 ms response under 50 concurrent requests (NFR-001)
- Data integrity: no partial writes; atomic persistence (NFR-002)
- Availability: 99.9% uptime target; 503 on transient store errors (NFR-003)
- Security: no authentication for MVP; SQL injection prevention; body size enforcement (NFR-004)
- Logging: structured request/response logging; WARN and ERROR levels (NFR-008)
- API contract: RESTful; consistent JSON error envelope; 400/500/503 status codes as specified in requirements Section 6

---

## 3. Findings Register

| ID | Severity | Area | Finding | Impact | Recommendation | Owner | Status |
|----|----------|------|---------|--------|----------------|-------|--------|
| DR-001 | High | Delivery | FastAPI returns `422 Unprocessable Entity` by default for Pydantic validation failures. The architecture does not specify overriding `RequestValidationError` to return `400 Bad Request`. AC-002 and AC-003 in `docs/requirements.md` explicitly require HTTP 400 for all validation rejections, and requirements Section 6 maps all validation errors to `400`. | AC-002 and AC-003 will fail in testing. API contract violates NFR-006 and the HTTP Status Code Map in requirements Section 6. | Add an explicit `@app.exception_handler(RequestValidationError)` in the Global Error Handler component that re-maps 422 to 400 and formats the response as `{"error": "Validation failed", "details": [...]}`. Document this as a mandatory part of the Global Error Handler contract in architecture Section 5. | Architect | Open |
| DR-002 | High | Reliability | The "request body is missing entirely" scenario (requirements Section 8 error table, final row) is not addressed in the architecture data flows or component descriptions. FastAPI's default response for a missing body is 422 with its own message, not 400 with `"Request body is required"`. | Requirements Section 8 mandates a specific 400 response and error message for this case. The omission means a defined edge case has no specified handling, creating an implementation gap that will surface as a test failure. | Extend the Global Error Handler to intercept the missing-body case (a subclass of `RequestValidationError` in FastAPI) and return `400` with `{"error": "Validation failed", "details": ["Request body is required"]}`. Add this scenario to the Core Flow 2 failure paths in architecture Section 6. | Architect | Open |
| DR-003 | High | Maintainability | The Validation Layer description (architecture Section 5, Component 2) states errors are raised as `ValidationError` but does not specify that Pydantic's default type error messages must be replaced with the exact strings required by `docs/requirements.md`. Pydantic v2's default for a non-numeric `amount` is `"Input should be a valid number, unable to parse string as a number"` — not `"amount must be a valid number"` as required by requirements Section 8. | Pydantic's built-in messages will not match AC-002 or the error-handling table in requirements Section 8. Without explicit custom message configuration, the implementation will produce non-conforming error text that fails acceptance tests. | Specify in architecture Section 5 (Validation Layer) that all Pydantic field validators must use custom `@field_validator` decorators with explicit error message strings matching the exact text in requirements Section 8. List the required message strings in the architecture to anchor the implementation contract. | Architect | Open |
| DR-004 | Medium | Data | The Validation Layer description (architecture Section 5, Component 2) lists only three business rules: `amount > 0`, `category not blank or whitespace`, and `date matches YYYY-MM-DD`. It omits two field-length constraints defined in FR-001 and requirements Section 7: `category` maximum 100 characters and `description` maximum 500 characters. Requirements Section 8 specifies a 400 rejection and the message `"description must not exceed 500 characters"` for oversized descriptions. | These two constraints are required by FR-001 and must be enforced by the Validation Layer. Omitting them from the component spec creates an implementation gap; the developer may not add these validators. | Update architecture Section 5 (Validation Layer) to explicitly list all field constraints: `amount > 0`; `category` non-blank/non-whitespace with max 100 characters; `date` in YYYY-MM-DD format; `description` optional but max 500 characters if present. Each constraint must name its source requirement. | Architect | Open |
| DR-005 | Medium | Data | OQ-03 in architecture Section 9 asks whether to enforce two-decimal-place precision for `amount` at the database layer or only at the application layer. The open question is unresolved. Requirements assumption A-05 states "Decimal amounts are limited to two decimal places (currency precision)." Storing `amount` as SQLite `REAL` (8-byte IEEE 754 floating-point) cannot guarantee exact two-decimal representation for all values. | Unresolved precision handling means implementation may introduce floating-point rounding artefacts in stored amounts, violating A-05 and the data model definition in requirements Section 7. This is a data integrity risk, not merely a code quality concern. | Resolve OQ-03 before implementation begins. Recommended resolution: store `amount` as `TEXT` in SQLite, preserving exact decimal string representation; validate at the Validation Layer that the value is numeric, greater than zero, and has at most two decimal places using a regex or `Decimal` type comparison. Document the resolution in architecture Section 9 and reflect it in the SQLite schema (see DR-007). | Architect | Open |
| DR-006 | Medium | Data | The Validation Layer description states "category not blank or whitespace" as a business rule, but does not specify the implementation mechanism. Pydantic's `min_length=1` constraint rejects empty strings but accepts whitespace-only strings such as `"   "`. A whitespace-only category would bypass the validator and be stored as a non-empty but semantically empty string. | Requirements Section 8 requires rejection of blank or whitespace categories with the message `"category is required"`. Failing to specify the exact mechanism leaves a gap that will produce a test failure for the whitespace edge case. | Update architecture Section 5 (Validation Layer) to specify that the `category` field validator must call `.strip()` on the value before checking length, or use Pydantic v2's `strip_whitespace=True` field config combined with `min_length=1`, ensuring whitespace-only inputs are treated as blank. | Architect | Open |
| DR-007 | Medium | Data | The architecture does not define the SQLite `expenses` table DDL (CREATE TABLE statement). Column types for `id` (TEXT vs BLOB), `amount` (REAL vs TEXT), `date` (TEXT vs DATE), and the handling of the optional `description` default value are unspecified. | Without a defined schema, implementation decisions on column types are left to the developer. This directly affects data integrity (see DR-005 on amount precision), query correctness, and the ability for future stories (edit, delete, list) to build against a stable schema contract. | Add a `Database Schema` sub-section to architecture Section 5 (Repository) or Section 7 (Technology Choices — Data Layer) that specifies the `CREATE TABLE expenses` DDL with column names, types, NOT NULL constraints, and the default for `description`. The schema should reflect the resolution of OQ-03 (DR-005). | Architect | Open |
| DR-008 | Medium | Security | Architecture Sections 7 and 8 state that "FastAPI's built-in body size limit is configured" but do not specify the limit value. NFR-004 requires enforcement of a maximum request body size; without a concrete value the implementation decision is left entirely to the developer. | A too-generous limit fails to satisfy the payload-flooding protection goal of NFR-004. An unnecessarily tight limit may reject valid large descriptions (up to 500 characters). Without a documented value, the control cannot be verified or audited. | Specify the maximum request body size in architecture Section 8 (Security). A value of 10 KB is appropriate given the largest valid payload is approximately 700 bytes (500-character description plus other fields). Document the value alongside the FastAPI `app = FastAPI(...)` configuration note so the implementation target is unambiguous. | Architect | Open |
| DR-009 | Medium | Operability | OQ-01 in architecture Section 9 asks whether the SQLite database file path should be hard-coded or read from an environment variable. The architecture recommends the environment-variable approach but does not commit to it. Without resolution, the implementation may default to a hard-coded path, making environment-specific configuration (test vs. production) impossible without code changes. | A hard-coded path breaks the principle stated in architecture Section 8 (Operational Readiness) that "the SQLite database file path is configurable via an environment variable." This creates an inconsistency within the architecture document and complicates the test setup described in future test stories. | Resolve OQ-01 in architecture Section 9 by committing to the environment-variable approach: define a `DATABASE_URL` (or `DB_PATH`) environment variable with a default value of `./expenses.db`. Remove OQ-01 from the open questions list and update the Operational Readiness paragraph in Section 8 to reflect this as a confirmed design decision. | Architect | Open |
| DR-010 | Low | Reliability | Architecture Section 9 (R-02) recommends enabling SQLite WAL mode as a crash-durability mitigation, but uses advisory language ("Enable WAL mode"). The Repository component description in Section 5 does not list WAL mode initialisation as a responsibility. | If left as a recommendation rather than a requirement, the implementation may omit WAL mode. An OS crash without WAL mode risks journal corruption and potential data loss, which conflicts with NFR-002 (data integrity) and the spirit of R-02's mitigation. | Elevate WAL mode from a risk mitigation note in Section 9 to a mandatory repository initialisation step in architecture Section 5 (Repository component Responsibility field): "On startup, execute `PRAGMA journal_mode=WAL` before accepting any writes." Remove the conditional language from Section 9. | Architect | Open |

---

## 4. Agreed Design Decisions

| Decision ID | Decision | Rationale | Trade-offs | Follow-up |
|-------------|----------|-----------|------------|-----------|
| DD-001 | Layered Modular Monolith (Router → Validation → Service → Repository) is the selected architecture style | Single endpoint with straightforward CRUD semantics; distributing across services adds infrastructure cost with no benefit at this scale or team size | Horizontal scale-out later requires migrating the data layer to a networked database; the repository abstraction isolates this change | None required for MVP |
| DD-002 | FastAPI + Pydantic replaces Flask + SQLAlchemy | FastAPI provides automatic body parsing, Pydantic validation, OpenAPI docs generation, and ASGI compatibility for future async scale-out; reduces boilerplate compared to Flask and is lighter than SQLAlchemy for a single-table MVP | FastAPI's default 422 responses for validation errors must be overridden (DR-001, DR-002, DR-003) — this is a known framework quirk with a well-defined workaround | Address DR-001 through DR-003 in architecture update before implementation |
| DD-003 | SQLite via Python's built-in `sqlite3` module is the data store | Zero infrastructure setup; satisfies local single-developer deployment; parameterised queries satisfy NFR-004; transactions satisfy NFR-002; repository abstraction isolates future migration to PostgreSQL | Single writer at a time; not suitable for horizontal scale-out; floating-point precision for `amount` must be managed explicitly (DR-005, DR-007) | Resolve DR-005 and DR-007 to define column types before implementation |
| DD-004 | No authentication or authorisation for MVP | Explicitly scoped out by NFR-004 and A-04 in requirements; interface designed to accept auth middleware in a future iteration without restructuring | The endpoint is open to any caller on the network; must be restricted to localhost or trusted network for MVP (R-03 in architecture) | Ensure server is not exposed on a public interface during MVP operation |
| DD-005 | UUID v4 generated by the Expense Service using Python's `uuid` standard library | Satisfies FR-002; no additional dependency required; caller cannot supply their own ID (A-02); UUID v4 collision probability is negligible for a local single-user MVP | None for MVP scale | None |
| DD-006 | Synchronous request handling is sufficient for the 50-concurrent-request target | FastAPI with `uvicorn` handles 50 concurrent synchronous requests well within the 500 ms target given the lightweight SQLite write path; async queue overhead is not justified | If write concurrency grows significantly, uvicorn multi-worker mode or an async SQLite driver will be required; the layered interface isolates this change | Monitor latency under load testing; plan async migration trigger point |

---

## 5. Required Architecture Document Updates

> This design review agent does not modify `docs/architecture.md` or any other file. All required changes are documented below for the Architect or Senior Developer to apply before implementation begins.

| Change ID | Target Section in `docs/architecture.md` | Required Update | Linked Finding |
|-----------|------------------------------------------|-----------------|----------------|
| ACH-001 | Section 5 — Component 6: Global Error Handler | Add an explicit statement that a FastAPI `@app.exception_handler(RequestValidationError)` must be registered to intercept Pydantic validation errors and return `400 Bad Request` (not 422) with the standard `{"error": "Validation failed", "details": [...]}` envelope. Reference NFR-006 and AC-002/AC-003 as the drivers. | DR-001 |
| ACH-002 | Section 6 — Core Flow 2 (Validation Failure) and a new Core Flow 3: Missing Request Body | Add a new Core Flow 3 that describes the "request body is missing entirely" scenario: client sends POST with no body → FastAPI raises RequestValidationError → Global Error Handler intercepts → returns 400 with `{"error": "Validation failed", "details": ["Request body is required"]}` → Request Logger records 400 at WARN. | DR-002 |
| ACH-003 | Section 5 — Component 2: Validation Layer | Add a statement that all field validators must use explicit custom error message strings matching the exact text in `docs/requirements.md` Section 8. List the six required error message strings: `"amount must be greater than zero"`, `"amount must be a valid number"`, `"category is required"`, `"date is required"`, `"date must be in YYYY-MM-DD format"`, `"description must not exceed 500 characters"`. | DR-003 |
| ACH-004 | Section 5 — Component 2: Validation Layer | Extend the business-rules list to include all field constraints: `amount` greater than zero; `amount` numeric; `category` non-blank, non-whitespace, max 100 characters; `date` in strict YYYY-MM-DD format; `description` optional but max 500 characters when present. Each constraint must cite its source requirement (FR-001, FR-005, FR-006, FR-007). | DR-004 |
| ACH-005 | Section 5 — Component 2: Validation Layer | Specify that the `category` validator calls `.strip()` on the input before checking length, or uses Pydantic v2's `strip_whitespace=True` field config with `min_length=1`, to ensure whitespace-only strings are rejected as blank. | DR-006 |
| ACH-006 | Section 9 — Open Questions: Resolve OQ-03; Section 5 — Component 4: Repository | Resolve OQ-03: commit to storing `amount` as `TEXT` in SQLite to preserve exact decimal representation; validate at the application layer that the value is numeric, greater than zero, and has at most two decimal places. Remove OQ-03 from Open Questions and move the decision to Section 4 (Agreed Decisions). | DR-005 |
| ACH-007 | Section 5 — Component 4: Repository (new sub-section: Database Schema) | Add the `CREATE TABLE expenses` DDL specifying: `id TEXT PRIMARY KEY NOT NULL`, `amount TEXT NOT NULL`, `category TEXT NOT NULL`, `date TEXT NOT NULL`, `description TEXT NOT NULL DEFAULT ''`. Column types must reflect the OQ-03 resolution (ACH-006). | DR-007 |
| ACH-008 | Section 8 — Cross-Cutting Concerns: Security | Replace the vague "maximum request body size is configured" statement with a concrete value: 10 KB. Add the FastAPI application initialisation note: `app = FastAPI(); app.add_middleware(...)` or equivalent with the body-size limit setting. | DR-008 |
| ACH-009 | Section 9 — Open Questions: Resolve OQ-01; Section 8 — Operational Readiness | Resolve OQ-01: commit to reading the database file path from a `DB_PATH` environment variable with a default of `./expenses.db`. Update the Operational Readiness paragraph to name the variable and default explicitly. Remove OQ-01 from Open Questions. | DR-009 |
| ACH-010 | Section 5 — Component 4: Repository (Responsibility field) | Add WAL mode initialisation as a mandatory responsibility: "On application startup, execute `PRAGMA journal_mode=WAL` on the SQLite connection before accepting any write operations." Adjust the R-02 note in Section 9 to reference this as a confirmed implementation step rather than a conditional recommendation. | DR-010 |

---

## 6. Open Risks and Watch Items

- **Risk**: SQLite write concurrency ceiling (R-01 in architecture)
  - **Mitigation / Monitoring**: Repository layer is the sole SQLite integration point; switching to PostgreSQL requires only repository-layer changes. Monitor p95 latency under load; establish a migration trigger (e.g., sustained p95 > 300 ms under 50 concurrent writes) before expanding the user base.

- **Risk**: SQLite file durability on crash (R-02 in architecture)
  - **Mitigation / Monitoring**: WAL mode must be committed as a mandatory initialisation step (ACH-010). Add a regular backup of `expenses.db` before production use. Monitor disk health on the host machine.

- **Risk**: No authentication on MVP endpoint (R-03 in architecture)
  - **Mitigation / Monitoring**: Accepted as an explicit MVP assumption (A-04, NFR-004). The server process must be bound to `127.0.0.1` or a trusted private network interface only during MVP operation. Authentication must be scoped into the first post-MVP story before any public-facing deployment.

- **Risk**: Single `uvicorn` process with no automatic restart (R-04 in architecture)
  - **Mitigation / Monitoring**: Process supervisor (systemd or equivalent with `Restart=always`) is required before targeting the 99.9% uptime NFR-003. This is an infrastructure concern, not an application-layer change, and must be in place before the MVP is declared production-ready.

- **Risk**: Floating-point precision for `amount` if stored as SQLite REAL
  - **Mitigation / Monitoring**: This risk is contingent on OQ-03 resolution. If the recommendation in ACH-006 is accepted (store as TEXT), this risk is eliminated. If REAL storage is chosen instead, a rounding artefact in stored values is possible for amounts with repeating binary fractions; document the accepted precision loss and validate it meets A-05.

---

## 7. Exit Criteria

- [x] No unresolved Critical findings — no Critical findings were identified
- [ ] High findings have approved mitigation or fix — DR-001, DR-002, and DR-003 are open; architecture updates ACH-001 through ACH-003 must be applied and confirmed by the Architect before this criterion is met
- [x] Key assumptions explicitly documented — A-01 through A-07 are carried forward from `docs/requirements.md` and confirmed in architecture Section 9
- [ ] Architecture baseline updated and internally consistent — ten architecture updates (ACH-001 through ACH-010) are required; this criterion is met when all updates are applied to `docs/architecture.md` and the document status advances from `Draft` to `Reviewed`
