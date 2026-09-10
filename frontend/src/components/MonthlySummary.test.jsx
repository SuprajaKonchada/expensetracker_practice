import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import MonthlySummary from "./MonthlySummary";

describe("MonthlySummary", () => {
  it("shows the empty message when there is nothing for the month", () => {
    render(
      <MonthlySummary
        month="2026-01"
        onMonthChange={vi.fn()}
        total={0}
        byCategory={{}}
        budgetStatuses={[]}
        budgets={{}}
      />
    );
    expect(screen.getByText("No expenses for this month.")).toBeInTheDocument();
  });

  it("flags an over-budget category", () => {
    render(
      <MonthlySummary
        month="2026-01"
        onMonthChange={vi.fn()}
        total={120}
        byCategory={{ Food: 120 }}
        budgetStatuses={[{ category: "Food", budget: 100, spent: 120, remaining: -20, exceeded: true }]}
        budgets={{ Food: 100 }}
      />
    );

    expect(screen.getByText("Over by $20.00")).toBeInTheDocument();
  });

  it("shows remaining budget for a category under budget", () => {
    render(
      <MonthlySummary
        month="2026-01"
        onMonthChange={vi.fn()}
        total={30}
        byCategory={{ Transport: 30 }}
        budgetStatuses={[{ category: "Transport", budget: 50, spent: 30, remaining: 20, exceeded: false }]}
        budgets={{ Transport: 50 }}
      />
    );

    expect(screen.getByText("$20.00 left")).toBeInTheDocument();
  });
});
