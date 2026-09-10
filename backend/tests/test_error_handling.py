import sqlite3


def test_database_error_returns_safe_generic_message(client, monkeypatch):
    def boom(conn):
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr("expense_store.list_expenses", boom)

    resp = client.get("/api/expenses")

    assert resp.status_code == 500
    assert resp.get_json() == {"error": "A database error occurred."}
    assert "Traceback" not in resp.get_data(as_text=True)


def test_unexpected_error_returns_safe_generic_message(client, monkeypatch):
    def boom(conn):
        raise RuntimeError("something exploded")

    monkeypatch.setattr("expense_store.list_expenses", boom)

    resp = client.get("/api/expenses")

    assert resp.status_code == 500
    assert resp.get_json() == {"error": "An unexpected error occurred."}
    assert "Traceback" not in resp.get_data(as_text=True)
    assert "RuntimeError" not in resp.get_data(as_text=True)


def test_unknown_route_returns_json_not_html(client):
    resp = client.get("/api/does-not-exist")

    assert resp.status_code == 404
    assert resp.content_type == "application/json"
    assert "error" in resp.get_json()
