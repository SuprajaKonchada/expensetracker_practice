"""Data-access layer for the budgets table. No business logic here."""


def fetch_all_for_month(conn, month):
    """Return all budget rows for the given month."""
    return conn.execute("SELECT * FROM budgets WHERE month = ?", (month,)).fetchall()


def upsert(conn, category, month, amount):
    """Insert a budget for (category, month), or update its amount if one already exists."""
    conn.execute(
        "INSERT INTO budgets (category, month, amount) VALUES (?, ?, ?) "
        "ON CONFLICT(category, month) DO UPDATE SET amount = excluded.amount",
        (category, month, amount),
    )
    conn.commit()


def remove(conn, category, month):
    """Delete the budget for the given category and month, if any."""
    conn.execute("DELETE FROM budgets WHERE category = ? AND month = ?", (category, month))
    conn.commit()
