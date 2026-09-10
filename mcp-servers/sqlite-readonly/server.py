"""Read-only MCP server for inspecting the Expense Tracker SQLite database.

Runs as a standalone process outside the Flask application (backend/) and the
React app (frontend/) — it never imports or modifies either. It opens exactly
one database file, given by SQLITE_DB_PATH, using SQLite's own read-only URI
mode so writes fail at the engine level even if a tool's own validation were
ever bypassed. Only schema-inspection and SELECT/WITH querying are exposed;
there is no write_query, create_table, or ATTACH DATABASE capability.
"""
import os
import sqlite3
from pathlib import Path

from mcp.server.mcpserver import MCPServer

DB_PATH = Path(os.environ["SQLITE_DB_PATH"]).resolve()
MAX_ROWS = 200

server = MCPServer("sqlite-readonly")


def _connect() -> sqlite3.Connection:
    """Open DB_PATH in hard, OS-enforced read-only mode (SQLite rejects any write)."""
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"Configured SQLITE_DB_PATH does not exist: {DB_PATH}")
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _table_names(conn: sqlite3.Connection) -> set[str]:
    """Return real table names, used to validate identifiers before they reach a PRAGMA."""
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return {row["name"] for row in rows}


@server.tool()
def list_tables() -> list[str]:
    """List every table in the expense tracker database."""
    conn = _connect()
    try:
        return sorted(_table_names(conn))
    finally:
        conn.close()


@server.tool()
def describe_table(table_name: str) -> list[dict]:
    """Describe a table's columns: name, declared type, NOT NULL, default value, and primary-key position."""
    conn = _connect()
    try:
        if table_name not in _table_names(conn):
            raise ValueError(f"Unknown table: {table_name}")
        rows = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@server.tool()
def list_foreign_keys(table_name: str) -> list[dict]:
    """List a table's declared foreign key constraints, if any."""
    conn = _connect()
    try:
        if table_name not in _table_names(conn):
            raise ValueError(f"Unknown table: {table_name}")
        rows = conn.execute(f'PRAGMA foreign_key_list("{table_name}")').fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@server.tool()
def read_query(sql: str) -> list[dict]:
    """Run a single read-only SELECT/WITH query (results capped at 200 rows).

    Rejects anything but one SELECT or WITH statement; the underlying connection is
    also opened read-only, so writes fail even if this check were ever bypassed.
    """
    cleaned = sql.strip().rstrip(";")
    if ";" in cleaned:
        raise ValueError("Only a single statement is allowed")
    if not cleaned.lower().startswith(("select", "with")):
        raise ValueError("Only SELECT and WITH (read-only) statements are allowed")
    conn = _connect()
    try:
        rows = conn.execute(cleaned).fetchmany(MAX_ROWS)
        return [dict(row) for row in rows]
    finally:
        conn.close()


if __name__ == "__main__":
    server.run()
