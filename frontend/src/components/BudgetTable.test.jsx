import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import BudgetTable from "./BudgetTable";
import { CATEGORIES } from "../constants";

describe("BudgetTable", () => {
  it("renders one row per category with the stored budget value", () => {
    render(<BudgetTable budgets={{ Food: 200 }} month="2026-01" onMonthChange={vi.fn()} onChange={vi.fn()} />);

    for (const category of CATEGORIES) {
      expect(screen.getByText(category)).toBeInTheDocument();
    }
    expect(screen.getByDisplayValue("200")).toBeInTheDocument();
  });

  it("calls onChange with the category and new value on blur", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<BudgetTable budgets={{}} month="2026-01" onMonthChange={vi.fn()} onChange={onChange} />);

    const foodInput = screen.getAllByPlaceholderText("No budget")[0];
    await user.type(foodInput, "150");
    await user.tab();

    expect(onChange).toHaveBeenCalledWith("Food", "150");
  });

  it("gives each budget input an accessible label tied to its category", () => {
    render(<BudgetTable budgets={{}} month="2026-01" onMonthChange={vi.fn()} onChange={vi.fn()} />);

    for (const category of CATEGORIES) {
      expect(screen.getByLabelText(`${category} monthly budget`)).toBeInTheDocument();
    }
  });

  it("shows the selected month and calls onMonthChange when it's changed", async () => {
    const user = userEvent.setup();
    const onMonthChange = vi.fn();
    render(<BudgetTable budgets={{}} month="2026-01" onMonthChange={onMonthChange} onChange={vi.fn()} />);

    const monthInput = screen.getByLabelText("Month");
    expect(monthInput).toHaveValue("2026-01");

    await user.type(monthInput, "2026-03");

    expect(onMonthChange).toHaveBeenCalled();
  });
});
