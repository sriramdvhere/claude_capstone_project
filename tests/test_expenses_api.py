"""
Integration tests for POST /expenses (IMP-011).

Uses FastAPI TestClient with an isolated per-test SQLite database
(configured via the test_client fixture in tests/conftest.py).

Coverage:
  AC-001 — valid expense returns 201 with all fields including a UUID id.
  AC-002 — invalid / zero amount returns 400 with exact error string.
  AC-003 — missing mandatory fields returns 400 identifying absent fields.
  DR-001 — no test scenario produces HTTP 422.
  DR-002 — missing request body returns 400 with "Request body is required".
  DR-003 — all error strings match requirements Section 8 verbatim.
  NFR-003 — simulated DB failure returns 503.
"""
import uuid
from unittest.mock import patch

import pytest

from app.repository import DBError, DBUnavailableError


# ---------------------------------------------------------------------------
# AC-001 — Happy path
# ---------------------------------------------------------------------------


def test_create_valid_expense_returns_201(test_client):
    response = test_client.post(
        "/expenses",
        json={
            "amount": 45.50,
            "category": "Food",
            "date": "2026-07-22",
            "description": "Lunch at the office cafeteria",
        },
    )
    assert response.status_code == 201


def test_create_valid_expense_response_contains_uuid_id(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50, "category": "Food", "date": "2026-07-22"},
    )
    data = response.json()
    assert "id" in data
    parsed = uuid.UUID(data["id"])  # raises ValueError if not a valid UUID
    assert parsed.version == 4


def test_create_valid_expense_response_contains_all_fields(test_client):
    response = test_client.post(
        "/expenses",
        json={
            "amount": 45.50,
            "category": "Food",
            "date": "2026-07-22",
            "description": "Lunch",
        },
    )
    data = response.json()
    assert data["category"] == "Food"
    assert data["date"] == "2026-07-22"
    assert data["description"] == "Lunch"
    assert isinstance(data["amount"], float)
    assert data["amount"] == pytest.approx(45.50)


def test_create_expense_without_description_defaults_to_empty_string(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": 10.00, "category": "Transport", "date": "2026-07-22"},
    )
    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_two_expenses_get_distinct_ids(test_client):
    r1 = test_client.post(
        "/expenses",
        json={"amount": 10.00, "category": "Food", "date": "2026-07-01"},
    )
    r2 = test_client.post(
        "/expenses",
        json={"amount": 20.00, "category": "Transport", "date": "2026-07-02"},
    )
    assert r1.json()["id"] != r2.json()["id"]


# ---------------------------------------------------------------------------
# AC-002 — Invalid amount → 400 with exact error string
# ---------------------------------------------------------------------------


def test_zero_amount_returns_400_with_exact_message(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": 0, "category": "Food", "date": "2026-07-22"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Validation failed"
    assert "amount must be greater than zero" in data["details"]


def test_negative_amount_returns_400_with_exact_message(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": -10.00, "category": "Food", "date": "2026-07-22"},
    )
    assert response.status_code == 400
    assert "amount must be greater than zero" in response.json()["details"]


def test_non_numeric_amount_returns_400_with_exact_message(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": "abc", "category": "Food", "date": "2026-07-22"},
    )
    assert response.status_code == 400
    assert "amount must be a valid number" in response.json()["details"]


def test_zero_string_amount_returns_400(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": "0.00", "category": "Food", "date": "2026-07-22"},
    )
    assert response.status_code == 400
    assert "amount must be greater than zero" in response.json()["details"]


# ---------------------------------------------------------------------------
# AC-003 — Missing mandatory fields → 400
# ---------------------------------------------------------------------------


def test_missing_category_returns_400_with_category_required(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50, "date": "2026-07-22"},
    )
    assert response.status_code == 400
    assert "category is required" in response.json()["details"]


def test_missing_date_returns_400_with_date_required(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50, "category": "Food"},
    )
    assert response.status_code == 400
    assert "date is required" in response.json()["details"]


def test_whitespace_category_returns_400_with_category_required(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50, "category": "   ", "date": "2026-07-22"},
    )
    assert response.status_code == 400
    assert "category is required" in response.json()["details"]


def test_invalid_date_format_returns_400_with_exact_message(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50, "category": "Food", "date": "22-07-2026"},
    )
    assert response.status_code == 400
    assert "date must be in YYYY-MM-DD format" in response.json()["details"]


def test_description_too_long_returns_400_with_exact_message(test_client):
    response = test_client.post(
        "/expenses",
        json={
            "amount": 45.50,
            "category": "Food",
            "date": "2026-07-22",
            "description": "a" * 501,
        },
    )
    assert response.status_code == 400
    assert "description must not exceed 500 characters" in response.json()["details"]


# ---------------------------------------------------------------------------
# DR-002 — Missing request body → 400 with "Request body is required"
# ---------------------------------------------------------------------------


def test_missing_body_returns_400_with_request_body_is_required(test_client):
    response = test_client.post(
        "/expenses",
        content=b"",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Validation failed"
    assert "Request body is required" in data["details"]


# ---------------------------------------------------------------------------
# DR-001 — No HTTP 422 for any input
# ---------------------------------------------------------------------------


def test_no_422_for_invalid_amount(test_client):
    response = test_client.post(
        "/expenses",
        json={"amount": "not_a_number", "category": "Food", "date": "2026-07-22"},
    )
    assert response.status_code != 422, "Must not return 422 for invalid amount"
    assert response.status_code == 400


def test_no_422_for_missing_fields(test_client):
    response = test_client.post("/expenses", json={})
    assert response.status_code != 422, "Must not return 422 for missing fields"
    assert response.status_code == 400


def test_no_422_for_missing_body(test_client):
    response = test_client.post(
        "/expenses",
        content=b"",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code != 422


# ---------------------------------------------------------------------------
# NFR-003 — DB failures → correct HTTP status codes
# ---------------------------------------------------------------------------


def test_db_unavailable_returns_503(test_client):
    with patch("app.repository.insert", side_effect=DBUnavailableError("DB down")):
        response = test_client.post(
            "/expenses",
            json={"amount": 45.50, "category": "Food", "date": "2026-07-22"},
        )
    assert response.status_code == 503


def test_db_error_returns_500(test_client):
    with patch("app.repository.insert", side_effect=DBError("General error")):
        response = test_client.post(
            "/expenses",
            json={"amount": 45.50, "category": "Food", "date": "2026-07-22"},
        )
    assert response.status_code == 500


# ---------------------------------------------------------------------------
# Body size limit (DR-008)
# ---------------------------------------------------------------------------


def test_body_exceeding_10kb_returns_413(test_client):
    large_description = "x" * (10 * 1024 + 1)
    # Build a JSON body whose Content-Length exceeds 10 KB
    import json

    body = json.dumps(
        {
            "amount": 1.00,
            "category": "Test",
            "date": "2026-07-22",
            "description": large_description,
        }
    ).encode()
    response = test_client.post(
        "/expenses",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413


# ---------------------------------------------------------------------------
# Additional coverage: error response body structures
# ---------------------------------------------------------------------------


def test_db_unavailable_response_body_structure(test_client):
    """503 response must contain 'error' and 'details' keys."""
    with patch("app.repository.insert", side_effect=DBUnavailableError("DB down")):
        response = test_client.post(
            "/expenses",
            json={"amount": 45.50, "category": "Food", "date": "2026-07-22"},
        )
    data = response.json()
    assert response.status_code == 503
    assert "error" in data
    assert "details" in data
    assert isinstance(data["details"], list)


def test_db_error_response_body_structure(test_client):
    """500 response must contain 'error' and 'details' keys."""
    with patch("app.repository.insert", side_effect=DBError("General error")):
        response = test_client.post(
            "/expenses",
            json={"amount": 45.50, "category": "Food", "date": "2026-07-22"},
        )
    data = response.json()
    assert response.status_code == 500
    assert "error" in data
    assert "details" in data
    assert isinstance(data["details"], list)


def test_413_response_body_structure(test_client):
    """413 response must contain 'error' and 'details' keys."""
    import json

    large_description = "x" * (10 * 1024 + 1)
    body = json.dumps(
        {
            "amount": 1.00,
            "category": "Test",
            "date": "2026-07-22",
            "description": large_description,
        }
    ).encode()
    response = test_client.post(
        "/expenses",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    data = response.json()
    assert response.status_code == 413
    assert "error" in data
    assert "details" in data


# ---------------------------------------------------------------------------
# Additional coverage: null field values in JSON
# ---------------------------------------------------------------------------


def test_null_amount_returns_400_with_exact_message(test_client):
    """JSON null for amount must return 400 with 'amount must be a valid number'."""
    response = test_client.post(
        "/expenses",
        json={"amount": None, "category": "Food", "date": "2026-07-22"},
    )
    assert response.status_code == 400
    assert "amount must be a valid number" in response.json()["details"]


def test_null_date_returns_400_with_exact_message(test_client):
    """JSON null for date must return 400 with 'date is required'."""
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50, "category": "Food", "date": None},
    )
    assert response.status_code == 400
    assert "date is required" in response.json()["details"]


# ---------------------------------------------------------------------------
# Additional coverage: category too long at API level
# ---------------------------------------------------------------------------


def test_category_too_long_returns_400(test_client):
    """Category exceeding 100 characters must return 400."""
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50, "category": "a" * 101, "date": "2026-07-22"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Validation failed"
    assert len(data["details"]) > 0


# ---------------------------------------------------------------------------
# Additional coverage: multiple validation errors in a single request
# ---------------------------------------------------------------------------


def test_multiple_missing_fields_returns_all_errors(test_client):
    """A request missing both category and date must return 400 with both errors."""
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50},
    )
    assert response.status_code == 400
    details = response.json()["details"]
    assert "category is required" in details
    assert "date is required" in details


# ---------------------------------------------------------------------------
# Additional coverage: date format variants at API level
# ---------------------------------------------------------------------------


def test_date_slash_format_returns_400(test_client):
    """Date in YYYY/MM/DD format must return 400 with the exact message."""
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50, "category": "Food", "date": "2026/07/22"},
    )
    assert response.status_code == 400
    assert "date must be in YYYY-MM-DD format" in response.json()["details"]


def test_date_invalid_calendar_date_returns_400(test_client):
    """Date with impossible month (13) must return 400 with the exact message."""
    response = test_client.post(
        "/expenses",
        json={"amount": 45.50, "category": "Food", "date": "2026-13-01"},
    )
    assert response.status_code == 400
    assert "date must be in YYYY-MM-DD format" in response.json()["details"]


# ---------------------------------------------------------------------------
# Additional coverage: 400 error response shape invariant
# ---------------------------------------------------------------------------


def test_400_error_response_has_correct_shape(test_client):
    """Every 400 response must include 'error' and 'details' as a list."""
    response = test_client.post(
        "/expenses",
        json={"amount": -1, "category": "Food", "date": "2026-07-22"},
    )
    data = response.json()
    assert response.status_code == 400
    assert data["error"] == "Validation failed"
    assert isinstance(data["details"], list)
    assert len(data["details"]) > 0
