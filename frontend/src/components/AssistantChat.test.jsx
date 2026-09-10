import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AssistantChat from "./AssistantChat";
import * as api from "../api/client";

vi.mock("../api/client");

async function sendMessage(user, text) {
  await user.type(screen.getByLabelText("Message"), text);
  await user.click(screen.getByRole("button", { name: "Send" }));
}

beforeEach(() => {
  vi.resetAllMocks();
});

describe("AssistantChat", () => {
  it("shows the empty-state placeholder initially", () => {
    render(<AssistantChat onDataChanged={vi.fn()} />);

    expect(
      screen.getByText(/Ask me about your expenses, budgets, or spending/)
    ).toBeInTheDocument();
  });

  it("sends a message with an empty history on the first turn, and shows the reply", async () => {
    const user = userEvent.setup();
    api.sendAssistantMessage.mockResolvedValue({ reply: "You spent $10 on Food.", toolCalls: [] });
    const onDataChanged = vi.fn().mockResolvedValue();

    render(<AssistantChat onDataChanged={onDataChanged} />);

    await sendMessage(user, "How much did I spend on Food?");

    await waitFor(() =>
      expect(api.sendAssistantMessage).toHaveBeenCalledWith("How much did I spend on Food?", [])
    );

    expect(await screen.findByText(/How much did I spend on Food\?/)).toBeInTheDocument();
    expect(await screen.findByText(/You spent \$10 on Food\./)).toBeInTheDocument();
    await waitFor(() => expect(onDataChanged).toHaveBeenCalledTimes(1));
  });

  it("includes prior turns in history on a second message", async () => {
    const user = userEvent.setup();
    api.sendAssistantMessage
      .mockResolvedValueOnce({ reply: "You spent $10 on Food.", toolCalls: [] })
      .mockResolvedValueOnce({ reply: "You spent $5 on Transport.", toolCalls: [] });
    const onDataChanged = vi.fn().mockResolvedValue();

    render(<AssistantChat onDataChanged={onDataChanged} />);

    await sendMessage(user, "How much did I spend on Food?");
    await screen.findByText(/You spent \$10 on Food\./);

    await sendMessage(user, "What about Transport?");

    await waitFor(() =>
      expect(api.sendAssistantMessage).toHaveBeenNthCalledWith(2, "What about Transport?", [
        { role: "user", content: "How much did I spend on Food?" },
        { role: "assistant", content: "You spent $10 on Food." },
      ])
    );
  });

  it("shows an error and does not add a fake assistant message when the call fails", async () => {
    const user = userEvent.setup();
    api.sendAssistantMessage.mockRejectedValue(new Error("Request failed with status 500"));

    render(<AssistantChat onDataChanged={vi.fn()} />);

    await sendMessage(user, "Hello");

    expect(await screen.findByText("Request failed with status 500")).toBeInTheDocument();
    expect(screen.queryByText(/^Assistant:/)).not.toBeInTheDocument();
  });

  it("disables the send button and input while a request is in flight", async () => {
    const user = userEvent.setup();
    let resolveSend;
    api.sendAssistantMessage.mockReturnValue(
      new Promise((resolve) => {
        resolveSend = resolve;
      })
    );

    render(<AssistantChat onDataChanged={vi.fn().mockResolvedValue()} />);

    await user.type(screen.getByLabelText("Message"), "Hello");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
    expect(screen.getByLabelText("Message")).toBeDisabled();
    expect(screen.getByRole("status")).toHaveTextContent("Thinking…");

    resolveSend({ reply: "Hi there!", toolCalls: [] });
    await waitFor(() => expect(screen.getByLabelText("Message")).not.toBeDisabled());
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });
});
