from datetime import date

import expense_store


def sample_payload(**overrides):
    """Build a default sample expense request payload, overriding any fields passed as keyword arguments."""
    payload = {"description": "Coffee", "amount": 4.5, "date": "2026-01-01", "category": "Food"}
    payload.update(overrides)
    return payload


def test_create_expense_returns_201_and_the_created_expense(client):
    resp = client.post("/api/expenses", json=sample_payload())
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["description"] == "Coffee"
    assert body["amount"] == 4.5
    assert "id" in body


def test_create_expense_rejects_invalid_payload(client):
    resp = client.post("/api/expenses", json=sample_payload(amount=0))
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_get_expenses_lists_created_expenses(client):
    client.post("/api/expenses", json=sample_payload())
    client.post("/api/expenses", json=sample_payload(description="Bus", category="Transport"))

    resp = client.get("/api/expenses")

    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body) == 2


def test_update_expense_modifies_existing_expense(client):
    created = client.post("/api/expenses", json=sample_payload()).get_json()

    resp = client.put(f"/api/expenses/{created['id']}", json=sample_payload(description="Latte", amount=5.5))

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["description"] == "Latte"
    assert body["amount"] == 5.5


def test_update_expense_returns_404_for_missing_id(client):
    resp = client.put("/api/expenses/missing-id", json=sample_payload())
    assert resp.status_code == 404


def test_delete_expense_removes_it(client):
    created = client.post("/api/expenses", json=sample_payload()).get_json()

    resp = client.delete(f"/api/expenses/{created['id']}")
    assert resp.status_code == 204

    remaining = client.get("/api/expenses").get_json()
    assert remaining == []


def test_create_expense_response_never_exposes_internal_rollover_flag(client):
    resp = client.post("/api/expenses", json=sample_payload(recurrence="Weekly"))
    assert resp.status_code == 201
    assert "next_occurrence_created" not in resp.get_json()


def test_create_expense_with_recurrence_returns_201_and_echoes_it_back(client):
    resp = client.post("/api/expenses", json=sample_payload(recurrence="Weekly"))
    assert resp.status_code == 201
    assert resp.get_json()["recurrence"] == "Weekly"


def test_create_expense_rejects_invalid_recurrence(client):
    resp = client.post("/api/expenses", json=sample_payload(recurrence="Daily"))
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_create_expense_with_no_recurrence_defaults_to_none(client):
    resp = client.post("/api/expenses", json=sample_payload())
    assert resp.status_code == 201
    assert resp.get_json()["recurrence"] == "None"


def test_update_expense_with_recurrence_echoes_it_back(client):
    created = client.post("/api/expenses", json=sample_payload()).get_json()

    resp = client.put(f"/api/expenses/{created['id']}", json=sample_payload(recurrence="Monthly"))

    assert resp.status_code == 200
    assert resp.get_json()["recurrence"] == "Monthly"


def test_get_expenses_rolls_over_a_due_weekly_expense_exactly_once(client):
    # Use today's date so the spawned next occurrence (today + 7 days) is in the future and
    # won't itself be due on the second GET below.
    today = date.today().isoformat()
    client.post("/api/expenses", json=sample_payload(date=today, recurrence="Weekly"))

    first_get = client.get("/api/expenses")
    assert first_get.status_code == 200
    first_body = first_get.get_json()
    assert len(first_body) == 2
    dates = sorted(e["date"] for e in first_body)
    assert dates == sorted([today, expense_store.next_due_date(today, "Weekly")])

    second_get = client.get("/api/expenses")
    assert second_get.status_code == 200
    assert len(second_get.get_json()) == 2
