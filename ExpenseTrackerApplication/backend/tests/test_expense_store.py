import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import expense_store


def sample_expense(**overrides):
    """Build a default sample expense dict, overriding any fields passed as keyword arguments."""
    expense = {"id": "id-1", "description": "Coffee", "amount": 4.5, "date": "2026-01-01", "category": "Food"}
    expense.update(overrides)
    return expense


def test_validate_expense_rejects_empty_description():
    valid, error = expense_store.validate_expense(
        {"description": "   ", "amount": 10, "date": "2026-01-01", "category": "Food"}
    )
    assert valid is False
    assert "description" in error.lower()


def test_validate_expense_rejects_non_positive_amount():
    valid, error = expense_store.validate_expense(
        {"description": "Coffee", "amount": 0, "date": "2026-01-01", "category": "Food"}
    )
    assert valid is False
    assert "amount" in error.lower()


def test_validate_expense_rejects_missing_date():
    valid, error = expense_store.validate_expense(
        {"description": "Coffee", "amount": 5, "date": "", "category": "Food"}
    )
    assert valid is False
    assert "date" in error.lower()


def test_validate_expense_accepts_valid_data():
    valid, error = expense_store.validate_expense(
        {"description": "Coffee", "amount": 5, "date": "2026-01-01", "category": "Food"}
    )
    assert valid is True
    assert error is None


def test_create_expense_trims_description_and_uses_given_id():
    expense = expense_store.create_expense(
        {"description": "  Coffee  ", "amount": 4.5, "date": "2026-01-01", "category": "Food"}, "id-1"
    )
    assert expense == sample_expense()


def test_add_expense_inserts_and_list_returns_it(conn):
    expense = sample_expense()
    expense_store.add_expense(conn, expense)

    result = expense_store.list_expenses(conn)

    assert result == [expense]


def test_update_expense_updates_matching_row_leaving_others_untouched(conn):
    expense_store.add_expense(conn, sample_expense())
    expense_store.add_expense(
        conn, sample_expense(id="id-2", description="Bus", amount=2, date="2026-01-02", category="Transport")
    )

    updated = expense_store.update_expense(
        conn, "id-1", {"description": "Latte", "amount": 5.5, "date": "2026-01-03", "category": "Food"}
    )

    assert updated == {"id": "id-1", "description": "Latte", "amount": 5.5, "date": "2026-01-03", "category": "Food"}
    remaining = {e["id"]: e for e in expense_store.list_expenses(conn)}
    assert remaining["id-2"]["description"] == "Bus"


def test_update_expense_trims_description(conn):
    expense_store.add_expense(conn, sample_expense())
    updated = expense_store.update_expense(
        conn, "id-1", {"description": "  Latte  ", "amount": 5.5, "date": "2026-01-03", "category": "Food"}
    )
    assert updated["description"] == "Latte"


def test_update_expense_returns_none_when_id_not_found(conn):
    expense_store.add_expense(conn, sample_expense())
    updated = expense_store.update_expense(
        conn, "missing-id", {"description": "X", "amount": 1, "date": "2026-01-01", "category": "Food"}
    )
    assert updated is None


def test_delete_expense_removes_the_expense_with_given_id(conn):
    expense_store.add_expense(conn, sample_expense())
    expense_store.add_expense(
        conn, sample_expense(id="id-2", description="Bus", amount=2, date="2026-01-02", category="Transport")
    )

    expense_store.delete_expense(conn, "id-1")

    remaining = expense_store.list_expenses(conn)
    assert len(remaining) == 1
    assert remaining[0]["id"] == "id-2"


def test_delete_expense_is_noop_when_id_not_found(conn):
    expense_store.add_expense(conn, sample_expense())
    expense_store.delete_expense(conn, "missing-id")
    assert len(expense_store.list_expenses(conn)) == 1


def test_get_monthly_summary_totals_only_expenses_within_given_month(conn):
    expense_store.add_expense(conn, sample_expense(id="id-1", amount=10, date="2026-01-05", category="Food"))
    expense_store.add_expense(conn, sample_expense(id="id-2", amount=20, date="2026-01-20", category="Transport"))
    expense_store.add_expense(conn, sample_expense(id="id-3", amount=99, date="2026-02-01", category="Food"))

    summary = expense_store.get_monthly_summary(conn, "2026-01")

    assert summary["total"] == 30


def test_get_monthly_summary_groups_totals_by_category(conn):
    expense_store.add_expense(conn, sample_expense(id="id-1", amount=10, date="2026-01-05", category="Food"))
    expense_store.add_expense(conn, sample_expense(id="id-2", amount=5, date="2026-01-10", category="Food"))
    expense_store.add_expense(conn, sample_expense(id="id-3", amount=20, date="2026-01-20", category="Transport"))

    summary = expense_store.get_monthly_summary(conn, "2026-01")

    assert summary["byCategory"] == {"Food": 15, "Transport": 20}


def test_get_monthly_summary_returns_zero_total_and_empty_breakdown_when_no_match(conn):
    expense_store.add_expense(conn, sample_expense(date="2026-02-01"))
    summary = expense_store.get_monthly_summary(conn, "2026-01")
    assert summary["total"] == 0
    assert summary["byCategory"] == {}
