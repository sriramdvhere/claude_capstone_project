# Requirements Document

## 1. Document Metadata

| Field             | Value                                      |
|-------------------|--------------------------------------------|
| **Version**       | v1.0                                       |
| **Last Updated**  | 10 Aug 2026                                |
| **User Story ID** | US-001                                     |
| **User Story**    | Add an Expense                             |
| **Prepared By**   | Sriram Dhanaraj                            |
| **Status**        | Draft                                      |

---

## 2. User Story

> **As a user,**
> I want to record a new expense with an amount, category, date, and description,
> **So that** I can keep track of my spending.

---

## 3. Functional Requirements

### FR-001 — Record a New Expense

The system must provide an endpoint that accepts a new expense record from the user.

**Input fields:**

| Field         | Type    | Required | Constraints                                                   |
|---------------|---------|----------|---------------------------------------------------------------|
| `amount`      | Decimal | Yes      | Must be a positive number greater than zero (e.g., `45.50`)  |
| `category`    | String  | Yes      | Must be non-empty; maximum 100 characters                     |
| `date`        | String  | Yes      | Must be a valid date in ISO 8601 format (`YYYY-MM-DD`)        |
| `description` | String  | No       | Optional free-text field; maximum 500 characters              |

### FR-002 — Unique ID Generation

When a valid expense is saved, the system must automatically generate and assign a unique identifier (UUID v4) to the expense record. The ID must not be supplied by the caller.

### FR-003 — Persist the Expense

The system must persist the expense record to the data store upon successful validation. The stored record must include all submitted fields plus the system-generated `id`.

### FR-004 — Return Created Expense

On successful creation, the system must return the full expense object (including the generated `id`) to the caller.

**Response body example (success):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "amount": 45.50,
  "category": "Food",
  "date": "2026-07-22",
  "description": "Lunch at the office cafeteria"
}
```

### FR-005 — Reject Invalid Amount

The system must reject any request where the `amount` is zero or negative. A descriptive validation error message must be returned indicating that the amount must be greater than zero.

### FR-006 — Reject Missing Mandatory Fields

The system must reject any request where one or more mandatory fields (`amount`, `category`, `date`) are absent or blank. The error response must identify which required fields are missing.

### FR-007 — Reject Invalid Date Format

The system must reject any request where the `date` field does not conform to ISO 8601 format (`YYYY-MM-DD`). The error response must indicate that the date format is invalid.

---

## 4. Non-Functional Requirements

### NFR-001 — Performance

- The add-expense endpoint must respond within **500 milliseconds** under normal load conditions.
- The endpoint must support at least **50 concurrent requests** without degraded response times.

### NFR-002 — Data Integrity

- Each expense record must have a unique, immutable `id` after creation.
- Partial writes must not occur; if persistence fails, no record should be saved and an appropriate error must be returned.

### NFR-003 — Reliability / Availability

- The service must target **99.9% uptime** (approximately 8.7 hours of downtime per year).
- Transient data-store errors must return a `503 Service Unavailable` response rather than silently failing.

### NFR-004 — Security

- Input fields must be sanitized to prevent injection attacks (SQL injection, NoSQL injection).
- The API must enforce a maximum request body size to prevent payload-flooding attacks.
- No authentication or authorization is required for the MVP scope; this can be added in a future iteration.

### NFR-005 — Maintainability

- Business validation logic (amount, category, date) must be isolated in a dedicated validation layer, separate from routing and persistence layers.
- Code must follow the project's established style guide and pass linting checks.

### NFR-006 — Usability / API Design

- The API must follow RESTful conventions.
- All error responses must use a consistent JSON structure:
  ```json
  {
    "error": "Validation failed",
    "details": ["amount must be greater than zero"]
  }
  ```

### NFR-007 — Compatibility

- The API must be accessible from any HTTP client (browsers, mobile apps, third-party tools such as Postman).
- Response payloads must be UTF-8 encoded JSON.

### NFR-008 — Logging and Monitoring

- Every inbound request must be logged with: timestamp, HTTP method, endpoint path, response status code, and latency.
- Validation failures must be logged at `WARN` level.
- Unhandled exceptions must be logged at `ERROR` level with a full stack trace.

### NFR-009 — Data Retention

- Expense records must be retained indefinitely unless explicitly deleted by a future feature.

---

## 5. Acceptance Criteria

### AC-001 — Successfully Record a Valid Expense

- **Given** the user provides a valid positive `amount` (e.g., `45.50`), a non-empty `category` (e.g., `"Food"`), and a valid ISO 8601 `date` (e.g., `"2026-07-22"`)
- **When** the user submits the request to add an expense
- **Then** the system must:
  - Save the expense to the data store
  - Generate a unique UUID for the record
  - Return the newly created expense object (including `id`)
  - Return HTTP status code **201 Created**

### AC-002 — Attempt to Record an Expense with an Invalid Amount

- **Given** the user provides an `amount` that is zero (e.g., `0.00`) or negative (e.g., `-10.00`)
- **When** the user submits the request to add an expense
- **Then** the system must:
  - Reject the request without persisting any record
  - Return HTTP status code **400 Bad Request**
  - Include a validation error message: `"amount must be greater than zero"`

### AC-003 — Attempt to Record an Expense with Missing Mandatory Fields

- **Given** the user omits or leaves blank the `category` or `date` field
- **When** the user submits the request to add an expense
- **Then** the system must:
  - Reject the request without persisting any record
  - Return HTTP status code **400 Bad Request**
  - List the names of all missing or blank required fields in the error response

---

## 6. HTTP API Specification

| Method | Endpoint        | Description          |
|--------|-----------------|----------------------|
| POST   | `/expenses`     | Create a new expense |

### Request Headers

| Header         | Value              | Required |
|----------------|--------------------|----------|
| `Content-Type` | `application/json` | Yes      |

### HTTP Status Code Map

| Scenario                           | Status Code               |
|------------------------------------|---------------------------|
| Expense created successfully       | `201 Created`             |
| Validation error (client fault)    | `400 Bad Request`         |
| Internal or persistence error      | `500 Internal Server Error` |
| Data store temporarily unavailable | `503 Service Unavailable` |

---

## 7. Data Model

### Expense Entity

| Field         | Type     | Nullable | Notes                                         |
|---------------|----------|----------|-----------------------------------------------|
| `id`          | UUID     | No       | System-generated; primary key                 |
| `amount`      | Decimal  | No       | Precision: up to 2 decimal places; > 0        |
| `category`    | String   | No       | Max 100 characters                            |
| `date`        | Date     | No       | Stored as ISO 8601 date                       |
| `description` | String   | Yes      | Optional; max 500 characters; defaults to `""` |

---

## 8. Error Handling and Edge Cases

| Scenario                            | Expected Behavior                                                          |
|-------------------------------------|----------------------------------------------------------------------------|
| `amount` is `0`                     | Reject with 400; error: `"amount must be greater than zero"`              |
| `amount` is negative                | Reject with 400; error: `"amount must be greater than zero"`              |
| `amount` is a non-numeric string    | Reject with 400; error: `"amount must be a valid number"`                 |
| `category` is blank or whitespace   | Reject with 400; error: `"category is required"`                          |
| `date` is absent                    | Reject with 400; error: `"date is required"`                              |
| `date` format is invalid            | Reject with 400; error: `"date must be in YYYY-MM-DD format"`             |
| `description` is absent             | Accept; store as empty string or null                                     |
| `description` exceeds 500 chars     | Reject with 400; error: `"description must not exceed 500 characters"`    |
| Data store write failure            | Return 500 or 503; do not persist partial record; log at ERROR level      |
| Request body is missing entirely    | Reject with 400; error: `"Request body is required"`                      |

---

## 9. Dependencies and Integrations

| Dependency              | Type     | Notes                                                          |
|-------------------------|----------|----------------------------------------------------------------|
| Data store              | Internal | Relational or document database for persistence of expenses   |
| UUID generation library | Internal | Standard library or well-known package for UUID v4 generation |
| Validation library      | Internal | Input sanitization and type-checking                          |

No external third-party integrations are required for this user story.

---

## 10. Assumptions

| ID   | Assumption                                                                                    |
|------|-----------------------------------------------------------------------------------------------|
| A-01 | The `description` field is optional; the acceptance criteria does not list it as mandatory.   |
| A-02 | Unique IDs are generated as UUID v4 by the system; callers cannot supply their own IDs.       |
| A-03 | Dates are accepted and stored in ISO 8601 format (`YYYY-MM-DD`) only.                        |
| A-04 | No authentication or authorization is required for the MVP scope of this user story.         |
| A-05 | Decimal amounts are limited to two decimal places (currency precision).                       |
| A-06 | There is no upper bound on the `amount` value for the MVP.                                   |
| A-07 | The API is accessed over HTTPS in production environments (infrastructure concern, not app).  |

---

## 11. Out of Scope (Post-MVP)

- Authentication and user-level expense isolation
- Editing or deleting an existing expense
- Listing or filtering expenses
- Pagination of expense records
- Currency support beyond a single default currency
- Recurring or scheduled expenses
- Bulk import of expenses
