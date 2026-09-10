"""Blueprint: /api/budgets"""
from flask import Blueprint, current_app, jsonify, request

import budget_store
from constants import CATEGORIES

budgets_bp = Blueprint("budgets", __name__, url_prefix="/api/budgets")

MONTH_ERROR = "A valid month (YYYY-MM) query parameter is required."


def _get_conn():
    return current_app.config["GET_CONN"]()


def _get_month_param():
    """Return the request's "month" query parameter if it's valid YYYY-MM, else None."""
    month = request.args.get("month", "")
    return month if budget_store.is_valid_month(month) else None


@budgets_bp.get("")
def get_budgets():
    """GET /api/budgets?month=YYYY-MM: return that month's budgets as {category: amount}.

    400s with an error message if the month parameter is missing or malformed.
    """
    month = _get_month_param()
    if month is None:
        return jsonify({"error": MONTH_ERROR}), 400

    conn = _get_conn()
    try:
        return jsonify(budget_store.list_budgets(conn, month))
    finally:
        conn.close()


@budgets_bp.put("/<category>")
def set_budget(category):
    """PUT /api/budgets/<category>?month=YYYY-MM: set (or remove) a category's budget for the month.

    Body must be JSON with an "amount" field. 400s if the category is unknown, the month
    parameter is missing/malformed, or "amount" is absent. Returns the month's updated budgets.
    """
    if category not in CATEGORIES:
        return jsonify({"error": "Unknown category."}), 400

    month = _get_month_param()
    if month is None:
        return jsonify({"error": MONTH_ERROR}), 400

    data = request.get_json(silent=True) or {}
    if "amount" not in data:
        return jsonify({"error": "amount is required."}), 400

    conn = _get_conn()
    try:
        budgets = budget_store.set_budget(conn, category, month, data["amount"])
        return jsonify(budgets)
    finally:
        conn.close()
