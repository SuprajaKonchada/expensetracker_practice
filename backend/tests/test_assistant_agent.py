"""Tests for the Claude Agent SDK-based agentic loop.

No test in this file makes a real `claude` CLI call (that would cost real money and require
network/auth) — `_query_fn` is monkeypatched with a fake async generator throughout. Tool
execution is tested separately at the `_build_tools` level (calling `tool.handler(args)`
directly), since real tool invocation only happens via the SDK's own internal MCP dispatch,
which a mocked `_query_fn` never actually triggers.
"""
import asyncio
import json

import assistant_agent
from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock


def make_fake_query(messages):
    """Return a fake replacement for `_query_fn` that yields `messages` in order, ignoring
    the real prompt/options it's called with."""

    async def fake(prompt, options):
        for message in messages:
            yield message

    return fake


def result_message(subtype="success", result=None):
    return ResultMessage(
        subtype=subtype,
        duration_ms=1,
        duration_api_ms=1,
        is_error=(subtype != "success"),
        num_turns=1,
        session_id="test-session",
        result=result,
    )


def assistant_message(text):
    return AssistantMessage(content=[TextBlock(text=text)], model="claude-opus-5")


def test_immediate_final_reply_with_no_tool_calls(conn, monkeypatch):
    monkeypatch.setattr(
        assistant_agent,
        "_query_fn",
        make_fake_query([assistant_message("Hi there!"), result_message(result="Hi there!")]),
    )

    result = assistant_agent.run_agent(conn, "hello")

    assert result["reply"] == "Hi there!"
    assert result["toolCalls"] == []


def test_result_message_is_the_authoritative_final_reply(conn, monkeypatch):
    """ResultMessage.result should win even if an earlier AssistantMessage text differs
    (e.g. an intermediate "let me check that" before the real final answer)."""
    monkeypatch.setattr(
        assistant_agent,
        "_query_fn",
        make_fake_query([assistant_message("Let me check..."), result_message(result="Here's your answer.")]),
    )

    result = assistant_agent.run_agent(conn, "how much did I spend?")

    assert result["reply"] == "Here's your answer."


def test_non_success_result_subtype_returns_graceful_reply(conn, monkeypatch):
    monkeypatch.setattr(
        assistant_agent,
        "_query_fn",
        make_fake_query([result_message(subtype="error_max_turns", result=None)]),
    )

    result = assistant_agent.run_agent(conn, "do something complicated")

    assert result["reply"] == assistant_agent.UNAVAILABLE_REPLY


def test_query_exception_returns_graceful_reply_never_raises(conn, monkeypatch):
    async def boom(prompt, options):
        raise RuntimeError("subprocess failed to start")
        yield  # pragma: no cover - makes this an async generator

    monkeypatch.setattr(assistant_agent, "_query_fn", boom)

    result = assistant_agent.run_agent(conn, "hello")

    assert result["reply"] == assistant_agent.UNAVAILABLE_REPLY
    assert result["toolCalls"] == []


def test_render_prompt_with_no_history_is_just_the_message():
    assert assistant_agent._render_prompt("hello", []) == "hello"
    assert assistant_agent._render_prompt("hello", None) == "hello"


def test_render_prompt_folds_history_into_text():
    history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello!"}]

    prompt = assistant_agent._render_prompt("how much did I spend?", history)

    assert "User: hi" in prompt
    assert "Assistant: hello!" in prompt
    assert "User: how much did I spend?" in prompt


def test_system_prompt_forbids_claiming_success_without_tool_confirmation():
    """Regression guard for a hallucination observed with a prior model backend: it once
    claimed an expense was added after its create_expense tool call actually failed."""
    prompt = assistant_agent._build_system_prompt()
    assert "ONLY source of truth" in prompt
    assert "error" in prompt.lower()


def test_build_options_strips_built_in_tools_and_locks_to_expense_tools(conn):
    options = assistant_agent._build_options(conn, [])

    assert options.tools == []
    assert options.permission_mode == "dontAsk"
    assert set(options.allowed_tools) == {
        "mcp__expense_tracker__list_expenses",
        "mcp__expense_tracker__create_expense",
        "mcp__expense_tracker__update_expense",
        "mcp__expense_tracker__delete_expense",
        "mcp__expense_tracker__get_budgets",
        "mcp__expense_tracker__get_monthly_summary",
    }


# --- Tool-closure tests: exercise the real assistant_tools wiring by calling each tool's
# handler directly, without going through a real model or MCP server. ---


def _tool_by_name(tools, name):
    return next(t for t in tools if t.name == name)


def _call_tool(tools, name, args):
    """Synchronously invoke an async tool handler (avoids a pytest-asyncio dependency)."""
    return asyncio.run(_tool_by_name(tools, name).handler(args))


def test_list_expenses_tool_logs_call_and_returns_content(conn):
    log = []
    tools = assistant_agent._build_tools(conn, log)

    output = _call_tool(tools, "list_expenses", {})

    assert output["is_error"] is False
    assert json.loads(output["content"][0]["text"]) == {"expenses": []}
    assert log == [{"tool": "list_expenses", "args": {}, "result": {"expenses": []}}]


def test_create_expense_tool_persists_and_logs(conn):
    log = []
    tools = assistant_agent._build_tools(conn, log)
    args = {"description": "Coffee", "amount": 4.5, "date": "2026-01-01", "category": "Food"}

    output = _call_tool(tools, "create_expense", args)

    body = json.loads(output["content"][0]["text"])
    assert output["is_error"] is False
    assert body["description"] == "Coffee"
    assert log[0]["tool"] == "create_expense"

    listed = _call_tool(assistant_agent._build_tools(conn, []), "list_expenses", {})
    assert len(json.loads(listed["content"][0]["text"])["expenses"]) == 1


def test_create_expense_tool_reports_validation_error_without_crashing(conn):
    log = []
    tools = assistant_agent._build_tools(conn, log)
    args = {"description": "Bad", "amount": -5, "date": "2026-01-01", "category": "Food"}

    output = _call_tool(tools, "create_expense", args)

    assert output["is_error"] is True
    assert "error" in json.loads(output["content"][0]["text"])


def test_delete_expense_tool(conn):
    tools = assistant_agent._build_tools(conn, [])
    created = _call_tool(
        tools, "create_expense", {"description": "Coffee", "amount": 4.5, "date": "2026-01-01", "category": "Food"}
    )
    expense_id = json.loads(created["content"][0]["text"])["id"]

    output = _call_tool(tools, "delete_expense", {"id": expense_id})

    assert json.loads(output["content"][0]["text"]) == {"deleted": True, "id": expense_id}


def test_get_budgets_tool_reports_invalid_month(conn):
    tools = assistant_agent._build_tools(conn, [])

    output = _call_tool(tools, "get_budgets", {"month": "not-a-month"})

    assert output["is_error"] is True
