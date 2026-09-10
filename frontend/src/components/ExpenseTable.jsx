import { formatCurrency } from "../constants";

/**
 * Renders the list of expenses as a table, with edit/delete actions per row
 * and an empty-state message when there are no expenses to show.
 *
 * @param {Object} props
 * @param {Array<Object>} props.expenses - Expenses to display, in the order given.
 * @param {(expense: Object) => void} props.onEdit - Called with the expense when its Edit button is clicked.
 * @param {(id: string) => void} props.onDelete - Called with the expense id when its Delete button is clicked.
 */
export default function ExpenseTable({ expenses, onEdit, onDelete }) {
  return (
    <section className="list-section">
      <table id="expense-table">
        <thead>
          <tr>
            <th scope="col">Description</th>
            <th scope="col">Amount</th>
            <th scope="col">Date</th>
            <th scope="col">Category</th>
            <th scope="col">Recurrence</th>
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody id="expense-list">
          {expenses.map((expense) => (
            <tr key={expense.id}>
              <td>{expense.description}</td>
              <td>{formatCurrency(expense.amount)}</td>
              <td>{expense.date}</td>
              <td>{expense.category}</td>
              <td>{expense.recurrence || "None"}</td>
              <td>
                <button className="action-btn edit-btn" onClick={() => onEdit(expense)}>
                  Edit
                </button>
                <button className="action-btn delete-btn" onClick={() => onDelete(expense.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {expenses.length === 0 && <p id="empty-state">No expenses yet. Add one above to get started.</p>}
    </section>
  );
}
