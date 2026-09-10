import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ExpenseTable from "./ExpenseTable";

const expenses = [
  { id: "1", description: "Coffee", amount: 4.5, date: "2026-01-01", category: "Food", recurrence: "Weekly" },
  { id: "2", description: "Bus", amount: 2, date: "2026-01-02", category: "Transport" },
];

describe("ExpenseTable", () => {
  it("renders a row per expense with formatted amounts", () => {
    render(<ExpenseTable expenses={expenses} onEdit={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByText("Coffee")).toBeInTheDocument();
    expect(screen.getByText("$4.50")).toBeInTheDocument();
    expect(screen.getByText("Bus")).toBeInTheDocument();
    expect(screen.queryByText("No expenses yet. Add one above to get started.")).not.toBeInTheDocument();
  });

  it("renders the recurrence value, defaulting to None when missing", () => {
    render(<ExpenseTable expenses={expenses} onEdit={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByText("Weekly")).toBeInTheDocument();
    // The second expense has no recurrence field and should render "None", not "undefined".
    const rows = screen.getAllByRole("row").slice(1);
    expect(rows[1]).toHaveTextContent("None");
  });

  it("shows the empty state when there are no expenses", () => {
    render(<ExpenseTable expenses={[]} onEdit={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByText("No expenses yet. Add one above to get started.")).toBeInTheDocument();
  });

  it("calls onEdit with the clicked expense", async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();
    render(<ExpenseTable expenses={expenses} onEdit={onEdit} onDelete={vi.fn()} />);

    await user.click(screen.getAllByText("Edit")[0]);
    expect(onEdit).toHaveBeenCalledWith(expenses[0]);
  });

  it("calls onDelete with the clicked expense id", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    render(<ExpenseTable expenses={expenses} onEdit={vi.fn()} onDelete={onDelete} />);

    await user.click(screen.getAllByText("Delete")[1]);
    expect(onDelete).toHaveBeenCalledWith("2");
  });
});
