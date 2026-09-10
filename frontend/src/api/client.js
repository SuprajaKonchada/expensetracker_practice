const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

/**
 * Low-level fetch wrapper shared by every API function in this module.
 * Prefixes `path` with the configured API base URL, sends JSON by default,
 * and normalizes error handling: a non-OK response is rejected with an Error
 * whose message is the backend's `{"error": "..."}` body when present (falling
 * back to a generic status-code message for non-JSON error bodies), and a 204
 * response resolves to `null` instead of attempting to parse an empty body.
 *
 * @param {string} path - API path appended to the base URL (e.g. "/expenses").
 * @param {RequestInit} [options] - Extra `fetch` options (method, body, etc.).
 * @returns {Promise<any>} The parsed JSON response body, or `null` for 204 responses.
 * @throws {Error} If the response status is not OK.
 */
async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      if (body && body.error) message = body.error;
    } catch {
      // ignore non-JSON error bodies
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

/**
 * Fetches all expenses.
 *
 * @returns {Promise<Array<Object>>} All expense records.
 */
export function getExpenses() {
  return request("/expenses");
}

/**
 * Creates a new expense.
 *
 * @param {Object} data - Expense fields (description, amount, date, category).
 * @returns {Promise<Object>} The created expense record.
 */
export function createExpense(data) {
  return request("/expenses", { method: "POST", body: JSON.stringify(data) });
}

/**
 * Updates an existing expense.
 *
 * @param {string} id - Id of the expense to update.
 * @param {Object} data - Updated expense fields.
 * @returns {Promise<Object>} The updated expense record.
 */
export function updateExpense(id, data) {
  return request(`/expenses/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

/**
 * Deletes an expense.
 *
 * @param {string} id - Id of the expense to delete.
 * @returns {Promise<null>} Resolves to `null` on success (204 response).
 */
export function deleteExpense(id) {
  return request(`/expenses/${id}`, { method: "DELETE" });
}

/**
 * Fetches the per-category budgets for a given month.
 *
 * @param {string} month - Month in "YYYY-MM" format.
 * @returns {Promise<Object>} Map of category name to budget amount.
 */
export function getBudgets(month) {
  return request(`/budgets?month=${encodeURIComponent(month)}`);
}

/**
 * Sets (or, for a non-positive/NaN amount, removes) a category's budget for a
 * given month.
 *
 * @param {string} category - Budget category.
 * @param {string} month - Month in "YYYY-MM" format.
 * @param {number} amount - Budget amount; non-positive or NaN removes the budget.
 * @returns {Promise<Object>} The updated map of category name to budget amount.
 */
export function setBudget(category, month, amount) {
  return request(`/budgets/${encodeURIComponent(category)}?month=${encodeURIComponent(month)}`, {
    method: "PUT",
    body: JSON.stringify({ amount }),
  });
}

/**
 * Fetches the aggregated summary (total, spend by category, and budget
 * statuses) for a given month.
 *
 * @param {string} month - Month in "YYYY-MM" format.
 * @returns {Promise<{total: number, byCategory: Object, budgetStatuses: Array<Object>}>} The month's summary.
 */
export function getSummary(month) {
  return request(`/summary?month=${encodeURIComponent(month)}`);
}

/**
 * Sends a message to the AI expense assistant and gets its reply, optionally
 * including prior turns of the conversation for multi-turn context.
 *
 * @param {string} message - The user's message.
 * @param {Array<{role: "user"|"assistant", content: string}>} [history] - Prior conversation turns, oldest first.
 * @returns {Promise<{reply: string, toolCalls: Array<Object>}>} The assistant's reply and any tools it used.
 */
export function sendAssistantMessage(message, history = []) {
  return request("/assistant/chat", { method: "POST", body: JSON.stringify({ message, history }) });
}
