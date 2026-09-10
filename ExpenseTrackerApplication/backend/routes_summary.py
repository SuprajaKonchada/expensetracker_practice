"""Blueprint: /api/summary"""
from flask import Blueprint, current_app, jsonify, request

import budget_store
import expense_store

summary_bp = Blueprint("summary", __name__, url_prefix="/api/summary")


def _get_conn():
    return current_app.config["GET_CONN"]()


@summary_bp.get("")
def get_summary():
    """GET /api/summary?month=YYYY-MM: return that month's total, per-category spend, and
    budget statuses. Budget statuses are computed only when the month parameter is valid;
    otherwise they're returned as an empty list.
    """
    month = request.args.get("month", "")
    conn = _get_conn()
    try:
        summary = expense_store.get_monthly_summary(conn, month)
        budgets = budget_store.list_budgets(conn, month) if budget_store.is_valid_month(month) else {}
        statuses = budget_store.get_budget_statuses(budgets, summary["byCategory"])
        return jsonify(
            {
                "total": summary["total"],
                "byCategory": summary["byCategory"],
                "budgetStatuses": statuses,
            }
        )
    finally:
        conn.close()
