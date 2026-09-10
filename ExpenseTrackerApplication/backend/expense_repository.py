"""Data-access layer for the expenses table. No business logic here."""


def fetch_all(conn):
    """Return all expense rows."""
    return conn.execute("SELECT * FROM expenses").fetchall()


def fetch_by_id(conn, expense_id):
    """Return the expense row with the given id, or None if it doesn't exist."""
    return conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()


def insert(conn, expense):
    """Insert a new expense row from an expense dict (id, description, amount, date, category)."""
    conn.execute(
        "INSERT INTO expenses (id, description, amount, date, category) VALUES (?, ?, ?, ?, ?)",
        (expense["id"], expense["description"], expense["amount"], expense["date"], expense["category"]),
    )
    conn.commit()


def update(conn, expense_id, expense):
    """Overwrite the fields of the expense row with the given id."""
    conn.execute(
        "UPDATE expenses SET description = ?, amount = ?, date = ?, category = ? WHERE id = ?",
        (expense["description"], expense["amount"], expense["date"], expense["category"], expense_id),
    )
    conn.commit()


def delete(conn, expense_id):
    """Delete the expense row with the given id, if any."""
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
