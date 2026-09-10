"""Blueprint: /api/assistant"""
from flask import Blueprint, current_app, jsonify, request

import assistant_agent

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")

# Client-supplied history is spliced directly into the LLM's message list (see
# assistant_agent.run_agent), so only these two roles are ever allowed through — never
# "system" or "tool", which a client must not be able to inject into the model's context.
_ALLOWED_HISTORY_ROLES = {"user", "assistant"}


def _get_conn():
    return current_app.config["GET_CONN"]()


def _sanitize_history(history):
    """Validate `history` is a list of {"role": "user"|"assistant", "content": str} entries
    and rebuild clean dicts containing only those two keys (dropping anything else a client
    might try to smuggle in, e.g. a fabricated "tool_calls" field). Returns None if invalid.
    """
    if not isinstance(history, list):
        return None
    clean = []
    for entry in history:
        if not isinstance(entry, dict):
            return None
        role = entry.get("role")
        content = entry.get("content")
        if role not in _ALLOWED_HISTORY_ROLES or not isinstance(content, str):
            return None
        clean.append({"role": role, "content": content})
    return clean


@assistant_bp.post("/chat")
def chat():
    """POST /api/assistant/chat: send a message to the AI expense assistant.

    Body: {"message": "...", "history": [...]} (history optional, defaults to []).
    400s if "message" is missing/not a string/blank, or if "history" isn't a list of
    {"role": "user"|"assistant", "content": str} entries. Returns {"reply": ..., "toolCalls": ...}.
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "A non-empty message is required."}), 400

    history = _sanitize_history(data.get("history") or [])
    if history is None:
        return jsonify({"error": "Invalid conversation history."}), 400

    conn = _get_conn()
    try:
        result = assistant_agent.run_agent(conn, message, history)
        return jsonify(result)
    finally:
        conn.close()
