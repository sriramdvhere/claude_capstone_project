"""
Unit tests for the Validation Layer (IMP-010).

Tests exercise ExpenseCreate directly — no HTTP layer involved.
Every test checks either the happy path or one of the seven exact error
message strings required by docs/requirements.md Section 8.
"""
import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.models import ExpenseCreate


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_valid_expense_is_accepted():
    expense = ExpenseCreate(
        amount="45.50",
        category="Food",
        date="2026-07-22",
        description="Lunch at the office cafeteria",
    )
    assert expense.amount == Decimal("45.50")
    assert expense.category == "Food"
    assert expense.date == "2026-07-22"
    assert expense.description == "Lunch at the office cafeteria"


def test_description_absent_defaults_to_empty_string():
    expense = ExpenseCreate(amount="45.50", category="Food", date="2026-07-22")
    assert expense.description == ""


def test_valid_expense_with_integer_amount():
    expense = ExpenseCreate(amount=10, category="Transport", date="2026-07-22")
    assert expense.amount == Decimal("10")


def test_valid_expense_with_float_amount():
    expense = ExpenseCreate(amount=9.99, category="Food", date="2026-07-22")
    assert expense.amount > 0


# ---------------------------------------------------------------------------
# amount — must be greater than zero (AC-002)
# ---------------------------------------------------------------------------


def test_amount_zero_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount=0, category="Food", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "amount must be greater than zero" in messages


def test_amount_zero_string_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="0", category="Food", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "amount must be greater than zero" in messages


def test_amount_negative_integer_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount=-1, category="Food", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "amount must be greater than zero" in messages


def test_amount_negative_float_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount=-10.00, category="Food", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "amount must be greater than zero" in messages


# ---------------------------------------------------------------------------
# amount — must be a valid number
# ---------------------------------------------------------------------------


def test_amount_non_numeric_string_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="abc", category="Food", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "amount must be a valid number" in messages


def test_amount_boolean_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount=True, category="Food", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "amount must be a valid number" in messages


def test_amount_none_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount=None, category="Food", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "amount must be a valid number" in messages


# ---------------------------------------------------------------------------
# category — is required (blank / whitespace)
# ---------------------------------------------------------------------------


def test_category_empty_string_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="45.50", category="", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "category is required" in messages


def test_category_whitespace_only_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="45.50", category="   ", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "category is required" in messages


def test_category_tab_only_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="45.50", category="\t\n", date="2026-07-22")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "category is required" in messages


# ---------------------------------------------------------------------------
# category — maximum 100 characters (DR-004)
# ---------------------------------------------------------------------------


def test_category_exactly_100_chars_is_accepted():
    expense = ExpenseCreate(
        amount="45.50", category="a" * 100, date="2026-07-22"
    )
    assert len(expense.category) == 100


def test_category_101_chars_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="45.50", category="a" * 101, date="2026-07-22")
    assert len(exc_info.value.errors()) > 0


# ---------------------------------------------------------------------------
# category — whitespace is stripped (DR-006)
# ---------------------------------------------------------------------------


def test_category_whitespace_is_stripped():
    expense = ExpenseCreate(amount="45.50", category="  Food  ", date="2026-07-22")
    assert expense.category == "Food"


# ---------------------------------------------------------------------------
# date — is required (absent)
# ---------------------------------------------------------------------------


def test_date_absent_raises_missing_type_error():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="45.50", category="Food")
    types = [e["type"] for e in exc_info.value.errors()]
    assert "missing" in types


# ---------------------------------------------------------------------------
# date — must be in YYYY-MM-DD format
# ---------------------------------------------------------------------------


def test_date_wrong_format_dd_mm_yyyy_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="45.50", category="Food", date="22-07-2026")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "date must be in YYYY-MM-DD format" in messages


def test_date_with_time_component_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="45.50", category="Food", date="2026-07-22T00:00:00")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "date must be in YYYY-MM-DD format" in messages


def test_date_plain_text_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(amount="45.50", category="Food", date="not-a-date")
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "date must be in YYYY-MM-DD format" in messages


# ---------------------------------------------------------------------------
# description — must not exceed 500 characters
# ---------------------------------------------------------------------------


def test_description_exactly_500_chars_is_accepted():
    expense = ExpenseCreate(
        amount="45.50",
        category="Food",
        date="2026-07-22",
        description="a" * 500,
    )
    assert len(expense.description) == 500


def test_description_501_chars_raises_correct_message():
    with pytest.raises(ValidationError) as exc_info:
        ExpenseCreate(
            amount="45.50",
            category="Food",
            date="2026-07-22",
            description="a" * 501,
        )
    messages = [e["msg"] for e in exc_info.value.errors()]
    assert "description must not exceed 500 characters" in messages
