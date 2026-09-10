import { useState } from "react";
import { CATEGORIES, RECURRENCE_OPTIONS } from "../constants";

const emptyForm = {
  description: "",
  amount: "",
  date: new Date().toISOString().slice(0, 10),
  category: CATEGORIES[0],
  recurrence: RECURRENCE_OPTIONS[0],
};

/**
 * Builds the initial local form state for a given `editingExpense` value.
 *
 * @param {Object|null} editingExpense - Expense currently being edited, or null to add a new one.
 * @returns {{description: string, amount: number|string, date: string, category: string, recurrence: string}}
 */
function buildFormState(editingExpense) {
  if (!editingExpense) return emptyForm;
  return {
    description: editingExpense.description,
    amount: editingExpense.amount,
    date: editingExpense.date,
    category: editingExpense.category,
    recurrence: editingExpense.recurrence || RECURRENCE_OPTIONS[0],
  };
}

/**
 * Add/edit form for a single expense. Renders as "Add Expense" with an empty
 * form when `editingExpense` is null, or "Edit Expense" pre-filled with that
 * expense's fields otherwise. The caller is expected to remount this component
 * (e.g. via a `key` tied to the editing expense's id) when switching between
 * expenses so the local form state re-initializes from `editingExpense`.
 *
 * @param {Object} props
 * @param {Object|null} props.editingExpense - Expense currently being edited, or null to add a new one.
 * @param {string|null} props.error - Error message to display above the form actions, if any.
 * @param {(data: {description: string, amount: number, date: string, category: string, recurrence: string}) => void} props.onSubmit - Called with the parsed form values on submit.
 * @param {() => void} props.onCancel - Called when the Cancel button (shown only while editing) is clicked.
 */
export default function ExpenseForm({ editingExpense, error, onSubmit, onCancel }) {
  const [form, setForm] = useState(() => buildFormState(editingExpense));

  /**
   * Creates a change handler bound to a single form field.
   *
   * @param {string} field - Key of `form` to update.
   * @returns {(e: Event) => void} An `onChange` handler for that field's input.
   */
  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  /**
   * Handles form submission: prevents the default page navigation, parses
   * the amount field to a number, and delegates to `onSubmit`.
   *
   * @param {Event} e - The form submit event.
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      description: form.description,
      amount: parseFloat(form.amount),
      date: form.date,
      category: form.category,
      recurrence: form.recurrence,
    });
  };

  const isEditing = Boolean(editingExpense);

  return (
    <section className="form-section">
      <h2 id="form-title">{isEditing ? "Edit Expense" : "Add Expense"}</h2>
      <form id="expense-form" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="description">Description</label>
          <input
            type="text"
            id="description"
            placeholder="e.g. Groceries"
            required
            value={form.description}
            onChange={handleChange("description")}
          />
        </div>

        <div className="field">
          <label htmlFor="amount">Amount</label>
          <input
            type="number"
            id="amount"
            step="0.01"
            min="0.01"
            placeholder="0.00"
            required
            value={form.amount}
            onChange={handleChange("amount")}
          />
        </div>

        <div className="field">
          <label htmlFor="date">Date</label>
          <input type="date" id="date" required value={form.date} onChange={handleChange("date")} />
        </div>

        <div className="field">
          <label htmlFor="category">Category</label>
          <select id="category" required value={form.category} onChange={handleChange("category")}>
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="recurrence">Recurrence</label>
          <select id="recurrence" required value={form.recurrence} onChange={handleChange("recurrence")}>
            {RECURRENCE_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div id="form-error" className="error-message" role="alert">
            {error}
          </div>
        )}

        <div className="form-actions">
          <button type="submit" id="submit-btn">
            {isEditing ? "Update Expense" : "Add Expense"}
          </button>
          {isEditing && (
            <button type="button" id="cancel-btn" onClick={onCancel}>
              Cancel
            </button>
          )}
        </div>
      </form>
    </section>
  );
}
