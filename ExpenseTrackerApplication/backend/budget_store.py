"""Budget business logic. Mirrors js/budgetStore.js. Persistence delegated to budget_repository."""
import math
import re

import budget_repository

MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def is_valid_month(month):
    """Return True if month is a non-empty string in YYYY-MM format."""
    return bool(month) and bool(MONTH_PATTERN.match(month))


def list_budgets(conn, month):
    """Return the given month's budgets as a {category: amount} dict."""
    rows = budget_repository.fetch_all_for_month(conn, month)
    return {row["category"]: row["amount"] for row in rows}


def set_budget(conn, category, month, amount):
    """Set (or remove) the budget for a category/month and return the updated month's budgets.

    A non-numeric, NaN, or non-positive amount removes the category's budget for that
    month instead of storing it.
    """
    if (
        not isinstance(amount, (int, float))
        or isinstance(amount, bool)
        or math.isnan(amount)
        or amount <= 0
    ):
        budget_repository.remove(conn, category, month)
        return list_budgets(conn, month)

    budget_repository.upsert(conn, category, month, amount)
    return list_budgets(conn, month)


def get_budget_statuses(budgets, by_category):
    """Build per-category budget status entries (spent, remaining, exceeded) sorted by category.

    `budgets` is a {category: amount} dict and `by_category` is a {category: spent} dict;
    only categories present in `budgets` are included.
    """
    statuses = []
    for category in sorted(budgets.keys()):
        budget = budgets[category]
        spent = by_category.get(category, 0)
        statuses.append(
            {
                "category": category,
                "budget": budget,
                "spent": spent,
                "remaining": budget - spent,
                "exceeded": spent > budget,
            }
        )
    return statuses
