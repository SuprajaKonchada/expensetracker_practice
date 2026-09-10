import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math

import budget_store


def test_set_budget_adds_a_new_budget_for_a_category_and_month(conn):
    updated = budget_store.set_budget(conn, "Food", "2026-01", 200)
    assert updated == {"Food": 200}


def test_set_budget_overwrites_existing_budget_for_same_category_and_month(conn):
    budget_store.set_budget(conn, "Food", "2026-01", 200)
    updated = budget_store.set_budget(conn, "Food", "2026-01", 350)
    assert updated == {"Food": 350}


def test_set_budget_is_scoped_to_its_month(conn):
    budget_store.set_budget(conn, "Food", "2026-01", 200)
    budget_store.set_budget(conn, "Food", "2026-02", 300)

    assert budget_store.list_budgets(conn, "2026-01") == {"Food": 200}
    assert budget_store.list_budgets(conn, "2026-02") == {"Food": 300}


def test_set_budget_removes_budget_when_given_non_positive_amount(conn):
    budget_store.set_budget(conn, "Food", "2026-01", 200)
    budget_store.set_budget(conn, "Transport", "2026-01", 50)
    updated = budget_store.set_budget(conn, "Food", "2026-01", 0)
    assert updated == {"Transport": 50}


def test_set_budget_removes_budget_when_given_nan(conn):
    budget_store.set_budget(conn, "Food", "2026-01", 200)
    updated = budget_store.set_budget(conn, "Food", "2026-01", math.nan)
    assert updated == {}


def test_list_budgets_returns_empty_for_a_month_with_nothing_set(conn):
    budget_store.set_budget(conn, "Food", "2026-01", 200)
    assert budget_store.list_budgets(conn, "2026-02") == {}


def test_is_valid_month_accepts_yyyy_mm():
    assert budget_store.is_valid_month("2026-01") is True
    assert budget_store.is_valid_month("2026-12") is True


def test_is_valid_month_rejects_malformed_values():
    assert budget_store.is_valid_month("") is False
    assert budget_store.is_valid_month("2026-13") is False
    assert budget_store.is_valid_month("2026-1") is False
    assert budget_store.is_valid_month("not-a-month") is False


def test_get_budget_statuses_computes_spent_remaining_exceeded_per_category():
    budgets = {"Food": 100, "Transport": 50}
    by_category = {"Food": 120, "Housing": 40}

    statuses = budget_store.get_budget_statuses(budgets, by_category)

    assert statuses == [
        {"category": "Food", "budget": 100, "spent": 120, "remaining": -20, "exceeded": True},
        {"category": "Transport", "budget": 50, "spent": 0, "remaining": 50, "exceeded": False},
    ]


def test_get_budget_statuses_returns_empty_list_when_no_budgets_set():
    assert budget_store.get_budget_statuses({}, {"Food": 50}) == []
