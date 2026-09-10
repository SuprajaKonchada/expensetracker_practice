"""Agentic loop: uses the Claude Agent SDK to autonomously call expense-tracker tools until
it produces a final natural-language answer.

Authentication: the SDK spawns the local `claude` CLI as a subprocess and reuses ITS existing
login session — no ANTHROPIC_API_KEY is read or required by this module (confirmed
empirically; not documented behavior, but verified working on this machine). This means the
assistant's cost/quota is billed against whatever Claude plan the `claude` CLI is logged into
wherever this backend runs — NOT free/local the way the project's earlier Ollama-based
attempt was. Every request here spends real money/quota shared with normal Claude Code usage.

A custom, minimal `system_prompt` is supplied deliberately: leaving it unset makes the SDK
fall back to the full default Claude Code system prompt (skills, subagents, slash commands,
etc.), which is irrelevant overhead for a narrow expense-tracking assistant and measurably
inflates cost/latency per request.

Each call to `run_agent` spawns a fresh `claude` CLI subprocess (the SDK does not reuse a
session/subprocess across separate calls), so prior conversation turns are folded into the
prompt text itself (`_render_prompt`) rather than passed as a structured message list.
"""
import asyncio
import json
import logging

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

import assistant_tools
import config
import constants

logger = logging.getLogger(__name__)

UNAVAILABLE_REPLY = "The assistant is temporarily unavailable. Please try again."

# Indirection so tests can monkeypatch the actual SDK call with a fake async generator
# without needing a real `claude` CLI subprocess (which would cost real money).
_query_fn = query


def _build_system_prompt():
    categories = ", ".join(constants.CATEGORIES)
    recurrence_options = ", ".join(constants.RECURRENCE_OPTIONS)
    return (
        "You are the AI Expense Assistant for a personal expense-tracking app. You help the "
        "user view, add, edit, and delete expenses, and check budgets and monthly summaries. "
        "You can also just chat normally (e.g. respond to a greeting) when the user isn't "
        "asking about their expenses. "
        "Use the provided tools to read or change real data instead of guessing values. "
        f"Valid expense categories are: {categories}. Valid recurrence values are: "
        f"{recurrence_options}. Dates are formatted \"YYYY-MM-DD\" and months are formatted "
        "\"YYYY-MM\". If a request is ambiguous or you're missing information needed for a "
        "destructive or data-changing action (creating, updating, or deleting an expense), "
        "ask the user to clarify in your final reply rather than guessing. "
        "A tool's result is the ONLY source of truth for whether an action succeeded. If a "
        "tool result contains an \"error\" field, the action FAILED — tell the user what went "
        "wrong and either retry with corrected arguments or ask them to clarify. Never tell "
        "the user an expense was added, updated, or deleted unless the tool result actually "
        "shows that outcome."
    )


def _render_prompt(message, history):
    """Fold prior turns (if any) into a single prompt string, since query() takes one prompt
    per call rather than a structured message list."""
    if not history:
        return message
    lines = [f"{'User' if turn['role'] == 'user' else 'Assistant'}: {turn['content']}" for turn in history]
    lines.append(f"User: {message}")
    lines.append("\nRespond to the latest user message above.")
    return "\n".join(lines)


def _build_tools(conn, tool_call_log):
    """Build the expense-tracker tools (as SdkMcpTool objects) bound to this request's `conn`.
    `tool_call_log` is appended to directly by each tool as it runs, since that's a more
    reliable way to capture exact args/results than re-parsing SDK message types afterward.
    Split out from `_build_tool_server` so tests can invoke `tool.handler(args)` directly
    without spinning up a real MCP server or model."""

    def _run_tool(name, args):
        result = assistant_tools.execute_tool(conn, name, args)
        tool_call_log.append({"tool": name, "args": args, "result": result})
        return {"content": [{"type": "text", "text": json.dumps(result)}], "is_error": "error" in result}

    @tool("list_expenses", "List expenses, optionally filtered by category and/or month.",
          {"category": str, "month": str})
    async def list_expenses(args):
        return _run_tool("list_expenses", args)

    @tool("create_expense", "Create a new expense.",
          {"description": str, "amount": float, "date": str, "category": str, "recurrence": str})
    async def create_expense(args):
        return _run_tool("create_expense", args)

    @tool("update_expense", "Update an existing expense by id (full replace — supply every field).",
          {"id": str, "description": str, "amount": float, "date": str, "category": str, "recurrence": str})
    async def update_expense(args):
        return _run_tool("update_expense", args)

    @tool("delete_expense", "Delete an expense by id.", {"id": str})
    async def delete_expense(args):
        return _run_tool("delete_expense", args)

    @tool("get_budgets", "Get the budgets set for a given month, as {category: amount}.", {"month": str})
    async def get_budgets(args):
        return _run_tool("get_budgets", args)

    @tool("get_monthly_summary", "Get a month's total spend, per-category breakdown, and budget statuses.",
          {"month": str})
    async def get_monthly_summary(args):
        return _run_tool("get_monthly_summary", args)

    return [list_expenses, create_expense, update_expense, delete_expense, get_budgets, get_monthly_summary]


def _build_options(conn, tool_call_log):
    server = create_sdk_mcp_server(name="expense_tracker", version="1.0.0", tools=_build_tools(conn, tool_call_log))
    tool_names = [
        f"mcp__expense_tracker__{name}"
        for name in ("list_expenses", "create_expense", "update_expense", "delete_expense",
                      "get_budgets", "get_monthly_summary")
    ]
    return ClaudeAgentOptions(
        model=config.CLAUDE_MODEL,
        system_prompt=_build_system_prompt(),
        mcp_servers={"expense_tracker": server},
        allowed_tools=tool_names,
        tools=[],  # strip all built-in tools (Read/Write/Bash/etc.) — only our MCP tools may run
        permission_mode="dontAsk",  # headless backend: no interactive prompts; deny anything not allow-listed
    )


async def _run(conn, message, history):
    tool_call_log = []
    options = _build_options(conn, tool_call_log)
    prompt = _render_prompt(message, history)

    reply = None
    async for msg in _query_fn(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock) and block.text:
                    reply = block.text
        elif isinstance(msg, ResultMessage):
            if msg.subtype == "success":
                reply = msg.result or reply
            else:
                logger.warning("Claude Agent SDK query ended with subtype=%s", msg.subtype)
                reply = reply or UNAVAILABLE_REPLY

    return {"reply": reply or UNAVAILABLE_REPLY, "toolCalls": tool_call_log}


def run_agent(conn, message, history=None):
    """Run one user turn through the Claude Agent SDK's agentic loop.

    Returns {"reply": str, "toolCalls": [{"tool": str, "args": dict, "result": dict}, ...]}.
    Never raises: any SDK/subprocess failure is caught and turned into a graceful reply so a
    chat request can never 500 the Flask app.
    """
    try:
        return asyncio.run(_run(conn, message, history or []))
    except Exception:
        logger.exception("Claude Agent SDK query failed")
        return {"reply": UNAVAILABLE_REPLY, "toolCalls": []}
