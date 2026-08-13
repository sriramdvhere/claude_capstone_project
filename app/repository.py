"""
Expense Repository (IMP-006).

Exposes a single public function:
    insert(record: ExpenseRecord) -> ExpenseRecord

Design decisions:
- amount is serialised to str on INSERT and deserialised to Decimal on SELECT
  (DR-005 / ACH-006).
- Every INSERT is wrapped in an explicit transaction; the transaction is
  committed on success and rolled back on any exception.
- No raw sqlite3 exception escapes this module boundary (NFR-004 / NFR-002).
- DBError      — general persistence failure → caller maps to HTTP 500.
- DBUnavailableError — transient / operational failure → caller maps to HTTP 503.
"""
import sqlite3
from decimal import Decimal

from app.database import get_connection
from app.models import ExpenseRecord

# ---------------------------------------------------------------------------
# Custom exception types
# ---------------------------------------------------------------------------


class DBError(Exception):
    """Raised for unrecoverable database errors (maps to HTTP 500)."""


class DBUnavailableError(Exception):
    """Raised for transient / operational database errors (maps to HTTP 503)."""


# ---------------------------------------------------------------------------
# SQL
# ---------------------------------------------------------------------------

_INSERT_SQL = """
INSERT INTO expenses (id, amount, category, date, description)
VALUES (?, ?, ?, ?, ?)
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def insert(record: ExpenseRecord) -> ExpenseRecord:
    """
    Persist *record* to the expenses table inside an explicit transaction.

    Returns the same record on success.
    Raises DBUnavailableError for sqlite3.OperationalError (transient).
    Raises DBError for all other sqlite3.Error (general failure).
    """
    params = (
        str(record.id),
        str(record.amount),   # store amount as TEXT (DR-005)
        record.category,
        record.date,
        record.description,
    )

    conn = get_connection()
    try:
        conn.execute("BEGIN")
        conn.execute(_INSERT_SQL, params)
        conn.commit()
        return record
    except sqlite3.OperationalError as exc:
        conn.rollback()
        raise DBUnavailableError(str(exc)) from exc
    except sqlite3.Error as exc:
        conn.rollback()
        raise DBError(str(exc)) from exc
    finally:
        conn.close()
