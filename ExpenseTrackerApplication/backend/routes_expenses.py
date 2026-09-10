"""Blueprint: /api/expenses"""
from flask import Blueprint, current_app, jsonify, request

import expense_store

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/expenses")


def _get_conn():
    return current_app.config["GET_CONN"]()


@expenses_bp.get("")
def get_expenses():
    """GET /api/expenses: return all expenses."""
    conn = _get_conn()
    try:
        return jsonify(expense_store.list_expenses(conn))
    finally:
        conn.close()


@expenses_bp.post("")
def create_expense():
    """POST /api/expenses: create a new expense from the JSON body.

    400s with an error message if the payload fails validation. Returns the created
    expense with a 201 status.
    """
    data = request.get_json(silent=True) or {}
    valid, error = expense_store.validate_expense(data)
    if not valid:
        return jsonify({"error": error}), 400

    conn = _get_conn()
    try:
        expense = expense_store.create_expense(data)
        expense_store.add_expense(conn, expense)
        return jsonify(expense), 201
    finally:
        conn.close()


@expenses_bp.put("/<expense_id>")
def update_expense(expense_id):
    """PUT /api/expenses/<expense_id>: update an existing expense from the JSON body.

    400s with an error message if the payload fails validation; 404s if no expense
    exists with that id. Returns the updated expense.
    """
    data = request.get_json(silent=True) or {}
    valid, error = expense_store.validate_expense(data)
    if not valid:
        return jsonify({"error": error}), 400

    conn = _get_conn()
    try:
        updated = expense_store.update_expense(conn, expense_id, data)
        if updated is None:
            return jsonify({"error": "Expense not found."}), 404
        return jsonify(updated)
    finally:
        conn.close()


@expenses_bp.delete("/<expense_id>")
def delete_expense(expense_id):
    """DELETE /api/expenses/<expense_id>: delete an expense. Returns 204 whether or not it existed."""
    conn = _get_conn()
    try:
        expense_store.delete_expense(conn, expense_id)
        return "", 204
    finally:
        conn.close()
