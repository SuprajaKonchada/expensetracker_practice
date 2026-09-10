import { CATEGORIES } from "../constants";

/**
 * Renders a month picker plus one editable budget input per category.
 * Budget edits commit on blur or Enter (not on every keystroke); each input's
 * `key` is tied to its current budget value so it resyncs to the latest value
 * (e.g. after a save) instead of retaining stale local edits.
 *
 * @param {Object} props
 * @param {Object} props.budgets - Map of category name to budget amount for `month`.
 * @param {string} props.month - Selected month, "YYYY-MM".
 * @param {(month: string) => void} props.onMonthChange - Called when the month picker changes.
 * @param {(category: string, rawValue: string) => void} props.onChange - Called on blur/Enter with the raw input text.
 */
export default function BudgetTable({ budgets, month, onMonthChange, onChange }) {
  return (
    <section className="budget-section">
      <h2>Category Budgets</h2>
      <div className="field">
        <label htmlFor="budget-month">Month</label>
        <input type="month" id="budget-month" value={month} onChange={(e) => onMonthChange(e.target.value)} />
      </div>
      <table id="budget-table">
        <thead>
          <tr>
            <th scope="col">Category</th>
            <th scope="col">Monthly Budget</th>
          </tr>
        </thead>
        <tbody id="budget-list">
          {CATEGORIES.map((category) => (
            <tr key={category}>
              <td>{category}</td>
              <td>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="budget-input"
                  placeholder="No budget"
                  aria-label={`${category} monthly budget`}
                  defaultValue={budgets[category] !== undefined ? budgets[category] : ""}
                  key={budgets[category]}
                  onBlur={(e) => onChange(category, e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") e.target.blur();
                  }}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
