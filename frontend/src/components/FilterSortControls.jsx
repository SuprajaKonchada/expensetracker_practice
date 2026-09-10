import { CATEGORIES } from "../constants";

const SORT_OPTIONS = [
  { value: "date-desc", label: "Date (newest first)" },
  { value: "date-asc", label: "Date (oldest first)" },
  { value: "amount-desc", label: "Amount (high to low)" },
  { value: "amount-asc", label: "Amount (low to high)" },
];

/**
 * Renders the category filter and sort-order dropdowns used above the
 * expense table. Purely presentational: selection state is owned by the parent.
 *
 * @param {Object} props
 * @param {string} props.filterCategory - Currently selected category filter ("" means all).
 * @param {(category: string) => void} props.onFilterChange - Called when the category filter changes.
 * @param {string} props.sortBy - Currently selected sort key.
 * @param {(sortBy: string) => void} props.onSortChange - Called when the sort order changes.
 */
export default function FilterSortControls({ filterCategory, onFilterChange, sortBy, onSortChange }) {
  return (
    <section className="filter-section">
      <div className="field">
        <label htmlFor="filter-category">Filter by category</label>
        <select id="filter-category" value={filterCategory} onChange={(e) => onFilterChange(e.target.value)}>
          <option value="">All</option>
          {CATEGORIES.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="sort-by">Sort by</label>
        <select id="sort-by" value={sortBy} onChange={(e) => onSortChange(e.target.value)}>
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </section>
  );
}
