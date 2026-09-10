import { CATEGORIES, CATEGORY_COLORS, formatCurrency } from "../constants";

const SIZE = 200;
const RADIUS = 90;
const CENTER = SIZE / 2;

/**
 * Converts an angle on the pie (measured clockwise from 12 o'clock, in
 * degrees) to an {x, y} point on the chart's circle.
 *
 * @param {number} angleDeg - Angle in degrees, clockwise from the top.
 * @returns {{x: number, y: number}} The corresponding point on the circle.
 */
function polarToCartesian(angleDeg) {
  const angleRad = ((angleDeg - 90) * Math.PI) / 180;
  return { x: CENTER + RADIUS * Math.cos(angleRad), y: CENTER + RADIUS * Math.sin(angleRad) };
}

/**
 * Builds the SVG path `d` attribute for a single pie slice spanning from
 * `startAngle` to `endAngle`, choosing the large-arc-flag as needed for
 * slices spanning more than 180 degrees.
 *
 * @param {number} startAngle - Slice start angle in degrees, clockwise from the top.
 * @param {number} endAngle - Slice end angle in degrees, clockwise from the top.
 * @returns {string} An SVG path `d` attribute describing the slice.
 */
function describeSlice(startAngle, endAngle) {
  const p1 = polarToCartesian(startAngle);
  const p2 = polarToCartesian(endAngle);
  const largeArcFlag = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${CENTER} ${CENTER} L ${p1.x} ${p1.y} A ${RADIUS} ${RADIUS} 0 ${largeArcFlag} 1 ${p2.x} ${p2.y} Z`;
}

/**
 * Renders a dependency-free SVG pie chart of spend by category, plus a
 * legend listing each category's amount and percentage share. Categories
 * with zero spend are excluded from the chart. Renders a single full circle
 * (rather than a one-slice arc, which SVG can't draw correctly) when only one
 * category has spend, and a "no spending" message when the month's total is
 * zero or negative.
 *
 * @param {Object} props
 * @param {Object} props.byCategory - Map of category name to spend amount for the month.
 */
export default function ExpensePieChart({ byCategory }) {
  const slices = CATEGORIES.map((category) => ({ category, amount: byCategory[category] || 0 })).filter(
    (slice) => slice.amount > 0
  );
  const total = slices.reduce((sum, slice) => sum + slice.amount, 0);

  if (total <= 0) {
    return <p className="pie-chart-empty">No spending to chart for this month.</p>;
  }

  const arcs = slices.reduce((acc, slice) => {
    const startAngle = acc.length ? acc[acc.length - 1].endAngle : 0;
    const endAngle = startAngle + (slice.amount / total) * 360;
    acc.push({ ...slice, startAngle, endAngle, percent: (slice.amount / total) * 100 });
    return acc;
  }, []);

  return (
    <div className="pie-chart">
      <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="pie-chart-svg" role="img" aria-label="Expense distribution by category">
        {arcs.length === 1 ? (
          <circle cx={CENTER} cy={CENTER} r={RADIUS} fill={CATEGORY_COLORS[arcs[0].category]} className="pie-slice">
            <title>{`${arcs[0].category}: ${formatCurrency(arcs[0].amount)} (100.0%)`}</title>
          </circle>
        ) : (
          arcs.map((arc) => (
            <path
              key={arc.category}
              d={describeSlice(arc.startAngle, arc.endAngle)}
              fill={CATEGORY_COLORS[arc.category]}
              className="pie-slice"
              tabIndex={0}
              role="img"
              aria-label={`${arc.category}: ${formatCurrency(arc.amount)}, ${arc.percent.toFixed(1)}% of total`}
            >
              <title>{`${arc.category}: ${formatCurrency(arc.amount)} (${arc.percent.toFixed(1)}%)`}</title>
            </path>
          ))
        )}
      </svg>
      <ul className="pie-chart-legend">
        {arcs.map((arc) => (
          <li key={arc.category}>
            <span className="pie-swatch" style={{ backgroundColor: CATEGORY_COLORS[arc.category] }} aria-hidden="true" />
            <span className="pie-legend-label">{arc.category}</span>
            <span className="pie-legend-value">{formatCurrency(arc.amount)}</span>
            <span className="pie-legend-percent">{arc.percent.toFixed(1)}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
