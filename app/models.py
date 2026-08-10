"""
Pydantic domain models for the Expense Tracker (IMP-003 + IMP-004).

ExpenseCreate  — inbound request body (no id).
ExpenseRecord  — full domain entity stored in the database.
ExpenseResponse — serialised HTTP response (FR-004).

All field validators use pydantic_core.PydanticCustomError so that the
exact error message strings from requirements Section 8 appear in the
error response without Pydantic's default "Value error, " prefix.
"""
import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from pydantic import BaseModel, field_serializer, field_validator
from pydantic_core import PydanticCustomError


class ExpenseCreate(BaseModel):
    """Validated inbound payload for creating an expense."""

    amount: Decimal
    category: str
    date: str
    description: Optional[str] = ""

    # ------------------------------------------------------------------
    # amount validator (DR-003)
    # ------------------------------------------------------------------
    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v: object) -> Decimal:
        """
        Accept int, float, str, or Decimal and convert to Decimal.
        Reject non-numeric values with "amount must be a valid number".
        Reject zero or negative values with "amount must be greater than zero".
        """
        if isinstance(v, bool):
            # bool is a subclass of int; treat it as non-numeric
            raise PydanticCustomError(
                "amount_invalid",
                "amount must be a valid number",
            )
        if isinstance(v, (int, float)):
            try:
                v = Decimal(str(v))
            except InvalidOperation:
                raise PydanticCustomError(
                    "amount_invalid",
                    "amount must be a valid number",
                )
        elif isinstance(v, str):
            try:
                v = Decimal(v)
            except InvalidOperation:
                raise PydanticCustomError(
                    "amount_invalid",
                    "amount must be a valid number",
                )
        elif not isinstance(v, Decimal):
            raise PydanticCustomError(
                "amount_invalid",
                "amount must be a valid number",
            )

        if v <= 0:
            raise PydanticCustomError(
                "amount_not_positive",
                "amount must be greater than zero",
            )

        return v

    # ------------------------------------------------------------------
    # category validator (DR-003, DR-004, DR-006)
    # ------------------------------------------------------------------
    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: object) -> str:
        """
        Strip whitespace, reject blank/whitespace-only values with
        "category is required", enforce 100-character maximum (DR-004).
        Returns the stripped value (DR-006).
        """
        if v is None:
            raise PydanticCustomError("category_required", "category is required")

        if not isinstance(v, str):
            v = str(v)

        v_stripped = v.strip()

        if not v_stripped:
            raise PydanticCustomError("category_required", "category is required")

        if len(v_stripped) > 100:
            raise PydanticCustomError(
                "category_too_long",
                "category must not exceed 100 characters",
            )

        return v_stripped  # store the stripped value (DR-006)

    # ------------------------------------------------------------------
    # date validator (DR-003)
    # ------------------------------------------------------------------
    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, v: object) -> str:
        """
        Reject null with "date is required".
        Reject values that do not match YYYY-MM-DD with
        "date must be in YYYY-MM-DD format".
        """
        if v is None:
            raise PydanticCustomError("date_required", "date is required")

        if not isinstance(v, str):
            v = str(v)

        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise PydanticCustomError(
                "date_invalid_format",
                "date must be in YYYY-MM-DD format",
            )

        return v

    # ------------------------------------------------------------------
    # description validator (DR-003, DR-004)
    # ------------------------------------------------------------------
    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: object) -> str:
        """
        Treat absent or null description as empty string.
        Enforce 500-character maximum (DR-004).
        """
        if v is None:
            return ""

        if not isinstance(v, str):
            v = str(v)

        if len(v) > 500:
            raise PydanticCustomError(
                "description_too_long",
                "description must not exceed 500 characters",
            )

        return v


class ExpenseRecord(BaseModel):
    """Full expense entity as stored in (and read from) the database."""

    id: uuid.UUID
    amount: Decimal
    category: str
    date: str
    description: str = ""


class ExpenseResponse(BaseModel):
    """HTTP response body returned to the caller (FR-004)."""

    id: uuid.UUID
    amount: Decimal
    category: str
    date: str
    description: str

    @field_serializer("amount")
    def serialize_amount(self, v: Decimal) -> float:
        """
        Serialize Decimal amount as a JSON number (float).

        Pydantic v2 serializes Decimal as a string by default; this serializer
        ensures the response matches the FR-004 example ("amount": 45.50).
        """
        return float(v)
