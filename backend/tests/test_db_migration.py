import os
import sqlite3
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db as db_module


def test_init_db_migrates_legacy_single_column_budgets_to_current_month(db_path):
    legacy_conn = sqlite3.connect(db_path)
    legacy_conn.execute("CREATE TABLE budgets (category TEXT PRIMARY KEY, amount REAL NOT NULL)")
    legacy_conn.execute("INSERT INTO budgets (category, amount) VALUES ('Food', 200)")
    legacy_conn.commit()
    legacy_conn.close()

    db_module.init_db(db_path)

    conn = db_module.get_connection(db_path)
    try:
        rows = [dict(row) for row in conn.execute("SELECT * FROM budgets")]
    finally:
        conn.close()

    current_month = date.today().strftime("%Y-%m")
    assert rows == [{"category": "Food", "month": current_month, "amount": 200}]


def test_init_db_is_idempotent_on_an_already_migrated_database(db_path):
    db_module.init_db(db_path)
    db_module.init_db(db_path)

    conn = db_module.get_connection(db_path)
    try:
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(budgets)")]
    finally:
        conn.close()

    assert set(columns) == {"category", "month", "amount"}


def test_init_db_migrates_legacy_expenses_table_adding_recurrence_columns(db_path):
    legacy_conn = sqlite3.connect(db_path)
    legacy_conn.execute(
        "CREATE TABLE expenses (id TEXT PRIMARY KEY, description TEXT NOT NULL, amount REAL NOT NULL, "
        "date TEXT NOT NULL, category TEXT NOT NULL)"
    )
    legacy_conn.execute(
        "INSERT INTO expenses (id, description, amount, date, category) VALUES (?, ?, ?, ?, ?)",
        ("id-1", "Coffee", 4.5, "2026-01-01", "Food"),
    )
    legacy_conn.commit()
    legacy_conn.close()

    db_module.init_db(db_path)

    conn = db_module.get_connection(db_path)
    try:
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(expenses)")]
        rows = [dict(row) for row in conn.execute("SELECT * FROM expenses")]
    finally:
        conn.close()

    assert set(columns) == {
        "id",
        "description",
        "amount",
        "date",
        "category",
        "recurrence",
        "next_occurrence_created",
    }
    assert rows == [
        {
            "id": "id-1",
            "description": "Coffee",
            "amount": 4.5,
            "date": "2026-01-01",
            "category": "Food",
            "recurrence": "None",
            "next_occurrence_created": 0,
        }
    ]


def test_init_db_expenses_migration_is_idempotent_on_an_already_migrated_database(db_path):
    db_module.init_db(db_path)
    db_module.init_db(db_path)

    conn = db_module.get_connection(db_path)
    try:
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(expenses)")]
    finally:
        conn.close()

    assert set(columns) == {
        "id",
        "description",
        "amount",
        "date",
        "category",
        "recurrence",
        "next_occurrence_created",
    }
