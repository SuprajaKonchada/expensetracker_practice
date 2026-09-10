#!/usr/bin/env python3
"""SessionStart hook: orients Claude Code on the expense tracker architecture
and how to use the SQLite MCP server vs. the application REST API.

Stdlib only, no external dependencies. Reads (and ignores) the hook's JSON
payload on stdin, then prints plain-text guidance to stdout, which Claude
Code injects as session context.
"""
import sys

GUIDANCE = """\
Expense Tracker session guidance:

1. Inspect the existing architecture first (see CLAUDE.md): React frontend
   (frontend/) -> Flask REST API (backend/) -> SQLite (backend/expense_tracker.db).
2. A read-only SQLite MCP server ("sqlite-readonly") is configured for this
   project, exposing: list_tables, describe_table, list_foreign_keys, read_query.
3. Use the SQLite MCP server for database inspection and querying (schema
   checks, ad-hoc SELECTs). It is read-only, so it cannot perform data
   manipulation (INSERT/UPDATE/DELETE) - do not rely on the REST API just to
   look at data when the MCP server can answer it directly.
4. Use the application's REST API (backend/routes_*.py) when implementing or
   testing application behavior, and for any data manipulation (creating,
   updating, deleting expenses/budgets).
5. This guidance is informational only - do not modify application code
   based solely on this startup analysis.
"""


def main() -> int:
    sys.stdin.read()
    print(GUIDANCE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
