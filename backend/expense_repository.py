"""Data-access layer for the expenses table. No business logic here."""


def fetch_all(conn):
    """Return all expense rows."""
    return conn.execute("SELECT * FROM expenses").fetchall()


def fetch_by_id(conn, expense_id):
    """Return the expense row with the given id, or None if it doesn't exist."""
    return conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()


def insert(conn, expense):
    """Insert a new expense row from an expense dict (id, description, amount, date, category,
    recurrence, next_occurrence_created)."""
    conn.execute(
        "INSERT INTO expenses (id, description, amount, date, category, recurrence, next_occurrence_created) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            expense["id"],
            expense["description"],
            expense["amount"],
            expense["date"],
            expense["category"],
            expense["recurrence"],
            int(expense["next_occurrence_created"]),
        ),
    )
    conn.commit()


def update(conn, expense_id, expense):
    """Overwrite the fields of the expense row with the given id."""
    conn.execute(
        "UPDATE expenses SET description = ?, amount = ?, date = ?, category = ?, recurrence = ?, "
        "next_occurrence_created = ? WHERE id = ?",
        (
            expense["description"],
            expense["amount"],
            expense["date"],
            expense["category"],
            expense["recurrence"],
            int(expense["next_occurrence_created"]),
            expense_id,
        ),
    )
    conn.commit()


def delete(conn, expense_id):
    """Delete the expense row with the given id, if any."""
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()


def fetch_due_recurring(conn, today):
    """Return recurring expense rows that are due to spawn their next occurrence:
    `recurrence != 'None'`, not yet rolled over, and dated on or before `today` (an ISO date
    string)."""
    return conn.execute(
        "SELECT * FROM expenses WHERE recurrence != 'None' AND next_occurrence_created = 0 AND date <= ?",
        (today,),
    ).fetchall()


def mark_occurrence_created(conn, expense_id):
    """Flag the expense row with the given id as having already had its next occurrence created,
    so a later due-check doesn't spawn a duplicate."""
    conn.execute("UPDATE expenses SET next_occurrence_created = 1 WHERE id = ?", (expense_id,))
    conn.commit()
