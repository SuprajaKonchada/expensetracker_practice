import { useState } from "react";
import * as api from "../api/client";

/**
 * Chat panel for the AI expense assistant. Owns its own message list and
 * input state locally (UI-local, not shared app state); after each
 * successful assistant reply it calls `onDataChanged` so the parent can
 * refresh expenses/budgets/summary, since the assistant may have
 * autonomously created/updated/deleted expenses.
 *
 * @param {Object} props
 * @param {() => Promise<void>} props.onDataChanged - Called (and awaited) after each successful assistant reply.
 */
export default function AssistantChat({ onDataChanged }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isSending) return;

    const history = messages.map(({ role, content }) => ({ role, content }));
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setError(null);
    setIsSending(true);
    try {
      const { reply } = await api.sendAssistantMessage(trimmed, history);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
      try {
        await onDataChanged();
      } catch (err) {
        setError(err.message);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <section className="assistant-section">
      <h2>AI Expense Assistant</h2>

      <div className="chat-messages" id="chat-messages">
        {messages.length === 0 && (
          <p className="chat-empty-state">
            Ask me about your expenses, budgets, or spending — e.g. &quot;How much did I spend on Food this
            month?&quot;
          </p>
        )}
        {messages.map((message, index) => (
          <div key={index} className={`chat-message chat-message-${message.role}`}>
            <strong>{message.role === "user" ? "You:" : "Assistant:"}</strong> {message.content}
          </div>
        ))}
      </div>

      {isSending && (
        <p role="status" className="chat-status">
          Thinking…
        </p>
      )}

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      <form id="assistant-form" onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          id="assistant-input"
          aria-label="Message"
          placeholder="Ask about your expenses…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isSending}
        />
        <button type="submit" id="assistant-send-btn" disabled={isSending || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}
