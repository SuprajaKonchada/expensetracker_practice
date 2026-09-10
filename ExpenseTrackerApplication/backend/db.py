"""SQLite connection and schema management."""
import sqlite3
from datetime import date

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS budgets (
    category TEXT NOT NULL,
    month TEXT NOT NULL,
    amount REAL NOT NULL,
    PRIMARY KEY (category, month)
);
"""


def get_connection(db_path=None):
    """Open a SQLite connection with row access by column name and foreign keys enabled.

    Uses `db_path` if given, otherwise falls back to `config.DB_PATH`.
    """
    conn = sqlite3.connect(db_path or config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate_legacy_budgets(conn):
    """Upgrade a pre-monthly budgets table (category PRIMARY KEY, no month) to (category, month).

    Existing recurring budgets are carried forward onto the current month, since that's the
    closest still-meaningful interpretation of a value that previously applied to every month.
    """
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(budgets)")]
    if not columns or "month" in columns:
        return

    current_month = date.today().strftime("%Y-%m")
    conn.execute("ALTER TABLE budgets RENAME TO budgets_legacy")
    conn.execute(
        "CREATE TABLE budgets (category TEXT NOT NULL, month TEXT NOT NULL, amount REAL NOT NULL, "
        "PRIMARY KEY (category, month))"
    )
    conn.execute(
        "INSERT INTO budgets (category, month, amount) SELECT category, ?, amount FROM budgets_legacy",
        (current_month,),
    )
    conn.execute("DROP TABLE budgets_legacy")
    conn.commit()


def init_db(db_path=None):
    """Initialize the database at `db_path` (or the configured default): migrate a legacy
    budgets table if present, then ensure the current schema exists."""
    conn = get_connection(db_path)
    try:
        _migrate_legacy_budgets(conn)
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
