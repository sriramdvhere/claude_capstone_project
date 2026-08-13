"""
Unit tests for the Expense Service layer (app/service.py).

These tests exercise the service in isolation by mocking the repository
boundary.  No database or HTTP layer is involved.

Coverage:
  - Successful create_expense returns an ExpenseRecord.
  - The generated id is a UUID v4.
  - All field values from the validated input are propagated correctly.
  - DBUnavailableError raised by the repository is propagated to the caller.
  - DBError raised by the repository is propagated to the caller.
"""
import uuid
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest

from app.models import ExpenseCreate, ExpenseRecord
from app import service
from app.repository import DBError, DBUnavailableError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_expense_create(
    amount="45.50",
    category="Food",
    date="2026-07-22",
    description="Lunch",
) -> ExpenseCreate:
    """Return a fully-validated ExpenseCreate instance for use in service tests."""
    return ExpenseCreate(
        amount=amount,
        category=category,
        date=date,
        description=description,
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_create_expense_returns_expense_record():
    """create_expense must return an ExpenseRecord on success."""
    data = make_expense_create()

    with patch("app.repository.insert") as mock_insert:
        # The repository echoes back whatever record it receives.
        mock_insert.side_effect = lambda r: r

        result = service.create_expense(data)

    assert isinstance(result, ExpenseRecord)


def test_create_expense_generates_uuid_v4():
    """The generated id must be a valid UUID version 4."""
    data = make_expense_create()

    with patch("app.repository.insert") as mock_insert:
        mock_insert.side_effect = lambda r: r

        result = service.create_expense(data)

    assert isinstance(result.id, uuid.UUID)
    assert result.id.version == 4


def test_create_expense_propagates_amount():
    """The amount from the validated input must appear unchanged in the record."""
    data = make_expense_create(amount="123.45")

    with patch("app.repository.insert") as mock_insert:
        mock_insert.side_effect = lambda r: r

        result = service.create_expense(data)

    assert result.amount == Decimal("123.45")


def test_create_expense_propagates_category():
    """The category from the validated input must appear unchanged in the record."""
    data = make_expense_create(category="Transport")

    with patch("app.repository.insert") as mock_insert:
        mock_insert.side_effect = lambda r: r

        result = service.create_expense(data)

    assert result.category == "Transport"


def test_create_expense_propagates_date():
    """The date from the validated input must appear unchanged in the record."""
    data = make_expense_create(date="2026-01-15")

    with patch("app.repository.insert") as mock_insert:
        mock_insert.side_effect = lambda r: r

        result = service.create_expense(data)

    assert result.date == "2026-01-15"


def test_create_expense_propagates_description():
    """The description from the validated input must appear unchanged in the record."""
    data = make_expense_create(description="Taxi to airport")

    with patch("app.repository.insert") as mock_insert:
        mock_insert.side_effect = lambda r: r

        result = service.create_expense(data)

    assert result.description == "Taxi to airport"


def test_create_expense_empty_description_propagates():
    """An absent description (empty string default) must reach the record as ''."""
    data = ExpenseCreate(amount="45.50", category="Food", date="2026-07-22")

    with patch("app.repository.insert") as mock_insert:
        mock_insert.side_effect = lambda r: r

        result = service.create_expense(data)

    assert result.description == ""


def test_two_calls_generate_distinct_ids():
    """Each call to create_expense must produce a unique UUID."""
    data = make_expense_create()
    ids = []

    with patch("app.repository.insert") as mock_insert:
        mock_insert.side_effect = lambda r: r

        ids.append(service.create_expense(data).id)
        ids.append(service.create_expense(data).id)

    assert ids[0] != ids[1]


# ---------------------------------------------------------------------------
# Repository delegation
# ---------------------------------------------------------------------------


def test_create_expense_calls_repository_insert_once():
    """create_expense must call repository.insert exactly once."""
    data = make_expense_create()

    with patch("app.repository.insert") as mock_insert:
        mock_insert.side_effect = lambda r: r
        service.create_expense(data)

    mock_insert.assert_called_once()


def test_create_expense_passes_expense_record_to_repository():
    """The object passed to repository.insert must be an ExpenseRecord."""
    data = make_expense_create()

    with patch("app.repository.insert") as mock_insert:
        mock_insert.side_effect = lambda r: r
        service.create_expense(data)

    args, _ = mock_insert.call_args
    assert isinstance(args[0], ExpenseRecord)


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------


def test_create_expense_propagates_db_unavailable_error():
    """DBUnavailableError from repository must propagate to the caller unchanged."""
    data = make_expense_create()

    with patch("app.repository.insert", side_effect=DBUnavailableError("DB down")):
        with pytest.raises(DBUnavailableError):
            service.create_expense(data)


def test_create_expense_propagates_db_error():
    """DBError from repository must propagate to the caller unchanged."""
    data = make_expense_create()

    with patch("app.repository.insert", side_effect=DBError("General failure")):
        with pytest.raises(DBError):
            service.create_expense(data)
