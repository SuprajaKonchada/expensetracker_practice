"""Expense business logic. Mirrors js/expenseStore.js. Persistence delegated to expense_repository."""
import calendar
import math
import uuid
from datetime import date, timedelta

import constants
import expense_repository


def validate_expense(data):
    """Validate an incoming expense payload.

    Returns a (valid, error) tuple: (True, None) if `data` has a non-blank description,
    a positive numeric amount, a date, a category, and (if present) a recurrence that's one
    of `constants.RECURRENCE_OPTIONS`; otherwise (False, message) with a user-facing error
    message describing the first problem found. An absent or `None` recurrence is fine — it
    defaults to "None" at creation time.
    """
    description = data.get("description")
    amount = data.get("amount")
    date_value = data.get("date")
    category = data.get("category")
    recurrence = data.get("recurrence")

    if not description or not str(description).strip():
        return False, "Please enter a description."
    if not isinstance(amount, (int, float)) or isinstance(amount, bool):
        return False, "Please enter a valid amount greater than 0."
    if math.isnan(amount) or amount <= 0:
        return False, "Please enter a valid amount greater than 0."
    if not date_value:
        return False, "Please select a date."
    if not category:
        return False, "Please select a category."
    if recurrence is not None and recurrence not in constants.RECURRENCE_OPTIONS:
        return False, "Please select a valid recurrence."
    return True, None


def _row_to_expense(row):
    """Convert a sqlite3.Row from the expenses table into a plain, public expense dict.

    `next_occurrence_created` is internal bookkeeping and is intentionally omitted here.
    """
    return {
        "id": row["id"],
        "description": row["description"],
        "amount": row["amount"],
        "date": row["date"],
        "category": row["category"],
        "recurrence": row["recurrence"],
    }


def create_expense(data, expense_id=None):
    """Build a new expense dict from validated input data, trimming the description.

    Uses `expense_id` if given, otherwise generates a new UUID. `recurrence` defaults to
    "None" when absent, and `next_occurrence_created` always starts False.
    """
    return {
        "id": expense_id or str(uuid.uuid4()),
        "description": str(data["description"]).strip(),
        "amount": data["amount"],
        "date": data["date"],
        "category": data["category"],
        "recurrence": data.get("recurrence") or "None",
        "next_occurrence_created": False,
    }


def next_due_date(due_date, recurrence):
    """Return the ISO date string of the next occurrence after `due_date` for `recurrence`,
    or None for "None".

    "Weekly" adds 7 days. "Monthly" advances to the same day-of-month next month, clamped to
    that month's actual last day (e.g. 2026-01-31 -> 2026-02-28).
    """
    if recurrence == "Weekly":
        return (date.fromisoformat(due_date) + timedelta(days=7)).isoformat()
    if recurrence == "Monthly":
        current = date.fromisoformat(due_date)
        if current.month == 12:
            next_year, next_month = current.year + 1, 1
        else:
            next_year, next_month = current.year, current.month + 1
        last_day_of_next_month = calendar.monthrange(next_year, next_month)[1]
        next_day = min(current.day, last_day_of_next_month)
        return date(next_year, next_month, next_day).isoformat()
    return None


def roll_over_due_expenses(conn):
    """Spawn the next occurrence for every recurring expense that's due (date <= today) and
    hasn't already had its next occurrence created.

    Each due expense gets a brand-new expense row (fresh id, same description/amount/category/
    recurrence, date advanced by `next_due_date`), and the original row is flagged via
    `expense_repository.mark_occurrence_created` so a later call doesn't create a duplicate.
    The original row's other fields are left untouched. Returns the list of newly created
    expense dicts.
    """
    today = date.today().isoformat()
    due_rows = expense_repository.fetch_due_recurring(conn, today)

    created = []
    for row in due_rows:
        next_occurrence = {
            "id": str(uuid.uuid4()),
            "description": row["description"],
            "amount": row["amount"],
            "date": next_due_date(row["date"], row["recurrence"]),
            "category": row["category"],
            "recurrence": row["recurrence"],
            "next_occurrence_created": False,
        }
        expense_repository.insert(conn, next_occurrence)
        expense_repository.mark_occurrence_created(conn, row["id"])
        created.append(next_occurrence)

    return created


def list_expenses(conn):
    """Roll over any due recurring expenses, then return all expenses as a list of expense dicts."""
    roll_over_due_expenses(conn)
    rows = expense_repository.fetch_all(conn)
    return [_row_to_expense(r) for r in rows]


def add_expense(conn, expense):
    """Persist a new expense and return its public shape (internal `next_occurrence_created`
    bookkeeping is not part of the API response, matching `update_expense`)."""
    expense_repository.insert(conn, expense)
    return {k: v for k, v in expense.items() if k != "next_occurrence_created"}


def update_expense(conn, expense_id, data):
    """Update the expense with the given id from validated input data.

    Returns the updated expense dict, or None if no expense exists with that id. The
    internal `next_occurrence_created` flag is preserved from the existing row (editing an
    expense doesn't reset its rollover bookkeeping).
    """
    row = expense_repository.fetch_by_id(conn, expense_id)
    if row is None:
        return None
    full = {
        "id": expense_id,
        "description": str(data["description"]).strip(),
        "amount": data["amount"],
        "date": data["date"],
        "category": data["category"],
        "recurrence": data.get("recurrence") or "None",
        "next_occurrence_created": row["next_occurrence_created"],
    }
    expense_repository.update(conn, expense_id, full)
    return {k: v for k, v in full.items() if k != "next_occurrence_created"}


def delete_expense(conn, expense_id):
    """Delete the expense with the given id. No-op if it doesn't exist."""
    expense_repository.delete(conn, expense_id)


def get_monthly_summary(conn, month):
    """Compute the total spend and per-category breakdown for expenses dated within `month`.

    Rolls over any due recurring expenses first, so the summary is correct even if
    `/api/expenses` hasn't been called yet in this session. `month` is matched as a
    "YYYY-MM" date prefix. Returns {"total": float, "byCategory": dict}.
    """
    roll_over_due_expenses(conn)
    rows = expense_repository.fetch_all(conn)
    total = 0.0
    by_category = {}

    for row in rows:
        if not row["date"].startswith(month or ""):
            continue
        total += row["amount"]
        by_category[row["category"]] = by_category.get(row["category"], 0) + row["amount"]

    return {"total": total, "byCategory": by_category}
