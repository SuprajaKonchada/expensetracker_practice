import assistant_tools


def sample_payload(**overrides):
    payload = {"description": "Coffee", "amount": 4.5, "date": "2026-01-01", "category": "Food"}
    payload.update(overrides)
    return payload


def test_list_expenses_returns_all_when_no_filters(conn):
    assistant_tools.create_expense(conn, **sample_payload())
    assistant_tools.create_expense(conn, **sample_payload(description="Bus", category="Transport"))

    result = assistant_tools.list_expenses(conn)

    assert len(result["expenses"]) == 2


def test_list_expenses_filters_by_category(conn):
    assistant_tools.create_expense(conn, **sample_payload())
    assistant_tools.create_expense(conn, **sample_payload(description="Bus", category="Transport"))

    result = assistant_tools.list_expenses(conn, category="Transport")

    assert len(result["expenses"]) == 1
    assert result["expenses"][0]["description"] == "Bus"


def test_list_expenses_filters_by_month(conn):
    assistant_tools.create_expense(conn, **sample_payload(date="2026-01-15"))
    assistant_tools.create_expense(conn, **sample_payload(description="Feb item", date="2026-02-01"))

    result = assistant_tools.list_expenses(conn, month="2026-02")

    assert len(result["expenses"]) == 1
    assert result["expenses"][0]["description"] == "Feb item"


def test_list_expenses_filters_by_category_and_month(conn):
    assistant_tools.create_expense(conn, **sample_payload(date="2026-01-15"))
    assistant_tools.create_expense(conn, **sample_payload(description="Bus", category="Transport", date="2026-01-20"))

    result = assistant_tools.list_expenses(conn, category="Transport", month="2026-01")

    assert len(result["expenses"]) == 1
    assert result["expenses"][0]["description"] == "Bus"


def test_create_expense_valid_payload_returns_created_expense(conn):
    result = assistant_tools.create_expense(conn, **sample_payload())

    assert "error" not in result
    assert result["description"] == "Coffee"
    assert result["amount"] == 4.5
    assert "id" in result


def test_create_expense_invalid_payload_returns_error(conn):
    result = assistant_tools.create_expense(conn, **sample_payload(amount=0))

    assert "error" in result


def test_update_expense_found_updates_and_returns_it(conn):
    created = assistant_tools.create_expense(conn, **sample_payload())

    result = assistant_tools.update_expense(conn, id=created["id"], **sample_payload(description="Latte", amount=5.5))

    assert result["description"] == "Latte"
    assert result["amount"] == 5.5


def test_update_expense_invalid_payload_returns_error(conn):
    created = assistant_tools.create_expense(conn, **sample_payload())

    result = assistant_tools.update_expense(conn, id=created["id"], **sample_payload(amount=-1))

    assert "error" in result


def test_update_expense_not_found_returns_error(conn):
    result = assistant_tools.update_expense(conn, id="missing-id", **sample_payload())

    assert result == {"error": "Expense not found."}


def test_delete_expense_returns_deleted_confirmation(conn):
    created = assistant_tools.create_expense(conn, **sample_payload())

    result = assistant_tools.delete_expense(conn, id=created["id"])

    assert result == {"deleted": True, "id": created["id"]}
    assert assistant_tools.list_expenses(conn)["expenses"] == []


def test_delete_expense_is_idempotent_for_missing_id(conn):
    result = assistant_tools.delete_expense(conn, id="missing-id")

    assert result == {"deleted": True, "id": "missing-id"}


def test_get_budgets_valid_month_returns_budgets(conn):
    import budget_store

    budget_store.set_budget(conn, "Food", "2026-01", 100)

    result = assistant_tools.get_budgets(conn, month="2026-01")

    assert result == {"Food": 100}


def test_get_budgets_invalid_month_returns_error(conn):
    result = assistant_tools.get_budgets(conn, month="not-a-month")

    assert "error" in result


def test_get_monthly_summary_matches_budget_status_computation(conn):
    import budget_store

    assistant_tools.create_expense(conn, **sample_payload(date="2026-01-05", amount=150, category="Food"))
    budget_store.set_budget(conn, "Food", "2026-01", 100)

    result = assistant_tools.get_monthly_summary(conn, month="2026-01")

    assert result["total"] == 150
    assert result["byCategory"] == {"Food": 150}
    expected_statuses = budget_store.get_budget_statuses({"Food": 100}, {"Food": 150})
    assert result["budgetStatuses"] == expected_statuses
    assert result["budgetStatuses"][0]["exceeded"] is True


def test_execute_tool_dispatches_by_name(conn):
    result = assistant_tools.execute_tool(conn, "list_expenses", {})

    assert result == {"expenses": []}


def test_execute_tool_unknown_name_returns_error(conn):
    result = assistant_tools.execute_tool(conn, "not_a_real_tool", {})

    assert "error" in result


def test_execute_tool_catches_unexpected_exceptions(conn, monkeypatch):
    def boom(conn, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setitem(assistant_tools._TOOL_FUNCTIONS, "list_expenses", boom)

    result = assistant_tools.execute_tool(conn, "list_expenses", {})

    assert result == {"error": "Tool execution failed."}
