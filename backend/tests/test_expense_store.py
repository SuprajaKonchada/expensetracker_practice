import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import expense_store


def sample_expense(**overrides):
    """Build a default sample expense dict, overriding any fields passed as keyword arguments."""
    expense = {
        "id": "id-1",
        "description": "Coffee",
        "amount": 4.5,
        "date": "2026-01-01",
        "category": "Food",
        "recurrence": "None",
        "next_occurrence_created": False,
    }
    expense.update(overrides)
    return expense


def public(expense):
    """Strip the internal-only `next_occurrence_created` field, matching the shape returned by
    list_expenses/add_expense/update_expense."""
    return {k: v for k, v in expense.items() if k != "next_occurrence_created"}


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

    assert result == [public(expense)]


def test_update_expense_updates_matching_row_leaving_others_untouched(conn):
    expense_store.add_expense(conn, sample_expense())
    expense_store.add_expense(
        conn, sample_expense(id="id-2", description="Bus", amount=2, date="2026-01-02", category="Transport")
    )

    updated = expense_store.update_expense(
        conn, "id-1", {"description": "Latte", "amount": 5.5, "date": "2026-01-03", "category": "Food"}
    )

    assert updated == {
        "id": "id-1",
        "description": "Latte",
        "amount": 5.5,
        "date": "2026-01-03",
        "category": "Food",
        "recurrence": "None",
    }
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


def test_validate_expense_accepts_payload_with_no_recurrence_key():
    valid, error = expense_store.validate_expense(
        {"description": "Coffee", "amount": 5, "date": "2026-01-01", "category": "Food"}
    )
    assert valid is True
    assert error is None


def test_validate_expense_accepts_each_valid_recurrence_option():
    for recurrence in ["None", "Weekly", "Monthly"]:
        valid, error = expense_store.validate_expense(
            {"description": "Coffee", "amount": 5, "date": "2026-01-01", "category": "Food", "recurrence": recurrence}
        )
        assert valid is True
        assert error is None


def test_validate_expense_rejects_invalid_recurrence():
    valid, error = expense_store.validate_expense(
        {"description": "Coffee", "amount": 5, "date": "2026-01-01", "category": "Food", "recurrence": "Daily"}
    )
    assert valid is False
    assert "recurrence" in error.lower()

    valid, error = expense_store.validate_expense(
        {"description": "Coffee", "amount": 5, "date": "2026-01-01", "category": "Food", "recurrence": "Yearly"}
    )
    assert valid is False
    assert "recurrence" in error.lower()


def test_next_due_date_weekly_adds_seven_days():
    assert expense_store.next_due_date("2026-01-01", "Weekly") == "2026-01-08"


def test_next_due_date_monthly_advances_same_day_of_month():
    assert expense_store.next_due_date("2026-01-15", "Monthly") == "2026-02-15"


def test_next_due_date_monthly_clamps_to_last_day_of_shorter_month():
    assert expense_store.next_due_date("2026-01-31", "Monthly") == "2026-02-28"


def test_next_due_date_monthly_clamps_to_leap_year_february():
    assert expense_store.next_due_date("2028-01-31", "Monthly") == "2028-02-29"


def test_next_due_date_monthly_wraps_year_from_december():
    assert expense_store.next_due_date("2026-12-15", "Monthly") == "2027-01-15"


def test_next_due_date_returns_none_for_no_recurrence():
    assert expense_store.next_due_date("2026-01-01", "None") is None


def test_roll_over_due_expenses_creates_next_occurrence_for_due_weekly_expense(conn):
    # Use today's date as the due date: the spawned next occurrence (today + 7 days) then
    # lands in the future, so a follow-up list_expenses() call below doesn't cascade into
    # rolling that new row over again too.
    today = date.today().isoformat()
    expense_store.add_expense(
        conn, sample_expense(id="id-1", date=today, recurrence="Weekly")
    )

    created = expense_store.roll_over_due_expenses(conn)

    assert len(created) == 1
    new_expense = created[0]
    assert new_expense["date"] == expense_store.next_due_date(today, "Weekly")
    assert new_expense["description"] == "Coffee"
    assert new_expense["amount"] == 4.5
    assert new_expense["category"] == "Food"
    assert new_expense["recurrence"] == "Weekly"
    assert new_expense["id"] != "id-1"

    all_expenses = {e["id"]: e for e in expense_store.list_expenses(conn)}
    assert len(all_expenses) == 2
    original = all_expenses["id-1"]
    assert original["description"] == "Coffee"
    assert original["amount"] == 4.5
    assert original["date"] == today
    assert original["category"] == "Food"
    assert original["recurrence"] == "Weekly"


def test_roll_over_due_expenses_creates_next_occurrence_for_due_monthly_expense(conn):
    expense_store.add_expense(
        conn, sample_expense(id="id-1", date="2026-01-31", recurrence="Monthly")
    )

    created = expense_store.roll_over_due_expenses(conn)

    assert len(created) == 1
    assert created[0]["date"] == "2026-02-28"


def test_roll_over_due_expenses_ignores_future_dated_expense(conn):
    expense_store.add_expense(
        conn, sample_expense(id="id-1", date="2099-01-01", recurrence="Weekly")
    )

    created = expense_store.roll_over_due_expenses(conn)

    assert created == []
    assert len(expense_store.list_expenses(conn)) == 1


def test_roll_over_due_expenses_ignores_non_recurring_expense_regardless_of_date(conn):
    expense_store.add_expense(
        conn, sample_expense(id="id-1", date="2020-01-01", recurrence="None")
    )

    created = expense_store.roll_over_due_expenses(conn)

    assert created == []
    assert len(expense_store.list_expenses(conn)) == 1


def test_roll_over_due_expenses_does_not_duplicate_on_repeated_calls(conn):
    today = date.today().isoformat()
    expense_store.add_expense(
        conn, sample_expense(id="id-1", date=today, recurrence="Weekly")
    )

    first_pass = expense_store.list_expenses(conn)
    second_pass = expense_store.list_expenses(conn)

    assert len(first_pass) == 2
    assert len(second_pass) == 2
    assert {e["id"] for e in first_pass} == {e["id"] for e in second_pass}
