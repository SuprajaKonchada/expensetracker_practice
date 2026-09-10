def test_get_budgets_returns_empty_object_initially(client):
    resp = client.get("/api/budgets?month=2026-01")
    assert resp.status_code == 200
    assert resp.get_json() == {}


def test_get_budgets_requires_a_month_param(client):
    resp = client.get("/api/budgets")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_get_budgets_rejects_a_malformed_month(client):
    resp = client.get("/api/budgets?month=not-a-month")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_put_budget_sets_a_category_budget_for_the_given_month(client):
    resp = client.put("/api/budgets/Food?month=2026-01", json={"amount": 200})
    assert resp.status_code == 200
    assert resp.get_json() == {"Food": 200}


def test_put_budget_does_not_apply_to_other_months(client):
    client.put("/api/budgets/Food?month=2026-01", json={"amount": 200})

    resp = client.get("/api/budgets?month=2026-02")

    assert resp.get_json() == {}


def test_put_budget_with_non_positive_amount_removes_it(client):
    client.put("/api/budgets/Food?month=2026-01", json={"amount": 200})
    resp = client.put("/api/budgets/Food?month=2026-01", json={"amount": 0})
    assert resp.status_code == 200
    assert resp.get_json() == {}


def test_put_budget_rejects_unknown_category(client):
    resp = client.put("/api/budgets/NotACategory?month=2026-01", json={"amount": 100})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_put_budget_requires_amount_field(client):
    resp = client.put("/api/budgets/Food?month=2026-01", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_put_budget_requires_a_month_param(client):
    resp = client.put("/api/budgets/Food", json={"amount": 100})
    assert resp.status_code == 400
    assert "error" in resp.get_json()
