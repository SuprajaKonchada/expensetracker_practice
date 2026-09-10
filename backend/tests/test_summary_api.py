from datetime import date

import expense_store


def test_summary_totals_and_groups_by_category_for_the_given_month(client):
    client.post("/api/expenses", json={"description": "Coffee", "amount": 10, "date": "2026-01-05", "category": "Food"})
    client.post("/api/expenses", json={"description": "Lunch", "amount": 5, "date": "2026-01-10", "category": "Food"})
    client.post("/api/expenses", json={"description": "Bus", "amount": 20, "date": "2026-01-20", "category": "Transport"})
    client.post("/api/expenses", json={"description": "Other month", "amount": 99, "date": "2026-02-01", "category": "Food"})

    resp = client.get("/api/summary?month=2026-01")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 35
    assert body["byCategory"] == {"Food": 15, "Transport": 20}


def test_summary_includes_budget_statuses_with_exceeded_flag(client):
    client.put("/api/budgets/Food?month=2026-01", json={"amount": 100})
    client.put("/api/budgets/Transport?month=2026-01", json={"amount": 50})
    client.post("/api/expenses", json={"description": "Coffee", "amount": 120, "date": "2026-01-05", "category": "Food"})

    resp = client.get("/api/summary?month=2026-01")

    body = resp.get_json()
    statuses = {s["category"]: s for s in body["budgetStatuses"]}
    assert statuses["Food"]["exceeded"] is True
    assert statuses["Food"]["remaining"] == -20
    assert statuses["Transport"]["exceeded"] is False
    assert statuses["Transport"]["remaining"] == 50


def test_summary_budget_statuses_do_not_leak_into_other_months(client):
    client.put("/api/budgets/Food?month=2026-01", json={"amount": 100})
    client.post("/api/expenses", json={"description": "Coffee", "amount": 10, "date": "2026-02-05", "category": "Food"})

    resp = client.get("/api/summary?month=2026-02")

    body = resp.get_json()
    assert body["budgetStatuses"] == []


def test_summary_triggers_rollover_and_includes_the_new_occurrence(client):
    today = date.today().isoformat()
    client.post(
        "/api/expenses",
        json={"description": "Gym", "amount": 30, "date": today, "category": "Health", "recurrence": "Weekly"},
    )
    next_date = expense_store.next_due_date(today, "Weekly")
    current_month = today[:7]
    next_month = next_date[:7]

    resp = client.get(f"/api/summary?month={current_month}")
    body = resp.get_json()

    if current_month == next_month:
        assert body["byCategory"]["Health"] == 60
    else:
        assert body["byCategory"]["Health"] == 30
        resp_next = client.get(f"/api/summary?month={next_month}")
        assert resp_next.get_json()["byCategory"]["Health"] == 30
