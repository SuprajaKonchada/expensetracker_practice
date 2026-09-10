"""Expense business logic. Mirrors js/expenseStore.js. Persistence delegated to expense_repository."""
import math
import uuid

import expense_repository


def validate_expense(data):
    """Validate an incoming expense payload.

    Returns a (valid, error) tuple: (True, None) if `data` has a non-blank description,
    a positive numeric amount, a date, and a category; otherwise (False, message) with a
    user-facing error message describing the first problem found.
    """
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")

    if not description or not str(description).strip():
        return False, "Please enter a description."
    if not isinstance(amount, (int, float)) or isinstance(amount, bool):
        return False, "Please enter a valid amount greater than 0."
    if math.isnan(amount) or amount <= 0:
        return False, "Please enter a valid amount greater than 0."
    if not date:
        return False, "Please select a date."
    if not category:
        return False, "Please select a category."
    return True, None


def _row_to_expense(row):
    """Convert a sqlite3.Row from the expenses table into a plain expense dict."""
    return {
        "id": row["id"],
        "description": row["description"],
        "amount": row["amount"],
        "date": row["date"],
        "category": row["category"],
    }


def create_expense(data, expense_id=None):
    """Build a new expense dict from validated input data, trimming the description.

    Uses `expense_id` if given, otherwise generates a new UUID.
    """
    return {
        "id": expense_id or str(uuid.uuid4()),
        "description": str(data["description"]).strip(),
        "amount": data["amount"],
        "date": data["date"],
        "category": data["category"],
    }


def list_expenses(conn):
    """Return all expenses as a list of expense dicts."""
    rows = expense_repository.fetch_all(conn)
    return [_row_to_expense(r) for r in rows]


def add_expense(conn, expense):
    """Persist a new expense and return it unchanged."""
    expense_repository.insert(conn, expense)
    return expense


def update_expense(conn, expense_id, data):
    """Update the expense with the given id from validated input data.

    Returns the updated expense dict, or None if no expense exists with that id.
    """
    row = expense_repository.fetch_by_id(conn, expense_id)
    if row is None:
        return None
    updated = {
        "id": expense_id,
        "description": str(data["description"]).strip(),
        "amount": data["amount"],
        "date": data["date"],
        "category": data["category"],
    }
    expense_repository.update(conn, expense_id, updated)
    return updated


def delete_expense(conn, expense_id):
    """Delete the expense with the given id. No-op if it doesn't exist."""
    expense_repository.delete(conn, expense_id)


def get_monthly_summary(conn, month):
    """Compute the total spend and per-category breakdown for expenses dated within `month`.

    `month` is matched as a "YYYY-MM" date prefix. Returns {"total": float, "byCategory": dict}.
    """
    rows = expense_repository.fetch_all(conn)
    total = 0.0
    by_category = {}

    for row in rows:
        if not row["date"].startswith(month or ""):
            continue
        total += row["amount"]
        by_category[row["category"]] = by_category.get(row["category"], 0) + row["amount"]

    return {"total": total, "byCategory": by_category}
