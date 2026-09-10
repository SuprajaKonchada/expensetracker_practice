import { formatCurrency } from "../constants";
import ExpensePieChart from "./ExpensePieChart";
import TotalBar from "./TotalBar";

/**
 * Renders the monthly summary: a month picker, the month's total, a
 * per-category breakdown (showing budget status when a budget exists for
 * that category, plain spend otherwise), and the expense distribution pie
 * chart. The category list is the union of categories with spend and
 * categories with a budget, so a budgeted-but-unspent category still appears.
 *
 * @param {Object} props
 * @param {string} props.month - Selected month, "YYYY-MM".
 * @param {(month: string) => void} props.onMonthChange - Called when the month picker changes.
 * @param {number} props.total - Total spend for the month.
 * @param {Object} props.byCategory - Map of category name to spend amount for the month.
 * @param {Array<Object>} props.budgetStatuses - Per-category budget status objects (category, spent, budget, remaining, exceeded).
 * @param {Object} props.budgets - Map of category name to budget amount for the month.
 */
export default function MonthlySummary({ month, onMonthChange, total, byCategory, budgetStatuses, budgets }) {
  const statusByCategory = {};
  for (const status of budgetStatuses) {
    statusByCategory[status.category] = status;
  }

  const categories = [...new Set([...Object.keys(byCategory), ...Object.keys(budgets)])].sort();

  return (
    <section className="summary-section">
      <h2>Monthly Summary</h2>
      <div className="field">
        <label htmlFor="summary-month">Month</label>
        <input type="month" id="summary-month" value={month} onChange={(e) => onMonthChange(e.target.value)} />
      </div>

      <TotalBar label="Total for month:" amount={total} className="summary-total-bar" valueId="summary-total" />

      <ul id="summary-breakdown" className="summary-breakdown">
        {categories.length === 0 && <li className="summary-empty">No expenses for this month.</li>}
        {categories.map((category) => {
          const status = statusByCategory[category];
          if (status) {
            return (
              <li key={category} className={status.exceeded ? "over-budget" : ""}>
                <span>{category}</span>
                <span>
                  {formatCurrency(status.spent)} / {formatCurrency(status.budget)}
                </span>
                {status.exceeded ? (
                  <strong className="budget-flag">Over by {formatCurrency(Math.abs(status.remaining))}</strong>
                ) : (
                  <span className="budget-remaining">{formatCurrency(status.remaining)} left</span>
                )}
              </li>
            );
          }
          return (
            <li key={category}>
              <span>{category}</span>
              <span>{formatCurrency(byCategory[category] || 0)}</span>
            </li>
          );
        })}
      </ul>

      <h3>Expense Distribution</h3>
      <ExpensePieChart byCategory={byCategory} />
    </section>
  );
}
