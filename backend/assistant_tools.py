"""Tool implementations exposed to the AI Expense Assistant's agentic loop
(assistant_agent.py, which wraps these in Claude Agent SDK `@tool`-decorated closures).

Each tool function takes `conn` (a live sqlite3 connection, injected by the caller) plus
keyword arguments, and returns a JSON-serializable dict. All business logic is delegated to
the existing store modules (`expense_store`, `budget_store`) — this module only adapts their
inputs/outputs to a uniform shape, plus light in-memory filtering for listing.
"""
import logging

import budget_store
import expense_store

logger = logging.getLogger(__name__)


def list_expenses(conn, category=None, month=None):
    """List expenses, optionally filtered by exact category and/or "YYYY-MM" month prefix."""
    expenses = expense_store.list_expenses(conn)
    if category:
        expenses = [e for e in expenses if e["category"] == category]
    if month:
        expenses = [e for e in expenses if e["date"].startswith(month)]
    return {"expenses": expenses}


def create_expense(conn, description=None, amount=None, date=None, category=None, recurrence=None):
    """Validate and create a new expense, mirroring the POST /api/expenses route."""
    data = {
        "description": description,
        "amount": amount,
        "date": date,
        "category": category,
        "recurrence": recurrence,
    }
    valid, error = expense_store.validate_expense(data)
    if not valid:
        return {"error": error}

    expense = expense_store.create_expense(data)
    return expense_store.add_expense(conn, expense)


def update_expense(conn, id=None, description=None, amount=None, date=None, category=None, recurrence=None):
    """Validate and update an existing expense, mirroring the PUT /api/expenses/<id> route."""
    data = {
        "description": description,
        "amount": amount,
        "date": date,
        "category": category,
        "recurrence": recurrence,
    }
    valid, error = expense_store.validate_expense(data)
    if not valid:
        return {"error": error}

    updated = expense_store.update_expense(conn, id, data)
    if updated is None:
        return {"error": "Expense not found."}
    return updated


def delete_expense(conn, id=None):
    """Delete an expense by id. Idempotent, matching DELETE /api/expenses/<id>."""
    expense_store.delete_expense(conn, id)
    return {"deleted": True, "id": id}


def get_budgets(conn, month=None):
    """Return a month's budgets as {category: amount}."""
    if not budget_store.is_valid_month(month):
        return {"error": "Invalid month."}
    return budget_store.list_budgets(conn, month)


def get_monthly_summary(conn, month=None):
    """Return a month's total spend, per-category breakdown, and budget statuses, mirroring
    GET /api/summary."""
    summary = expense_store.get_monthly_summary(conn, month)
    budgets = budget_store.list_budgets(conn, month) if budget_store.is_valid_month(month) else {}
    statuses = budget_store.get_budget_statuses(budgets, summary["byCategory"])
    return {
        "total": summary["total"],
        "byCategory": summary["byCategory"],
        "budgetStatuses": statuses,
    }


_TOOL_FUNCTIONS = {
    "list_expenses": list_expenses,
    "create_expense": create_expense,
    "update_expense": update_expense,
    "delete_expense": delete_expense,
    "get_budgets": get_budgets,
    "get_monthly_summary": get_monthly_summary,
}


def execute_tool(conn, name, arguments):
    """Look up and run the named tool with `arguments` (a dict of keyword args).

    Returns the tool's result dict, or `{"error": "..."}` for an unknown tool name or an
    unexpected exception during execution. Unexpected exceptions are logged server-side but
    never leaked to the caller, so an agentic loop can safely keep going after a tool failure.
    """
    tool_function = _TOOL_FUNCTIONS.get(name)
    if tool_function is None:
        return {"error": f"Unknown tool: {name}"}

    try:
        return tool_function(conn, **(arguments or {}))
    except Exception:
        logger.exception("Tool execution failed: %s", name)
        return {"error": "Tool execution failed."}
