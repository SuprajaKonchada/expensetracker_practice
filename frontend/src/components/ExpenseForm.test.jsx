import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ExpenseForm from "./ExpenseForm";

describe("ExpenseForm", () => {
  it("renders in add mode with an empty description by default", () => {
    render(<ExpenseForm editingExpense={null} error={null} onSubmit={vi.fn()} onCancel={vi.fn()} />);

    expect(screen.getByRole("heading", { name: "Add Expense" })).toBeInTheDocument();
    expect(screen.getByLabelText("Description")).toHaveValue("");
    expect(screen.getByLabelText("Recurrence")).toHaveValue("None");
    expect(screen.queryByText("Cancel")).not.toBeInTheDocument();
  });

  it("submits parsed form data", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ExpenseForm editingExpense={null} error={null} onSubmit={onSubmit} onCancel={vi.fn()} />);

    await user.type(screen.getByLabelText("Description"), "Coffee");
    await user.clear(screen.getByLabelText("Amount"));
    await user.type(screen.getByLabelText("Amount"), "4.50");
    await user.click(screen.getByRole("button", { name: "Add Expense" }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ description: "Coffee", amount: 4.5, category: "Food", recurrence: "None" })
    );
  });

  it("submits the selected recurrence value", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ExpenseForm editingExpense={null} error={null} onSubmit={onSubmit} onCancel={vi.fn()} />);

    await user.type(screen.getByLabelText("Description"), "Coffee");
    await user.clear(screen.getByLabelText("Amount"));
    await user.type(screen.getByLabelText("Amount"), "4.50");
    await user.selectOptions(screen.getByLabelText("Recurrence"), "Weekly");
    await user.click(screen.getByRole("button", { name: "Add Expense" }));

    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ recurrence: "Weekly" }));
  });

  it("prefills fields and shows Cancel when editing", () => {
    const expense = {
      id: "1",
      description: "Bus",
      amount: 2,
      date: "2026-01-02",
      category: "Transport",
      recurrence: "Monthly",
    };
    render(<ExpenseForm editingExpense={expense} error={null} onSubmit={vi.fn()} onCancel={vi.fn()} />);

    expect(screen.getByText("Edit Expense")).toBeInTheDocument();
    expect(screen.getByLabelText("Description")).toHaveValue("Bus");
    expect(screen.getByLabelText("Recurrence")).toHaveValue("Monthly");
    expect(screen.getByText("Cancel")).toBeInTheDocument();
  });

  it("defaults recurrence to None when editing an expense without one", () => {
    const expense = { id: "1", description: "Bus", amount: 2, date: "2026-01-02", category: "Transport" };
    render(<ExpenseForm editingExpense={expense} error={null} onSubmit={vi.fn()} onCancel={vi.fn()} />);

    expect(screen.getByLabelText("Recurrence")).toHaveValue("None");
  });

  it("calls onCancel when Cancel is clicked", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    const expense = { id: "1", description: "Bus", amount: 2, date: "2026-01-02", category: "Transport" };
    render(<ExpenseForm editingExpense={expense} error={null} onSubmit={vi.fn()} onCancel={onCancel} />);

    await user.click(screen.getByText("Cancel"));
    expect(onCancel).toHaveBeenCalled();
  });

  it("displays a validation error message", () => {
    render(<ExpenseForm editingExpense={null} error="Please enter a description." onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(screen.getByText("Please enter a description.")).toBeInTheDocument();
  });
});
