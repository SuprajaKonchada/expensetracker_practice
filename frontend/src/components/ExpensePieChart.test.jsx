import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ExpensePieChart from "./ExpensePieChart";

describe("ExpensePieChart", () => {
  it("shows an empty message when there is no spending", () => {
    render(<ExpensePieChart byCategory={{}} />);
    expect(screen.getByText("No spending to chart for this month.")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("ignores categories with zero or missing amounts", () => {
    render(<ExpensePieChart byCategory={{ Food: 50, Transport: 0 }} />);
    expect(screen.getByText("Food")).toBeInTheDocument();
    expect(screen.queryByText("Transport")).not.toBeInTheDocument();
  });

  it("renders a legend entry per category with amount and share of total", () => {
    render(<ExpensePieChart byCategory={{ Food: 75, Transport: 25 }} />);

    expect(screen.getByText("Food")).toBeInTheDocument();
    expect(screen.getByText("$75.00")).toBeInTheDocument();
    expect(screen.getByText("75.0%")).toBeInTheDocument();

    expect(screen.getByText("Transport")).toBeInTheDocument();
    expect(screen.getByText("$25.00")).toBeInTheDocument();
    expect(screen.getByText("25.0%")).toBeInTheDocument();
  });

  it("renders one slice per category with an accessible label", () => {
    render(<ExpensePieChart byCategory={{ Food: 75, Transport: 25 }} />);
    expect(screen.getByRole("img", { name: "Food: $75.00, 75.0% of total" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Transport: $25.00, 25.0% of total" })).toBeInTheDocument();
  });

  it("renders a full circle when only one category has spending", () => {
    const { container } = render(<ExpensePieChart byCategory={{ Food: 40 }} />);
    expect(container.querySelector("circle.pie-slice")).toBeInTheDocument();
    expect(container.querySelector("path.pie-slice")).not.toBeInTheDocument();
  });
});
