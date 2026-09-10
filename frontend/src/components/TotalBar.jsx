import { formatCurrency } from "../constants";

/**
 * Reusable label/amount bar (e.g. "Total:" plus a formatted currency value).
 * Used for both the overall expense total and the monthly summary total.
 *
 * @param {Object} props
 * @param {string} props.label - Text shown before the amount.
 * @param {number} props.amount - Amount to format and display.
 * @param {string} props.className - CSS class applied to the wrapping element.
 * @param {string} props.valueId - `id` applied to the amount element, for test/DOM hooks.
 */
export default function TotalBar({ label, amount, className, valueId }) {
  return (
    <div className={className}>
      <span>{label}</span>
      <span id={valueId}>{formatCurrency(amount)}</span>
    </div>
  );
}
