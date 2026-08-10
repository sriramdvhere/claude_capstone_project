"""
Expense Service (IMP-007).

Implements the single use case "record a new expense":
  1. Accept a validated ExpenseCreate value object.
  2. Generate a UUID v4 identifier (FR-002).
  3. Construct an ExpenseRecord.
  4. Delegate persistence to the repository.
  5. Return the persisted record.

DBError and DBUnavailableError from the repository are propagated to the
caller without being swallowed here.
"""
import uuid

from app import repository
from app.models import ExpenseCreate, ExpenseRecord


def create_expense(data: ExpenseCreate) -> ExpenseRecord:
    """
    Create and persist a new expense record.

    Args:
        data: A fully validated ExpenseCreate instance.

    Returns:
        The persisted ExpenseRecord (including the generated UUID).

    Raises:
        repository.DBUnavailableError: Propagated from the repository on
            transient database failure.
        repository.DBError: Propagated from the repository on general
            database failure.
    """
    record = ExpenseRecord(
        id=uuid.uuid4(),
        amount=data.amount,
        category=data.category,
        date=data.date,
        description=data.description,
    )
    return repository.insert(record)
