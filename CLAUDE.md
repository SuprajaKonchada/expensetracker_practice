# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

Expense tracker migrated to a three-tier stack: **React frontend** talking to a **Python/Flask REST API** backed by **SQLite**.

```
backend/    Flask API + SQLite persistence
frontend/   React app (Vite)
```

### Backend (`backend/`)

- `config.py` — environment-driven settings (`DB_PATH`, `HOST`, `PORT`, `DEBUG`), read from env vars (`EXPENSE_TRACKER_DB_PATH`, `HOST`, `PORT`, `FLASK_DEBUG`) with dev-friendly defaults. `DEBUG` defaults to `False` — set `FLASK_DEBUG=true` for local debugging only; never enable it in a deployed environment, since it exposes stack traces.
- `constants.py` — shared `CATEGORIES` list, mirrors `frontend/src/constants.js`.
- `db.py` — SQLite connection + schema (`expenses`, `budgets` tables), connection uses `config.DB_PATH`.
- `expense_repository.py` / `budget_repository.py` — data-access layer: the only modules that issue raw SQL against `expenses`/`budgets`.
- `expense_store.py` / `budget_store.py` — business logic only (validation, aggregation, budget rules), DB-backed equivalents of the original `js/expenseStore.js` / `js/budgetStore.js` (same rules, e.g. non-positive or NaN budget amounts remove the category's budget), delegating all persistence to the repository modules above.
- `routes_expenses.py`, `routes_budgets.py`, `routes_summary.py` — Flask blueprints implementing the REST API (see below).
- `app.py` — app factory (`create_app(db_path=None)`), registers blueprints, CORS, and global error handlers, initializes the DB. Run directly with `python app.py` to serve using `config.HOST`/`config.PORT`/`config.DEBUG`.
- No ORM — plain `sqlite3` (stdlib) with `Row` factory.
- Global error handlers in `app.py` return safe, consistent JSON (`{"error": "..."}`) for `sqlite3.Error`, any other unhandled exception, and standard HTTP errors (404 etc.) — no stack traces or internal details are ever returned to the client.

**Database schema** — two tables, no foreign key between them: category is a fixed constant list (`backend/constants.py`, mirrored in `frontend/src/constants.js`) shared by convention on both frontend and backend, not a real DB entity (this mirrors the original app's design).
- `expenses(id TEXT PK, description TEXT, amount REAL, date TEXT "YYYY-MM-DD", category TEXT)`
- `budgets(category TEXT, month TEXT "YYYY-MM", amount REAL, PRIMARY KEY (category, month))` — one budget per category **per month**; there is no fallback to a prior month's value. `db.py` migrates a pre-monthly database (the old `category TEXT PRIMARY KEY` shape) by carrying each existing recurring budget forward onto the current month, the one time `init_db` sees the legacy shape.

**REST API**
- `GET/POST /api/expenses`, `PUT/DELETE /api/expenses/<id>`
- `GET /api/budgets?month=YYYY-MM`, `PUT /api/budgets/<category>?month=YYYY-MM` (body `{amount}` required; 400 if `month` is missing/malformed, `category` isn't one of `constants.CATEGORIES`, or `amount` is missing from the body; a non-positive/NaN amount value removes that category's budget for that month)
- `GET /api/summary?month=YYYY-MM` → `{ total, byCategory, budgetStatuses }` (`budgetStatuses` is computed from that month's budgets only)
- `GET /api/health`

### Frontend (`frontend/`)

React 19 + Vite. `src/api/client.js` is the fetch wrapper for the backend (base URL via `VITE_API_BASE_URL`, defaults to `http://localhost:5000/api`). `src/App.jsx` holds top-level state and wires components in `src/components/`: `ExpenseForm`, `ExpenseTable`, `BudgetTable`, `MonthlySummary`, `ExpensePieChart`, `FilterSortControls`, `TotalBar`. `src/constants.js` holds the shared `CATEGORIES` list, `CATEGORY_COLORS`, and `formatCurrency`. Category filtering/sorting of the expense list stays client-side (matching original UX); the monthly summary and budget-status computation is server-side via `/api/summary`. Budgets are scoped to a month (`App.jsx`'s `summaryMonth` state is the single source of truth); `BudgetTable` and `MonthlySummary` each render their own `<input type="month">` bound to that same state, so picking a month in either one moves both. `MonthlySummary` also renders `ExpensePieChart`, a dependency-free SVG chart of that month's `byCategory` spend.

## Commands

**Backend** (from `backend/`, Python 3.11 — see `.python-version` at repo root, pyenv-managed):
- Install deps: `pip install -r requirements.txt`
- Run the API: `python app.py` (serves on `http://localhost:5000`)
- Run tests: `pytest` (or `python -m pytest`)

**Frontend** (from `frontend/`):
- Install deps: `npm install`
- Run dev server: `npm run dev` (serves on `http://localhost:5173`, expects the backend on port 5000)
- Run tests: `npm test` (vitest + React Testing Library)
- Production build: `npm run build`

### Testing

- `backend/tests/test_expense_store.py`, `test_budget_store.py` — unit tests for the store modules (pytest), ported 1:1 from the original `node:test` suites (`test_budget_store.py` now also covers month-scoping and `is_valid_month`).
- `backend/tests/test_expenses_api.py`, `test_budgets_api.py`, `test_summary_api.py` — Flask test-client API tests, each using an isolated temp SQLite DB per test (see `tests/conftest.py`).
- `backend/tests/test_error_handling.py` — verifies DB/unexpected errors and unknown routes return safe, generic JSON (never a stack trace).
- `backend/tests/test_db_migration.py` — verifies `init_db` upgrades a legacy (pre-monthly) `budgets` table onto the current month, and that migration is idempotent.
- `frontend/src/**/*.test.jsx` — component tests (vitest + Testing Library, including `ExpensePieChart.test.jsx`) plus `App.test.jsx` for integration flows (create/edit/delete, loading state, delete/budget error handling) with `src/api/client.js` mocked.
