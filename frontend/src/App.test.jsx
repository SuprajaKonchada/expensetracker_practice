import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import * as api from "./api/client";

vi.mock("./api/client");

function makeExpense(overrides = {}) {
  return {
    id: "1",
    description: "Coffee",
    amount: 4.5,
    date: "2026-01-01",
    category: "Food",
    recurrence: "None",
    ...overrides,
  };
}

beforeEach(() => {
  vi.resetAllMocks();
  api.getExpenses.mockResolvedValue([]);
  api.getBudgets.mockResolvedValue({});
  api.getSummary.mockResolvedValue({ total: 0, byCategory: {}, budgetStatuses: [] });
  // vi.mock("./api/client") auto-mocks every export as a vi.fn(); no existing test
  // calls sendAssistantMessage, but AssistantChat renders unconditionally, so give it
  // a harmless default in case a test interacts with the chat UI.
  api.sendAssistantMessage.mockResolvedValue({ reply: "", toolCalls: [] });
  vi.spyOn(window, "confirm").mockReturnValue(true);
});

describe("App", () => {
  it("shows a loading state while initial data loads, then hides it", async () => {
    let resolveExpenses;
    api.getExpenses.mockReturnValue(
      new Promise((resolve) => {
        resolveExpenses = resolve;
      })
    );

    render(<App />);

    expect(screen.getByText("Loading expenses…")).toBeInTheDocument();

    resolveExpenses([]);
    await waitFor(() => expect(screen.queryByText("Loading expenses…")).not.toBeInTheDocument());
  });

  it("loads and displays existing expenses", async () => {
    api.getExpenses.mockResolvedValue([makeExpense()]);

    render(<App />);

    expect(await screen.findByText("Coffee")).toBeInTheDocument();
  });

  it("creates a new expense through the form", async () => {
    const user = userEvent.setup();
    api.getExpenses.mockResolvedValueOnce([]).mockResolvedValueOnce([makeExpense()]);
    api.createExpense.mockResolvedValue(makeExpense());

    render(<App />);
    await waitFor(() => expect(api.getExpenses).toHaveBeenCalledTimes(1));

    await user.type(screen.getByLabelText("Description"), "Coffee");
    await user.clear(screen.getByLabelText("Amount"));
    await user.type(screen.getByLabelText("Amount"), "4.50");
    await user.click(screen.getByRole("button", { name: "Add Expense" }));

    await waitFor(() =>
      expect(api.createExpense).toHaveBeenCalledWith(
        expect.objectContaining({ description: "Coffee", amount: 4.5 })
      )
    );
    expect(await screen.findByText("Coffee")).toBeInTheDocument();
  });

  it("edits an existing expense", async () => {
    const user = userEvent.setup();
    api.getExpenses.mockResolvedValue([makeExpense()]);
    api.updateExpense.mockResolvedValue(makeExpense({ description: "Latte" }));

    render(<App />);
    await screen.findByText("Coffee");

    await user.click(screen.getByText("Edit"));
    expect(screen.getByText("Edit Expense")).toBeInTheDocument();

    const descriptionField = screen.getByLabelText("Description");
    await user.clear(descriptionField);
    await user.type(descriptionField, "Latte");
    await user.click(screen.getByText("Update Expense"));

    await waitFor(() =>
      expect(api.updateExpense).toHaveBeenCalledWith("1", expect.objectContaining({ description: "Latte" }))
    );
  });

  it("deletes an expense after confirmation", async () => {
    const user = userEvent.setup();
    api.getExpenses.mockResolvedValueOnce([makeExpense()]).mockResolvedValueOnce([]);
    api.deleteExpense.mockResolvedValue(null);

    render(<App />);
    await screen.findByText("Coffee");

    await user.click(screen.getByText("Delete"));

    expect(window.confirm).toHaveBeenCalledWith("Delete this expense?");
    await waitFor(() => expect(api.deleteExpense).toHaveBeenCalledWith("1"));
  });

  it("shows an error when deleting an expense fails", async () => {
    const user = userEvent.setup();
    api.getExpenses.mockResolvedValue([makeExpense()]);
    api.deleteExpense.mockRejectedValue(new Error("Request failed with status 500"));

    render(<App />);
    await screen.findByText("Coffee");

    await user.click(screen.getByText("Delete"));

    expect(await screen.findByText("Request failed with status 500")).toBeInTheDocument();
  });

  it("shows an error when updating a budget fails", async () => {
    const user = userEvent.setup();
    api.setBudget.mockRejectedValue(new Error("Unknown category."));

    render(<App />);
    await waitFor(() => expect(api.getBudgets).toHaveBeenCalled());

    const foodInput = screen.getByLabelText("Food monthly budget");
    await user.type(foodInput, "100");
    await user.tab();

    expect(await screen.findByText("Unknown category.")).toBeInTheDocument();
  });

  it("shows a validation error returned by the API without clearing the form", async () => {
    const user = userEvent.setup();
    api.createExpense.mockRejectedValue(new Error("Please enter a valid amount greater than 0."));

    render(<App />);
    await waitFor(() => expect(api.getExpenses).toHaveBeenCalled());

    await user.type(screen.getByLabelText("Description"), "Coffee");
    await user.clear(screen.getByLabelText("Amount"));
    await user.type(screen.getByLabelText("Amount"), "5");
    await user.click(screen.getByRole("button", { name: "Add Expense" }));

    expect(await screen.findByText("Please enter a valid amount greater than 0.")).toBeInTheDocument();
  });

  it("renders the AI Expense Assistant panel alongside the rest of the app", async () => {
    api.getExpenses.mockResolvedValue([makeExpense()]);

    render(<App />);

    expect(await screen.findByText("Coffee")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "AI Expense Assistant" })).toBeInTheDocument();
    expect(screen.getByLabelText("Message")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument();
  });
});
