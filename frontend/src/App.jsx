import { useCallback, useEffect, useMemo, useState } from "react";
import * as api from "./api/client";
import AssistantChat from "./components/AssistantChat";
import BudgetTable from "./components/BudgetTable";
import ExpenseForm from "./components/ExpenseForm";
import ExpenseTable from "./components/ExpenseTable";
import FilterSortControls from "./components/FilterSortControls";
import MonthlySummary from "./components/MonthlySummary";
import TotalBar from "./components/TotalBar";
import "./App.css";

/**
 * Returns a new array of expenses sorted according to the given key.
 *
 * @param {Array<Object>} expenses - Expenses to sort (not mutated).
 * @param {"date-asc"|"date-desc"|"amount-asc"|"amount-desc"} sortBy - Sort key; any other value leaves the input order unchanged.
 * @returns {Array<Object>} A new, sorted array.
 */
function sortExpenses(expenses, sortBy) {
  const result = [...expenses];
  result.sort((a, b) => {
    if (sortBy === "date-asc") return a.date.localeCompare(b.date);
    if (sortBy === "date-desc") return b.date.localeCompare(a.date);
    if (sortBy === "amount-asc") return a.amount - b.amount;
    if (sortBy === "amount-desc") return b.amount - a.amount;
    return 0;
  });
  return result;
}

/**
 * Top-level application component. Owns all shared state (expenses, budgets,
 * filters, the selected summary month, and loading/error state), fetches data
 * from the backend API, and wires that state into the presentational child
 * components (ExpenseForm, BudgetTable, MonthlySummary, FilterSortControls,
 * ExpenseTable).
 */
export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [budgets, setBudgets] = useState({});
  const [filterCategory, setFilterCategory] = useState("");
  const [sortBy, setSortBy] = useState("date-desc");
  const [summaryMonth, setSummaryMonth] = useState(new Date().toISOString().slice(0, 7));
  const [summary, setSummary] = useState({ total: 0, byCategory: {}, budgetStatuses: [] });
  const [editingExpense, setEditingExpense] = useState(null);
  const [formError, setFormError] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadExpenses = useCallback(async () => {
    setExpenses(await api.getExpenses());
  }, []);

  const loadBudgets = useCallback(async (month) => {
    setBudgets(await api.getBudgets(month));
  }, []);

  const loadSummary = useCallback(async (month) => {
    setSummary(await api.getSummary(month));
  }, []);

  useEffect(() => {
    setIsLoading(true);
    Promise.all([loadExpenses(), loadBudgets(summaryMonth)])
      .catch((err) => setLoadError(err.message))
      .finally(() => setIsLoading(false));
    // Intentionally run once on mount only: summaryMonth changes are handled by the
    // effect below, so including it here would trigger a duplicate budgets load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loadExpenses, loadBudgets]);

  useEffect(() => {
    loadBudgets(summaryMonth).catch((err) => setLoadError(err.message));
  }, [summaryMonth, loadBudgets]);

  useEffect(() => {
    loadSummary(summaryMonth).catch((err) => setLoadError(err.message));
  }, [summaryMonth, expenses, budgets, loadSummary]);

  const visibleExpenses = useMemo(() => {
    const filtered = filterCategory ? expenses.filter((e) => e.category === filterCategory) : expenses;
    return sortExpenses(filtered, sortBy);
  }, [expenses, filterCategory, sortBy]);

  const visibleTotal = useMemo(() => visibleExpenses.reduce((sum, e) => sum + e.amount, 0), [visibleExpenses]);

  /**
   * Submits the expense form: updates the expense currently being edited, or
   * creates a new one if none is being edited. On success, clears the editing
   * state and reloads the expense list; on failure, surfaces the error via
   * `formError`.
   *
   * @param {Object} data - Expense payload from ExpenseForm.
   */
  const handleFormSubmit = async (data) => {
    setFormError(null);
    try {
      if (editingExpense) {
        await api.updateExpense(editingExpense.id, data);
      } else {
        await api.createExpense(data);
      }
      setEditingExpense(null);
      await loadExpenses();
    } catch (err) {
      setFormError(err.message);
    }
  };

  const handleEdit = (expense) => {
    setEditingExpense(expense);
    setFormError(null);
  };

  const handleCancelEdit = () => {
    setEditingExpense(null);
    setFormError(null);
  };

  /**
   * Deletes an expense after user confirmation. If the deleted expense was
   * currently being edited, also clears the editing state so the form resets.
   *
   * @param {string} id - Id of the expense to delete.
   */
  const handleDelete = async (id) => {
    if (!window.confirm("Delete this expense?")) return;
    setLoadError(null);
    try {
      await api.deleteExpense(id);
      if (editingExpense && editingExpense.id === id) setEditingExpense(null);
      await loadExpenses();
    } catch (err) {
      setLoadError(err.message);
    }
  };

  /**
   * Persists a budget edit for the current summary month. A raw value that
   * doesn't parse to a number (e.g. an emptied input) is treated as 0, which
   * the backend interprets as "remove this category's budget".
   *
   * @param {string} category - Budget category being edited.
   * @param {string} rawValue - Raw text from the budget input.
   */
  const handleBudgetChange = async (category, rawValue) => {
    const amount = parseFloat(rawValue);
    setLoadError(null);
    try {
      const updated = await api.setBudget(category, summaryMonth, Number.isNaN(amount) ? 0 : amount);
      setBudgets(updated);
    } catch (err) {
      setLoadError(err.message);
    }
  };

  /**
   * Refreshes shared expense/budget state after an assistant chat turn. The
   * chat component can't know whether a given turn mutated data (the
   * assistant may have autonomously created/updated/deleted expenses), so
   * this refreshes unconditionally, same spirit as handleDelete/handleFormSubmit
   * above. loadSummary re-runs automatically via the effect that depends on
   * [summaryMonth, expenses, budgets, loadSummary].
   */
  const handleAssistantDataChanged = async () => {
    await Promise.all([loadExpenses(), loadBudgets(summaryMonth)]);
  };

  return (
    <div className="container">
      <header>
        <h1>Expense Tracker</h1>
        <TotalBar label="Total:" amount={visibleTotal} className="total-bar" valueId="total-amount" />
      </header>

      {loadError && (
        <div className="error-message" role="alert">
          {loadError}
        </div>
      )}

      {isLoading ? (
        <p id="loading-state" role="status">
          Loading expenses…
        </p>
      ) : (
        <>
          <AssistantChat onDataChanged={handleAssistantDataChanged} />

          <ExpenseForm
            key={editingExpense ? editingExpense.id : "new"}
            editingExpense={editingExpense}
            error={formError}
            onSubmit={handleFormSubmit}
            onCancel={handleCancelEdit}
          />

          <BudgetTable
            budgets={budgets}
            month={summaryMonth}
            onMonthChange={setSummaryMonth}
            onChange={handleBudgetChange}
          />

          <MonthlySummary
            month={summaryMonth}
            onMonthChange={setSummaryMonth}
            total={summary.total}
            byCategory={summary.byCategory}
            budgetStatuses={summary.budgetStatuses}
            budgets={budgets}
          />

          <FilterSortControls
            filterCategory={filterCategory}
            onFilterChange={setFilterCategory}
            sortBy={sortBy}
            onSortChange={setSortBy}
          />

          <ExpenseTable expenses={visibleExpenses} onEdit={handleEdit} onDelete={handleDelete} />
        </>
      )}
    </div>
  );
}
