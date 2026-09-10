export const CATEGORIES = ["Food", "Transport", "Housing", "Utilities", "Entertainment", "Health", "Other"];

export const RECURRENCE_OPTIONS = ["None", "Weekly", "Monthly"];

// Fixed categorical assignment (never cycled) so a category always maps to the same color.
export const CATEGORY_COLORS = {
  Food: "#2a78d6",
  Transport: "#eb6834",
  Housing: "#1baf7a",
  Utilities: "#eda100",
  Entertainment: "#e87ba4",
  Health: "#008300",
  Other: "#4a3aa7",
};

/**
 * Formats a numeric amount as a USD currency string (e.g. `$12.50`).
 * Nullish or non-numeric input (`null`, `undefined`, `NaN`-producing values)
 * is treated as 0 rather than throwing or rendering "NaN".
 *
 * @param {number|string|null|undefined} amount - Value to format.
 * @returns {string} The formatted currency string.
 */
export function formatCurrency(amount) {
  return `$${Number(amount || 0).toFixed(2)}`;
}
